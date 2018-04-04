angular.module('FrontModule.controllers').controller('AdmCompareCtrl', function($scope, API) {
    
	/* Tab management */
    
    $scope.current_tab = 'locations';
    
	/* Mosaic management */
    
    $scope.die = function(mosaic, city, region, country) {
    	
    	var data = { 'id':mosaic.id, }
    	API.sendRequest('/api/im/mosaic/die/', 'POST', {}, data);
    	
    	mosaic.dead = true;
    	mosaic.notregistered = false;
    	
    	city.notregistered -= 1;
    	region.notregistered -= 1;
    	country.notregistered -= 1;
    }
     
    $scope.exclude = function(mosaic, city, region, country) {
    	
    	var data = { 'id':mosaic.id, }
    	API.sendRequest('/api/im/mosaic/exclude/', 'POST', {}, data);
    	
    	mosaic.excluded = true;
    	mosaic.notregistered = false;
    	
    	city.notregistered -= 1;
    	region.notregistered -= 1;
    	country.notregistered -= 1;
    }
    
    $scope.register = function(mosaic, city, region, country) {
    	
    	var data = { 'id':mosaic.id, }
    	API.sendRequest('/api/im/mosaic/register/', 'POST', {}, data);
    	
    	mosaic.registered = true;
    	mosaic.notregistered = false;
    	
    	city.notregistered -= 1;
    	region.notregistered -= 1;
    	country.notregistered -= 1;
    }
   
	/* Page loading */
	
	$scope.init = function(countries, mosaics) {
		
		$scope.countries = countries;
		$scope.mosaics = mosaics;
		
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
		
			for (var region of country.regions) {
			
				region.cities.sort(function(a, b) {

					if (a.diff > b.diff) return 1;
					if (a.diff < b.diff) return -1;
					
					if (a.name > b.name) return 1;
					if (a.name < b.name) return -1;
					
					return 0;
				});
			}
		}
		
        $scope.loaded = true;
	};
});