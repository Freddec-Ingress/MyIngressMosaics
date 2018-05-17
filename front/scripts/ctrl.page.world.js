angular.module('FrontModule.controllers').controller('WorldPageCtrl', function($scope, $window, API) {
    
    $('.hidden').each(function() { $(this).removeClass('hidden'); })
	
    /* Autocomplete management */
    
    var input = document.getElementById('city_autocomplete');
    var options = { types: ['(cities)'], };
    var autocomplete = new google.maps.places.Autocomplete(input, options);

    autocomplete.addListener('place_changed', function() {
    	
       	$scope.f_city_unknown = false;
		$scope.f_city_nomosaic = false;
     	$scope.f_city_searching = true;
		
    	var city_name = null;
    	var region_name = null;
    	var country_name = null;
    	
    	var place = autocomplete.getPlace();
    	for (var i = 0; i < place.address_components.length; i++) {
    		
    		var addressType = place.address_components[i].types[0];
    		if (addressType == 'country') country_name = place.address_components[i]['long_name'];
    		if (addressType == 'locality') city_name = place.address_components[i]['long_name'];
    		if (addressType == 'administrative_area_level_1') region_name = place.address_components[i]['long_name'];
    		if (addressType == 'administrative_area_level_2' && !region_name) region_name = place.address_components[i]['long_name'];
    	}
    	
		if (!region_name) region_name = city_name;
		
    	if (!country_name || !region_name || !city_name) {
    		
    		$scope.f_city_unknown = true;
    		$scope.f_city_searching = false;
    	}
    	else {
    		
    		var data = { 'name':city_name, 'region_name':region_name, 'country_name':country_name };
    		API.sendRequest('/api/search/city/', 'POST', {}, data).then(function(response) {
    		
    			if (response.city) {
    				
					$window.location.href = '/world/' + country_name + '/' + region_name + '/' + city_name;
    			}
    			else {
    				
    				$scope.f_city_nomosaic = true;
    			}
    		
				$scope.f_city_searching = false;
    		
    			
    		}, function(response) {
    			
    			$scope.f_city_nomosaic = true;
    			$scope.f_city_searching = false;
    		});
    	}
    });
	
	/* Tab management */

	$scope.current_tab = 'countries';
	
	/* Countries sorting */
	
	$scope.sortCountriesByMosaics = function() {
		
		$scope.countries_sorting = 'by_mosaics';

		$scope.countries.sort(function(a, b) {
			
			if (a.mosaic_count > b.mosaic_count) return -1;
			if (a.mosaic_count < b.mosaic_count) return 1;
			
			if (a.name > b.name) return 1;
			if (a.name < b.name) return -1;
			
			return 0;
		});
	}
	
	$scope.sortCountriesByName = function() {
		
		$scope.countries_sorting = 'by_name';

		$scope.countries.sort(function(a, b) {
			
			if (a.name > b.name) return 1;
			if (a.name < b.name) return -1;
			
			return 0;
		});
	}
 	
	/* Tags sorting */
	
	$scope.sortTagsByMosaics = function() {
		
		$scope.tags_sorting = 'by_mosaics';

		$scope.tags.sort(function(a, b) {
			
			if (a.count > b.count) return -1;
			if (a.count < b.count) return 1;
			
			if (a.label > b.label) return 1;
			if (a.label < b.label) return -1;
			
			return 0;
		});
		
		$scope.inactive_tags.sort(function(a, b) {
			
			if (a.count > b.count) return -1;
			if (a.count < b.count) return 1;
			
			if (a.label > b.label) return 1;
			if (a.label < b.label) return -1;
			
			return 0;
		});
	}
	
	$scope.sortTagsByName = function() {
		
		$scope.tags_sorting = 'by_name';

		$scope.tags.sort(function(a, b) {
			
			if (a.label > b.label) return 1;
			if (a.label < b.label) return -1;
			
			return 0;
		});

		$scope.inactive_tags.sort(function(a, b) {
			
			if (a.label > b.label) return 1;
			if (a.label < b.label) return -1;
			
			return 0;
		});
	}
   
    /* Page loading */
    
    $scope.init = function(countries, tags, inactive_tags) {
    	
    	$scope.tags = tags;
     	$scope.inactive_tags = inactive_tags;
     	
   		$scope.countries = countries;
    	
    	$scope.sortCountriesByMosaics();
     	$scope.sortTagsByMosaics();
   	
    	$scope.loaded = true;
    }
});