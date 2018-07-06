angular.module('FrontModule.controllers').controller('WaitingPageCtrl', function($scope, $auth, API, UtilsService) {
 
	$scope.authenticated = $auth.isAuthenticated();
   
    var inputCity = document.getElementById('city_input');
    var options = { types: ['(cities)'], };
	
    var autocomplete = new google.maps.places.Autocomplete(inputCity, options);
        
    autocomplete.addListener('place_changed', function() {
    	
    	var place = autocomplete.getPlace();
    	for (var i = 0; i < place.address_components.length; i++) {
    		
    		var addressType = place.address_components[i].types[0];
    		if (addressType == 'country') $scope.waiting.country_name = place.address_components[i]['long_name'];
    		if (addressType == 'locality') $scope.waiting.city_name = place.address_components[i]['long_name'];
    		if (addressType == 'administrative_area_level_1') $scope.waiting.region_name = place.address_components[i]['long_name'];
    		if (addressType == 'administrative_area_level_2' && !$scope.waiting.region_name) $scope.waiting.region_name = place.address_components[i]['long_name'];
     		if (addressType == 'administrative_area_level_3' && !$scope.waiting.city_name) $scope.waiting.city_name = place.address_components[i]['long_name'];
   		}

		if ($scope.waiting.region_name == '' || !$scope.waiting.region_name) {
			$scope.waiting.region_name = $scope.waiting.city_name;
		}
		
		$scope.$apply();
	});
	
	/* Waiting management */
	
	$scope.getImage = function(index) {
		for (var mission of $scope.missions) {
			if (mission.order == index) {
				return mission.image;
			}
		}
		return null;
	}
	
	$scope.detect_order = function(mission) {
		mission.order = UtilsService.getOrderFromMissionName(mission.title);
	}
	
	$scope.detect_order_all = function() {
		for (var mission of $scope.missions) {
			mission.order = UtilsService.getOrderFromMissionName(mission.title);
		}
	}
	
	$scope.reorderAsc = function() {
		
		var index = 0;
		for (var m of $scope.missions) {
			
			index += 1;
			m.order = index;
		}
		
		$scope.missions.sort(UtilsService.sortMissionsByOrderTitleAsc);
	}
	
	$scope.reorder = function() {
		
		for (var mission of $scope.missions) {
			API.sendRequest('/api/mission/reorder/', 'POST', {}, mission);
		}
		
		$scope.missions.sort(function(a, b) {
			
			if (parseInt(a.order) < parseInt(b.order))
				return -1;
				
			if (parseInt(a.order) > parseInt(b.order))
				return 1;
			
			return 0;
		});
		
		$scope.current_tab = 'details';
		window.scrollTo(0, 0);
	}
	
	$scope.update = function() {

		$scope.updating = true;
		
		var data = { 'ref':$scope.waiting.ref, 'title':$scope.waiting.title, 'country_name':$scope.waiting.country_name, 'region_name':$scope.waiting.region_name, 'city_name':$scope.waiting.city_name, 'mission_count':$scope.waiting.mission_count, }
		API.sendRequest('/api/waiting/update/', 'POST', {}, data).then(function(response) {

			$scope.updating = false;
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
	
	$scope.missions_to_add = [];
	
	$scope.add_mission = function(mission) {
		
		var mission_data = {
			
			'mission_id':mission.id,
			'ref':$scope.waiting.ref,
			'order':UtilsService.getOrderFromMissionName(mission.title),
		}
		
		$scope.missions_to_add.push(mission_data);
		
		var index = $scope.search_results.indexOf(mission);
		$scope.search_results.splice(index, 1);
	}
	
	function processMissionAdding() {
	
		if ($scope.missions_to_add.length < 1) {
			
			$scope.updating = false;
			return;
		}
		
		API.sendRequest('/api/waiting/addmission/', 'POST', {}, $scope.missions_to_add[0]).then(function(response) {
			
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
    
	/* Page init */
	
	$scope.init = function(waiting, missions, creators) {

		$scope.waiting = waiting;
		$scope.creators = creators;
		$scope.missions = missions;
		
		$scope.range = [];
	    for (var i = 0; i < $scope.waiting.mission_count; i++) {
	    	$scope.range.push(i);
	    }

		$scope.missions.sort(function(a, b) {
			
			if (parseInt(a.order) < parseInt(b.order))
				return -1;
				
			if (parseInt(a.order) > parseInt(b.order))
				return 1;
			
			return 0;
		});
		
		$scope.loaded = true;
	}
});
