angular.module('FrontModule.controllers').controller('ManagePageCtrl', function($scope, API, $window, UtilsService) {
	
    var inputCity = document.getElementById('city_input');
    var options = { types: ['(cities)'], };
	
    var autocomplete = new google.maps.places.Autocomplete(inputCity, options);
        
    autocomplete.addListener('place_changed', function() {
    	
		$scope.mosaic.newcity_name = '';
		$scope.mosaic.newregion_name = '';
		$scope.mosaic.newcountry_name = '';
    	
    	var place = autocomplete.getPlace();
    	for (var i = 0; i < place.address_components.length; i++) {
    		
    		var addressType = place.address_components[i].types[0];
    		if (addressType == 'country') $scope.mosaic.newcountry_name = place.address_components[i]['long_name'];
    		if (addressType == 'locality') $scope.mosaic.newcity_name = place.address_components[i]['long_name'];
    		if (addressType == 'administrative_area_level_1') $scope.mosaic.newregion_name = place.address_components[i]['long_name'];
    		if (addressType == 'administrative_area_level_2' && !$scope.mosaic.newregion_name) $scope.mosaic.newregion_name = place.address_components[i]['long_name'];
     		if (addressType == 'administrative_area_level_3' && !$scope.mosaic.newcity_name) $scope.mosaic.newcity_name = place.address_components[i]['long_name'];
   		}

		if ($scope.mosaic.newregion_name == '' || !$scope.mosaic.newregion_name) {
			
			$scope.mosaic.newregion_name = $scope.mosaic.newcity_name;
		}
		
		$scope.$apply();
	});
	
	/* Mosaic management */
	
	$scope.rename = function(newname) {
		
		if (!newname || newname.legnth < 3) return; 
		
		$scope.updating = true;
		
		var data = { 'ref':$scope.mosaic.ref, 'newname':newname }
		API.sendRequest('/api/mosaic/rename/', 'POST', {}, data).then(function(response) {
			
			$scope.mosaic.title = newname;
			
			$scope.updating = false;
		});
	}
	
	$scope.move = function() {
		
		if (!$scope.mosaic.newcountry_name || !$scope.mosaic.newregion_name || !$scope.mosaic.newcity_name) return; 
		
		$scope.updating = true;
		
		var data = { 'ref':$scope.mosaic.ref, 'newcountry_name':$scope.mosaic.newcountry_name, 'newregion_name':$scope.mosaic.newregion_name, 'newcity_name':$scope.mosaic.newcity_name }
		API.sendRequest('/api/mosaic/move/', 'POST', {}, data).then(function(response) {
			
			$scope.mosaic.country_name = $scope.mosaic.newcountry_name;
			$scope.mosaic.region_name = $scope.mosaic.newregion_name;
			$scope.mosaic.city_name = $scope.mosaic.newcity_name;
			
			$scope.updating = false;
		});
	}
	
	$scope.delete = function() {
		
		$scope.updating = true;
		
		var data = { 'ref':$scope.mosaic.ref }
		API.sendRequest('/api/mosaic/delete/', 'POST', {}, data).then(function(response) {
			
			$window.location.href = '/';
		});
	}
	
	$scope.ownermsg = function(newtext) {
		
		$scope.updating = true;
		
		var data = { 'ref':$scope.mosaic.ref, 'text':newtext }
		API.sendRequest('/api/mosaic/ownermsg/', 'POST', {}, data).then(function(response) {
			
			$scope.mosaic.owner_msg = newtext;
			
			$scope.updating = false;
		});
	}
	
	/* Mission management */
	
	$scope.orderChange = function() {
		
		$scope.missions.sort(function(a, b) {
			
			if (parseInt(a.neworder) < parseInt(b.neworder))
				return -1;
				
			if (parseInt(a.neworder) > parseInt(b.neworder))
				return 1;
			
			return 0;
		});
	}
	
	$scope.search = function(text) {
		
		$scope.search_results = null;
		
		if (!text || text.length < 3) {
			return;
		}

		$scope.searching = true;
		
		var data = { 'text':text };
		API.sendRequest('/api/search/missions/', 'POST', {}, data).then(function(response) {
			
			$scope.search_results = response.missions;
			if (!$scope.search_results) $scope.search_results = [];
			
			$scope.searching = false;
		});
	}
	
	var missions_to_remove = [];
	var missions_to_reorder = [];
	
	function processMissionRemoving() {
	
		if (missions_to_remove.length < 1) {
			
			var data = { 'ref':$scope.mosaic.ref }
			API.sendRequest('/api/mosaic/compute/', 'POST', {}, data).then(function(response) {
				API.sendRequest('/api/mosaic/preview/generate/', 'POST', {}, data).then(function(response) {
					
					$scope.updating = false;
				});
			});
			
			return;
		}
		
		API.sendRequest('/api/mosaic/removemission/', 'POST', {}, missions_to_remove[0]).then(function(response) {
			
			missions_to_remove.splice(0, 1);
			processMissionRemoving();
		});
	}
	
	function processMissionReordering() {
	
		if (missions_to_reorder.length < 1) {
			
			processMissionRemoving();
			return;
		}
		
		API.sendRequest('/api/mosaic/reorder/', 'POST', {}, missions_to_reorder[0]).then(function(response) {
			
			missions_to_reorder.splice(0, 1);
			processMissionReordering();
		});
	}
	
	$scope.reorder = function() {
		
		$scope.updating = true;
		
		missions_to_remove = [];
		missions_to_reorder = [];
		
		for (var mission of $scope.missions) {
			
			if (mission.order != mission.neworder) {
				missions_to_reorder.push({ 'ref':$scope.mosaic.ref, 'mission_id':mission.id, 'neworder':mission.neworder });
			}
			
			if (mission.toremove) {
				missions_to_remove.push({ 'ref':$scope.mosaic.ref, 'mission_id':mission.id });
			}
		}
		
		processMissionReordering();
	}
	
	$scope.missions_to_add = [];
	
	$scope.add_mission = function(mission) {
		
		var mission_data = {
			
			'mission_id':mission.id,
			'ref':$scope.mosaic.ref,
			'title':mission.title,
			'order':UtilsService.getOrderFromMissionName(mission.title),
			'neworder':UtilsService.getOrderFromMissionName(mission.title),
		}
		
		$scope.missions_to_add.push(mission_data);
		
		var index = $scope.search_results.indexOf(mission);
		$scope.search_results.splice(index, 1);
	}
	
	$scope.detect_order = function(mission) {
		mission.neworder = UtilsService.getOrderFromMissionName(mission.title);
	}
	
	$scope.remove_mission = function(mission) {
		
		var index = 0;
		for (var mission_data of $scope.missions_to_add) {
			
			if (mission_data.mission_id == mission.mission_id) {
				break;
			}
			
			index += 1;
		}
		
		$scope.missions_to_add.splice(index, 1);
		
		$scope.search_results.push(mission);
	}
	
	function processMissionAdding() {
	
		if ($scope.missions_to_add.length < 1) {
			
			$scope.orderChange();
			
			var data = { 'ref':$scope.mosaic.ref }
			API.sendRequest('/api/mosaic/compute/', 'POST', {}, data).then(function(response) {
				API.sendRequest('/api/mosaic/preview/generate/', 'POST', {}, data).then(function(response) {
					
					$scope.updating = false;
				});
			});
			
			return;
		}
		
		API.sendRequest('/api/mosaic/addmission/', 'POST', {}, $scope.missions_to_add[0]).then(function(response) {
			
			$scope.missions.push($scope.missions_to_add[0]);
			
			$scope.missions_to_add.splice(0, 1);
			processMissionAdding();
		});
	}
	
	$scope.addmissions = function() {
		
		$scope.updating = true;
		
		processMissionAdding();
	}
	
	/* Tab management */
	
	$scope.current_tab = 'details';
	
	/* Page loading */
	
	$scope.init = function(mosaic, missions) {

		$scope.mosaic = mosaic;
		$scope.missions = missions;
		
		$scope.loaded = true;
	}
});