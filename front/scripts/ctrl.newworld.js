angular.module('FrontModule.controllers').controller('NewWorldCtrl', function($scope, $window, API) {
	
	/* Page loading */
	
	API.sendRequest('/api/world/', 'GET').then(function(response) {

		$scope.mosaic_count = response.mosaic_count;
		$scope.countries = response.countries;
		
		$scope.countries.sort(function(a, b) {
			return b.mosaic_count - a.mosaic_count;
		});
		
        var input = document.getElementById('city_input');
        var options = {
			types: ['(cities)'],
		};
		
        var autocomplete = new google.maps.places.Autocomplete(input, options);

        autocomplete.addListener('place_changed', function() {
        	
         	$scope.flag_searching = true;
         	
	       	$scope.flag_city_unknown = false;
        	
        	$scope.city = null;
        	$scope.mosaics = null;
        	
        	var country_name = null;
        	var region_name = null;
        	var city_name = null;
        	
        	var place = autocomplete.getPlace();
        	for (var i = 0; i < place.address_components.length; i++) {
        		
        		var addressType = place.address_components[i].types[0];
        		if (addressType == 'country') country_name = place.address_components[i]['long_name'];
        		if (addressType == 'administrative_area_level_1') region_name = place.address_components[i]['long_name'];
	    		if (addressType == 'administrative_area_level_2' && !region_name) region_name = place.address_components[i]['long_name'];
        		if (addressType == 'locality') city_name = place.address_components[i]['long_name'];
        	}
        	
        	console.log(place.address_components);
	    	
	     	console.log(country_name);
	    	console.log(region_name);
	    	console.log(city_name);
	        
			if (!region_name) region_name = 'unknown';
			
        	if (!country_name || !region_name || !city_name) {
        		
        		$scope.flag_city_unknown = true;
        		
        		$scope.flag_searching = false;
        	}
        	else {
        		
        		API.sendRequest('/api/city/' + country_name + '/' + region_name + '/' + city_name + '/', 'GET').then(function(response) {
        		
        			$scope.city = response.city;
        			$scope.mosaics = response.mosaics;
        			
        			if ($scope.mosaics && $scope.mosaics.length > 0) {
						$window.location.href = '/world/' + country_name + '/' + region_name + '/' + city_name;
        			}

					$scope.flag_searching = false;
        		});
        	}
        });

		$scope.loaded = true;
	});
});