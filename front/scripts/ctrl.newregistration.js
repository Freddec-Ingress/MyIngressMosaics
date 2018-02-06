angular.module('FrontModule.controllers').controller('NewRegistrationCtrl', function($scope, $window, $location, toastr, API, UtilsService) {
	
	/* Tab management */
	
	$scope.current_step = 0;
	
	$scope.open_step = function(id) {
		
		$scope.current_step = id;
		
		if ($scope.current_step == 3) {
			
			$scope.computeDefault();
		}
	}
	
	/* Step #1 management */
	
	$scope.missions = null;
	$scope.selected = [];
	
	$scope.refreshing = false;
	
	$scope.searchText = '';
	$scope.requestText = '';
	
	$scope.refreshMissions = function(text) {
		
		$scope.searchText = text;
		
		$scope.missions = null;
		
		if (!text || text.length < 3) {
			
			$scope.get_potentials();
			return;
		}

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
	
	$scope.unselectAll = function() {
		
		for (var mission of $scope.missions) {
			if (mission.selected) {
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
		
		mission.selected = false;
		
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
	
	$scope.default = '';
	
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

		if ($scope.region_name == '' || !$scope.region_name) {
			
			$scope.region_name = $scope.country_name;
		}
		
		$scope.$apply();
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

	$scope.computeDefault = function() {
		
		$scope.default = '';
	
		$scope.city_name = '';
		$scope.region_name = '';
		$scope.country_name = '';
		
		var geocoder = new google.maps.Geocoder();
		
		var latlng = {
			lat: parseFloat($scope.selected[0].startLat),
			lng: parseFloat($scope.selected[0].startLng),
		};
		
		geocoder.geocode({'location': latlng}, function(results, status) {
			
			if (status == 'OK') {
				
				var components = null;
				if (results[0]) components = results[0].address_components;
				if (results[1]) components = results[1].address_components;
				
				if (components) {
					
					var city = '';
					var country = '';
					var admin1 = '';
					var admin2 = '';
					var admin3 = '';
					
					for (var item of components) {
						
						if (item.types[0] == 'country') country = item.long_name;
						if (item.types[0] == 'locality') city = item.long_name;
						if (item.types[0] == 'administrative_area_level_1') admin1 = item.long_name;
						if (item.types[0] == 'administrative_area_level_2') admin2 = item.long_name;
						if (item.types[0] == 'administrative_area_level_3') admin3 = item.long_name;
					}
					
					$scope.default = '';
					if (city) $scope.default += city;
					if (admin3) $scope.default += ', ' + admin3;
					if (admin2) $scope.default += ', ' + admin2;
					if (admin1) $scope.default += ', ' + admin1;
					if (country) $scope.default += ', ' + country;

					$scope.$apply();
				}
			}
		});
	}

	/* Step #4 management */
	
	$scope.creating = false;
	
	$scope.createMosaic = function() {
		
		$scope.creating = true;
		
		if ($scope.region_name == '' || !$scope.region_name) {
			
			$scope.region_name = $scope.country_name;
		}
		
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
		
			$('#city_input').val('');
			
			$window.open('https://www.myingressmosaics.com/mosaic/' + response);
			$window.location.href = '/registration';
			
			$scope.open_step(1);
			
			$scope.creating = false;
			
			$scope.refreshMissions();
		});
	}
	
	/* Page loading */

	$scope.init = function(text) {
	
		$scope.open_step(1);
		
		$scope.refreshMissions(text);
		
		$scope.loaded = true;
	}

	/* Potentials management */
	
	$scope.potential_state = 'init';
	
	$scope.get_potentials = function() {
		
		$scope.potential_state = 'searching';
		
		API.sendRequest('/api/potentials/', 'POST').then(function(response) {

			$scope.potentials = response;
			
			$scope.potentials.sort(function(a, b) {
				
				if (a.city.region.country.name > b.city.region.country.name) return 1;
				if (a.city.region.country.name < b.city.region.country.name) return -1;
				
				if (a.city.name > b.city.name) return 1;
				if (a.city.name < b.city.name) return -1;
				
				if (a.count > b.count) return -1;
				if (a.count < b.count) return 1;
				
				return 0;
			});

			$scope.potential_state = 'list';
		});
	}
	
	$scope.exclude = function(potential) {
		
		var index = $scope.potentials.indexOf(potential);
		$scope.potentials.splice(index, 1);
		
		var data = { 'name':potential.name};
		API.sendRequest('/api/adm/potential/exclude', 'POST', {}, data);
	}
});