angular.module('FrontModule.controllers').controller('NewRegistrationCtrl', function($scope, $window, toastr, API, UtilsService) {
	
	/* Tab management */
	
	$scope.current_step = 0;
	
	$scope.open_step = function(id) {
		
		$scope.current_step = id;
		
		if ($scope.current_step == 3) {
			
			if (!$scope.mosaic_name) $scope.computeMosaicName();
		}
	}
	
	/* Step #1 management */
	
	$scope.missions = null;
	$scope.selected = [];
	
	$scope.refreshing = false;
	
	$scope.searchText = '';
	$scope.requestText = '';
	
	$scope.refreshMissions = function(text) {
		
		$scope.missions = null;
		
		if (!text) return;
		
		if (text.length < 3) return;
		
		$scope.searchText = text;
		
		$scope.refreshing = true;
		
		var data = { 'text':text };
		API.sendRequest('/api/new_missions/', 'POST', {}, data).then(function(response) {
			
			$scope.missions = response.missions;
			if (!$scope.missions) $scope.missions = [];

			$scope.missions.sort(UtilsService.sortMissionsByCreatorTitleAsc);
			
			for (var mission of $scope.missions) {
				for (var select of $scope.selected) {
					if (mission.ref == select.ref) {
						mission.selected = true;
						break;
					}
				}
			}

			$scope.refreshing = false;
		});
	}

	$scope.toggleSelectMission = function(mission) {
	
		mission.selected = !mission.selected;
		
		if (mission.selected) {
			
			$scope.selected.push(mission);
			
			var order = UtilsService.getOrderFromMissionName(mission.title);
			if (order < 1) order = $scope.selected.indexOf(mission) + 1;
			mission.order = order.toString();
			
			$scope.selected.sort(UtilsService.sortMissionsByOrderTitleAsc);
			
			$scope.computeOffset();
		}
		else {
			
			var index = $scope.selected.indexOf(mission);
			$scope.selected.splice(index, 1);
			
			$scope.computeOffset();
		}
	}
	
	$scope.selectAll = function() {
		
		for (var mission of $scope.missions) {
			if (!mission.selected) {
				$scope.toggleSelectMission(mission);
			}
		}
	}
	
	$scope.sendRequest = function() {
		
		if (!$scope.requestText) return;
		
		if ($scope.requestText.length < 3) return;
		
		var data = { 'text':$scope.requestText };
		API.sendRequest('/api/new_missions/', 'POST', {}, data).then(function(response) {

			$scope.requestText = '';
			
			toastr.success('Request sent!');
		});
	}
	
	/* Step #2 management */
	
	$scope.columns = '6';
	
	$scope.offset = [];
	
	$scope.mission_selected = null;

	$scope.addFake = function(fakeorder) {
		
		var mission = {
			'ref': 'Unavailable',
			'order': fakeorder,
			'title': 'Fake mission',
		}
		
		$scope.selected.push(mission);
		
		$scope.selected.sort(UtilsService.sortMissionsByOrderTitleAsc);
		
		$scope.computeOffset();
	}
	
	$scope.computeOffset = function() {
		
		var temp = 0;
		if ($scope.selected.length > $scope.columns) {
			temp = $scope.columns - $scope.selected.length % $scope.columns;
			if (temp < 0 || temp > ($scope.columns - 1)) temp = 0;
		}
		
		$scope.offset = new Array(temp);
	}
	
	$scope.displayOrder = function(mission) {
		
		$scope.mission_selected = mission;
	}

	$scope.closeOrder = function() {
		
		$scope.mission_selected = null;
	}
	
	$scope.saveOrder = function(order) {
		
		if (!order) return;
		
		$scope.mission_selected.order = order;
		$scope.selected.sort(UtilsService.sortMissionsByOrderTitleAsc);
		
		$scope.closeOrder();
	}
	
	$scope.retireMission = function(mission) {
		
		var index = $scope.selected.indexOf(mission);
		$scope.selected.splice(index, 1);
		
		$scope.computeOffset();
			
		$scope.closeOrder();
	}
	
	$scope.reorderAsc = function() {
		
		var index = 0;
		for (var m of $scope.selected) {
			
			index += 1;
			m.order = index;
		}
		
		$scope.selected.sort(UtilsService.sortMissionsByOrderTitleAsc);
	}
	
	$scope.reorderDesc = function() {
		
		var index = $scope.selected.length + 1;
		for (var m of $scope.selected) {
			
			index -= 1;
			m.order = index;
		}
		
		$scope.selected.sort(UtilsService.sortMissionsByOrderTitleAsc);
	}
	
	$scope.reorderAlphaMosaic = function() {
		
		$scope.selected.sort(UtilsService.sortMissionsByTitleAsc);
		
		var index = 0;
		for (var m of $scope.selected) {
			
			index += 1;
			m.order = index;
		}
		
		$scope.selected.sort(UtilsService.sortMissionsByOrderTitleAsc);
	}
	
	$scope.reorderByEnd = function() {
		
		var last = $scope.selected[$scope.selected.length - 1];
		var start = last.order;
		
		var index = 0;
		for (var m of $scope.selected) {
			
			index += 1;
			m.order = start - $scope.selected.length + index;
		}
		
		$scope.selected.sort(UtilsService.sortMissionsByOrderTitleAsc);
	}
	
	$scope.sortMissionsByOrderTitleAsc = function() {
		
		$scope.selected.sort(UtilsService.sortMissionsByOrderTitleAsc);
	}
	
	/* Step #3 management */
	
	$scope.mosaic_name = '';
	$scope.mosaic_type = 'sequence';
	
	$scope.city_name = '';
	$scope.region_name = '';
	$scope.country_name = '';
	
    var inputCity = document.getElementById('city_input');
    var options = {
		types: ['(cities)'],
	};
	
    var autocomplete = new google.maps.places.Autocomplete(inputCity, options);
        
    autocomplete.addListener('place_changed', function() {
    	
		$scope.city_name = '';
		$scope.region_name = '';
		$scope.country_name = '';
    	
    	var place = autocomplete.getPlace();
    	for (var i = 0; i < place.address_components.length; i++) {
    		
    		var addressType = place.address_components[i].types[0];
    		if (addressType == 'country') $scope.country_name = place.address_components[i]['long_name'];
    		if (addressType == 'locality') $scope.city_name = place.address_components[i]['long_name'];
    		if (addressType == 'administrative_area_level_1') $scope.region_name = place.address_components[i]['long_name'];
    		if (addressType == 'administrative_area_level_2' && !$scope.region_name) $scope.region_name = place.address_components[i]['long_name'];
     		if (addressType == 'administrative_area_level_3' && !$scope.city_name) $scope.city_name = place.address_components[i]['long_name'];
   	}
    	
    	console.log(place.address_components);
    	
     	console.log($scope.country_name);
    	console.log($scope.region_name);
    	console.log($scope.city_name);
		
		$('#name_input').blur();
		
		$scope.apply();
	});
    
	$scope.computeMosaicName = function() {
		
		$scope.mosaic_name = '';
		
		var mosaic_name = $scope.selected[0].title;
		mosaic_name = mosaic_name.replace(/0|1|2|3|4|5|6|7|8|9|#/g, '');
		mosaic_name = mosaic_name.replace(/０|１|２|３|４|５|６|７|８|９/g, '');
		mosaic_name = mosaic_name.replace(/①|②|③|④|⑤|⑥/g, '');
		mosaic_name = mosaic_name.replace('.', '');
		mosaic_name = mosaic_name.replace('(', '');
		mosaic_name = mosaic_name.replace(')', '');
		mosaic_name = mosaic_name.replace('（', '');
		mosaic_name = mosaic_name.replace('）', '');
		mosaic_name = mosaic_name.replace('/', '');
		mosaic_name = mosaic_name.replace('[', '');
		mosaic_name = mosaic_name.replace(']', '');
		mosaic_name = mosaic_name.replace('【', '');
		mosaic_name = mosaic_name.replace('】', '');
		mosaic_name = mosaic_name.replace('-', '');
		mosaic_name = mosaic_name.replace('-', '');
		mosaic_name = mosaic_name.replace('－', '');
		mosaic_name = mosaic_name.replace('_', '');
		mosaic_name = mosaic_name.replace(':', '');
		mosaic_name = mosaic_name.replace('of ', '');
		mosaic_name = mosaic_name.replace(' of', '');
		mosaic_name = mosaic_name.replace('part ', '');
		mosaic_name = mosaic_name.replace(' part', '');
		mosaic_name = mosaic_name.replace('Part ', '');
		mosaic_name = mosaic_name.replace(' Part', '');
		mosaic_name = mosaic_name.replace('  ', ' ');
		mosaic_name = mosaic_name.replace('  ', ' ');
		mosaic_name = mosaic_name.replace('　', ' ');
		mosaic_name = mosaic_name.trim();
		
		$scope.mosaic_name = mosaic_name;
	}

	/* Step #4 management */
	
	$scope.creating = false;
	
	$scope.createMosaic = function() {
		
		$scope.creating = true;
		
		var data = {
			'country': $scope.country_name,
			'region': $scope.region_name,
			'city': $scope.city_name,
			'columns': $scope.columns,
			'type': $scope.mosaic_type,
			'title': $scope.mosaic_name,
			'missions': $scope.selected,
		};
		
		API.sendRequest('/api/mosaic/create/', 'POST', {}, data).then(function(response) {

			for (var mission of $scope.selected) {
				
				var index = -1;
				for (var test of $scope.missions) {
					
					index += 1;
					if (test.ref == mission.ref) break;
				}
				
				if (index != -1) $scope.missions.splice(index, 1);
			}
			
			if ($scope.missions.length < 1) $scope.missions = null;
			
			$scope.selected = [];
			
			$scope.columns = '6';
			
			$scope.offset = [];
			
			$scope.mission_selected = null;
			
			$scope.mosaic_name = '';
			$scope.mosaic_type = 'sequence';
			
			$scope.city_name = '';
			$scope.region_name = '';
			$scope.country_name = '';
		
			$window.open('https://www.myingressmosaics.com/mosaic/' + response);
			
			$scope.open_step(1);
			
			$scope.creating = false;
		});
	}
	
	/* Page loading */

	$scope.init = function(text) {
	
		$scope.open_step(1);
		
		$scope.loaded = true;
		
		$scope.refreshMissions(text);
	}
});