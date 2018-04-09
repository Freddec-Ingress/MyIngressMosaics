angular.module('FrontModule.controllers').controller('RegistrationPageCtrl', function($scope, $window, $location, API, $auth, UserService, UtilsService) {
	
	$scope.signin = UserService.signin;

	$scope.authenticated = $auth.isAuthenticated();
    
	$('.hidden').each(function() { $(this).removeClass('hidden'); })
	
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
	
	$scope.refreshMissions = function(text, select_all=false) {
		
		$scope.searchText = text;
		
		$scope.missions = null;
		
		if (!text || text.length < 3) {
			return;
		}

		$scope.refreshing = true;
		
		var data = { 'text':text };
		API.sendRequest('/api/search/missions/', 'POST', {}, data).then(function(response) {
			
			$scope.missions = response.missions;
			if (!$scope.missions) $scope.missions = [];

			for (var mission of $scope.missions) {
				for (var select of $scope.selected) {
					if (mission.ref == select.ref) {
						mission.selected = true;
						break;
					}
				}
			}
			
			$scope.potential = response.potential;
			if ($scope.potential) $scope.mosaic_name =$scope.potential.title;

			$scope.refreshing = false;
			
			if (select_all) $scope.selectAll();
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
		
		for (var mission of $scope.selected) {
			mission.selected = false;
		}
		
		$scope.selected = [];
	}

	/* Step #2 management */
	
	$scope.columns = '6';
	
	$scope.offset = [];
	
	$scope.mission_selected = null;

	$scope.computeOffset = function() {
		
		var temp = 0;
		if ($scope.selected.length > $scope.columns) {
			temp = $scope.columns - $scope.selected.length % $scope.columns;
			if (temp < 0 || temp > ($scope.columns - 1)) temp = 0;
		}
		
		$scope.offset = new Array(temp);
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
	$scope.mosaic_tags = '';
	
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

	$scope.computeDefault = function() {
		
		$scope.default = '';
	
		if ($scope.potential) {
			
			$scope.city_name = $scope.potential.city_name;
			$scope.region_name = $scope.potential.region_name;
			$scope.country_name = $scope.potential.country_name;
			
			$scope.mosaic_city = $scope.city_name + ', ' + $scope.region_name + ', ' + $scope.country_name;
			
		} else {
			
			$scope.city_name = '';
			$scope.region_name = '';
			$scope.country_name = '';
		}
		
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
	
	$scope.clipboardCopy = function() {
		
		var input = $('#city_input');
		input.prop('value', $scope.default);
		input.focus();
	}
	
	$scope.addTag = function(tag) {
		
		$scope.mosaic_tags += tag + '|';
	}
	
	$scope.removeTag = function(tag) {
		
		var str = tag + '|';
		$scope.mosaic_tags.replace(str, '');
	}
	
	/* Step #4 management */
	
	$scope.creating = false;
	
	$scope.createMosaic = function() {
		
		$scope.creating = true;
		
		if ($scope.region_name == '' || !$scope.region_name) {
			
			$scope.region_name = $scope.country_name;
		}
		
		if ($scope.potential) {
			
			var data = { 'title':$scope.potential.title, 'city_name':$scope.potential.city_name, 'country_name':$scope.potential.country_name, };
			API.sendRequest('/api/potential/delete/', 'POST', {}, data);
			$scope.potential = null;
		}
		
		var data = {
			'country': $scope.country_name,
			'region': $scope.region_name,
			'city': $scope.city_name,
			'columns': $scope.columns,
			'type': $scope.mosaic_type,
			'title': $scope.mosaic_name,
			'missions': $scope.selected,
			'tags':$scope.mosaic_tags,
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
			$scope.mosaic_tags = '';
			
			$scope.city_name = '';
			$scope.region_name = '';
			$scope.country_name = '';
		
			$('#city_input').val('');
			
			$window.open('https://www.myingressmosaics.com/mosaic/' + response);
			$window.location.href = '/registration';
			
			$scope.open_step(1);
			
			$scope.creating = false;
			
			$scope.refreshMissions();
			
		}, function(response) {

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
			$scope.mosaic_tags = '';
			
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

	$scope.init = function(text, countries) {
	
		$scope.countries = countries;
	
		$scope.open_step(1);
		
		if ($scope.authenticated && text) {
			
			$scope.refreshMissions(text, true);
		}
		
		$scope.loaded = true;
	}
});