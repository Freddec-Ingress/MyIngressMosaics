angular.module('FrontModule.controllers').controller('AdmMosaicCtrl', function($scope, API) {
    
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
	
	/* Mosaic management */
	
	$scope.selectMosaic = function(mosaic_ref) {
	    
	    $scope.loading = true;
	    
		API.sendRequest('/api/mosaic/' + mosaic_ref + '/', 'GET').then(function(response) {
            
            $scope.mosaic = response;
            
			$scope.city_name = $scope.mosaic.city.name;
			$scope.region_name = $scope.mosaic.city.region.name;
			$scope.country_name = $scope.mosaic.city.region.country.name;
			
            $scope.loading = false;
        });
	}
	
	$scope.deleteMosaic = function(mosaic) {
	    
	    var data = { 'ref':mosaic.ref }
		API.sendRequest('/api/mosaic/delete/', 'POST', {}, data).then(function(response) {
            
            $scope.mosaic = null;
        });
	}
	
	$scope.editMosaic = function(mosaic) {
	    
	    var data = { 'ref':mosaic.ref, 'city':$scope.city_name, 'region':$scope.region_name, 'country':$scope.country_name, 'type':mosaic.type, 'cols':mosaic.cols, 'title':mosaic.title }
		API.sendRequest('/api/mosaic/edit/', 'POST', {}, data).then(function(response) {
            
            $scope.mosaic = response;
        });
	}
	
	/* Page loading */
	
	$scope.loading = false;
	$scope.mosaic_ref = '';
	
	$scope.init = function(mosaic_ref) {

		if (mosaic_ref) {
			
			$scope.mosaic_ref = mosaic_ref;
			$scope.selectMosaic(mosaic_ref);
		}
		
	    $scope.loaded = true;
	}
});