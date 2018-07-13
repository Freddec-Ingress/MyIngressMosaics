angular.module('FrontModule.controllers').controller('AdmPotentialCtrl', function($scope, $window, API, UtilsService) {
	
	/* Potential management */
	
	$scope.missions = [];
	
	$scope.refresh = function() {
		
		$scope.refreshing = true;
		
		$scope.missions = [];
		
		var data = { 'text':$scope.name };
		API.sendRequest('/api/potential/refresh/', 'POST', {}, data).then(function(response) {
			
			$scope.missions = response.missions;
			
			for (var mission of $scope.missions) {
				
				if (!mission.order) {
				
					var order = UtilsService.getOrderFromMissionName(mission.title);
					if (order < 1) order = $scope.missions.indexOf(mission) + 1;
					mission.order = order;
				}
			}
			
			$scope.missions.sort(UtilsService.sortMissionsByOrderTitleAsc);
			
			$scope.refreshing = false;
			
			var geocoder = new google.maps.Geocoder();
			
			var latlng = {
				lat: parseFloat($scope.missions[0].startLat),
				lng: parseFloat($scope.missions[0].startLng),
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
		});
		
		var inputCity = document.getElementById('city_input');
	    var options = {
			types: ['(cities)'],
		};
		
		if (!$scope.autocomplete) {
			
		    $scope.autocomplete = new google.maps.places.Autocomplete(inputCity, options);
		        
		    $scope.autocomplete.addListener('place_changed', function() {
		    	
				$scope.city = '';
				$scope.region = '';
				$scope.country = '';
		    	
		    	var place = $scope.autocomplete.getPlace();
		    	console.log(place);
		    	for (var i = 0; i < place.address_components.length; i++) {
		    		
		    		var addressType = place.address_components[i].types[0];
		    		if (addressType == 'country') $scope.country = place.address_components[i]['long_name'];
		    		if (addressType == 'locality') $scope.city = place.address_components[i]['long_name'];
		    		if (addressType == 'administrative_area_level_1') $scope.region = place.address_components[i]['long_name'];
		    		if (addressType == 'administrative_area_level_2' && !$scope.region) $scope.region = place.address_components[i]['long_name'];
		     		if (addressType == 'administrative_area_level_3' && !$scope.city) $scope.city = place.address_components[i]['long_name'];
		   		}
		   		
		   		if (($scope.country == '' || !$scope.country) && $scope.city == 'Simferopol') {
		   			$scope.country = 'Crimea';
		   		}
		
				if ($scope.region == '' || !$scope.region) {
					
					$scope.region = $scope.city;
				}

				$scope.$apply();
			});
		}
	}
	
	$scope.remove_mission = function(mission) {
		
		var index = $scope.missions.indexOf(mission);
		$scope.missions.splice(index, 1);
	}
	
	$scope.missing_missions = '';
	$scope.mission_count = '';
	$scope.waiting = function(new_name) {
		
		var missions = [];
		for (var mission of $scope.missions) missions.push({'ref':mission.ref, 'order':mission.order});
		
		var data = { 'country_name':$scope.country, 'region_name':$scope.region, 'city_name':$scope.city, 'missions':missions, 'title':new_name, 'mission_count':$scope.mission_count };
		API.sendRequest('/api/waiting/create/', 'POST', {}, data).then(function() {
			$window.location.href = '/adm/missions';
		});
	}

	$scope.range = [];
	$scope.setRange = function() {
		
		$scope.missing_missions = '';
		$scope.range = [];
	    for (var i = 0; i < $scope.mission_count; i++) {
	    	$scope.range.push(i);
	    }
	}
	
	$scope.getImage = function(index) {
		for (var mission of $scope.missions) {
			if (mission.order == index) {
				return mission.image;
			}
		}
		var i = $scope.missing_missions.indexOf(index);
		if (i == -1) {
			$scope.missing_missions += index + ', ';
		}
		return null;
	}

	$scope.rename = function(new_name) {
		
		$scope.refreshing = true;
		
		var refs = [];
		for (var mission of $scope.missions) refs.push(mission.ref);
		
		var data = { 'refs':refs, 'new_name':new_name };
		API.sendRequest('/api/potential/update/', 'POST', {}, data).then(function(response) {
			
			$scope.name = new_name;
			
			$scope.refresh();
		});
	}
	
	$scope.validate = function(new_name) {
		
		var refs = [];
		for (var mission of $scope.missions) refs.push(mission.ref);
		
		var data = { 'refs':refs, 'title':new_name, 'country':$scope.country, 'region':$scope.region, 'city':$scope.city };
		API.sendRequest('/api/potential/create/', 'POST', {}, data);
			
		$window.location.href = '/adm/missions';
	}
	
	$scope.clipboardCopy = function() {
		
		var inputCity = $('#city_input');
		inputCity.prop('value', $scope.default);
		inputCity.focus();
	}
	
	/* Page loading */
	
	$scope.init = function(text) {

		if (text) $scope.rename(text);

		$scope.loaded = true;
	}
});