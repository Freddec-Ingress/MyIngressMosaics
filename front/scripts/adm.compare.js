angular.module('FrontModule.controllers').controller('AdmCompareCtrl', function($scope, API) {
    
	/* Tab management */
    
    $scope.current_tab = 'locations';
    
	/* City management */
    
    $scope.done = function(city) {
    	
    	var data = { 'id':city.id, }
    	API.sendRequest('/api/im/city/done/', 'POST', {}, data);
    	
		var index = $scope.cities.indexOf(city);
		$scope.cities.splice(index, 1);
    }
    
	/* Mosaic management */
    
    $scope.die = function(mosaic) {
    	
    	var data = { 'id':mosaic.id, }
    	API.sendRequest('/api/im/mosaic/die/', 'POST', {}, data);
    	
    	mosaic.dead = true;
    	
		var index = $scope.mosaics.indexOf(mosaic);
		$scope.mosaics.splice(index, 1);
    }
     
    $scope.exclude = function(mosaic) {
    	
    	var data = { 'id':mosaic.id, }
    	API.sendRequest('/api/im/mosaic/exclude/', 'POST', {}, data);
    	
    	mosaic.excluded = true;
    	
		var index = $scope.mosaics.indexOf(mosaic);
		$scope.mosaics.splice(index, 1);
    }
    
    $scope.register = function(mosaic) {
    	
    	var data = { 'id':mosaic.id, }
    	API.sendRequest('/api/im/mosaic/register/', 'POST', {}, data);
    	
    	mosaic.registered = true;
    	
		var index = $scope.mosaics.indexOf(mosaic);
		$scope.mosaics.splice(index, 1);
    }
   
	/* Page loading */
	
	$scope.init = function(countries, cities) {
		
		$scope.countries = countries;
		$scope.cities = cities;
		
		$scope.countries.sort(function(a, b) {

			if (a.diff > b.diff) return 1;
			if (a.diff < b.diff) return -1;
			
			if (a.name > b.name) return 1;
			if (a.name < b.name) return -1;
			
			return 0;
		});
		
		for (var country of $scope.countries) {
		
			country.regions.sort(function(a, b) {

				if (a.diff > b.diff) return 1;
				if (a.diff < b.diff) return -1;
				
				if (a.name > b.name) return 1;
				if (a.name < b.name) return -1;
				
				return 0;
			});
		}
		
		$scope.cities.sort(function(a, b) {

			if (a.country_name > b.country_name) return 1;
			if (a.country_name < b.country_name) return -1;

			if (a.region_name > b.region_name) return 1;
			if (a.region_name < b.region_name) return -1;

			if (a.name > b.name) return 1;
			if (a.name < b.name) return -1;
			
			return 0;
		});
		
        $scope.loaded = true;
	};
});