angular.module('FrontModule.controllers').controller('AdmCityCtrl', function($scope, API) {
	
	/* Country management */
	
	$scope.selectCountry = function(country_id) {
	    
        $scope.regions = [];
        
        var data = { 'country_id':country_id };
        API.sendRequest('/api/region/list/', 'POST', {}, data).then(function(response) {
            
            $scope.regions = response.regions;
        });
	}
	
	/* Region management */
	
	var selected_region_id = null;
	
	$scope.selectRegion = function(region_id) {
	    
	    selected_region_id = region_id;
	    
        $scope.cities = [];
        
        var data = { 'region_id':region_id };
        API.sendRequest('/api/city/list/', 'POST', {}, data).then(function(response) {
            
            $scope.cities = response.cities;
        });
	}
	
	$scope.refreshRegion = function() {
	    
	    $scope.selectRegion(selected_region_id);
	}
	
	/* City management */
	
	$scope.createCity = function(region_id, name, locale) {
	    
        var data = { 'region_id':region_id, 'name':name, 'locale':locale };
        API.sendRequest('/api/city/create/', 'POST', {}, data).then(function(response) {
            
            $scope.refreshRegion();
        });
	}
	
	$scope.mergeCities = function(src_id, dest_id) {
	    
        var data = { 'src_id':src_id, 'dest_id':dest_id };
        API.sendRequest('/api/city/move/', 'POST', {}, data).then(function(response) {
            
            $scope.refreshRegion();
        });
	}
	
	$scope.updateCity = function(city_id, new_name, new_locale) {
	    
        var data = { 'id':city_id, 'new_name':new_name, 'new_locale':new_locale };
        API.sendRequest('/api/city/update/', 'POST', {}, data).then(function(response) {
            
            $scope.refreshRegion();
        });
	}
	
	$scope.deleteCity = function(city_id) {
	    
        var data = { 'id':city_id };
        API.sendRequest('/api/city/delete/', 'POST', {}, data).then(function(response) {
            
            $scope.refreshRegion();
        });
	}
	
	$scope.teleportCity = function(region_id, city_id) {
	    
        var data = { 'region_id':region_id, 'city_id':city_id };
        API.sendRequest('/api/city/teleport/', 'POST', {}, data).then(function(response) {
            
            $scope.refreshRegion();
        });
	}
	
	/* Page loading */
	
    var input = document.getElementById('city_input');
    var options = {
		types: ['(cities)'],
	};
	
    var autocomplete = new google.maps.places.Autocomplete(input, options);
        
    autocomplete.addListener('place_changed', function() {
    	
    	var place = autocomplete.getPlace();
    	console.log(place.address_components);
	});
	
	API.sendRequest('/api/country/list/', 'POST').then(function(response) {
    
        $scope.countries = response.countries;
        
    	$scope.loaded = true;
	});
});