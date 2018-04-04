angular.module('FrontModule.controllers').controller('AdmCompareCtrl', function($scope, API) {
    
	/* Mosaic management */
    
    $scope.die = function(mosaic, city) {
    	
    	var data = { 'id':mosaic.id, }
    	API.sendRequest('/api/im/mosaic/die/', 'POST', {}, data);
    	
    	mosaic.dead = true;
    	mosaic.notregistered = false;
    	
    	city.notregistered_count -= 1;
    }
     
    $scope.exclude = function(mosaic, city) {
    	
    	var data = { 'id':mosaic.id, }
    	API.sendRequest('/api/im/mosaic/exclude/', 'POST', {}, data);
    	
    	mosaic.excluded = true;
    	mosaic.notregistered = false;
    	
    	city.notregistered_count -= 1;
    }
    
    $scope.register = function(mosaic, city) {
    	
    	var data = { 'id':mosaic.id, }
    	API.sendRequest('/api/im/mosaic/register/', 'POST', {}, data);
    	
    	mosaic.registered = true;
    	mosaic.notregistered = false;
    	
    	city.notregistered_count -= 1;
    }
   
	/* Page loading */
	
	$scope.init = function(countries) {
		
		$scope.countries = countries;
		
		$scope.countries.sort(function(a, b) {
			
			if (a.regions.length > 0 && b.regions.length < 1) return -1;
			if (a.regions.length < 1 && b.regions.length > 0) return 1;
			
			if (a.diff > b.diff) return 1;
			if (a.diff < b.diff) return -1;
			
			if (a.name > b.name) return 1;
			if (a.name < b.name) return -1;
			
			return 0;
		});
		
		for (var country of $scope.countries) {
		
			country.regions.sort(function(a, b) {
				
				if (a.cities.length > 0 && b.cities.length < 1) return -1;
				if (a.cities.length < 1 && b.cities.length > 0) return 1;
				
				if (a.diff > b.diff) return 1;
				if (a.diff < b.diff) return -1;
				
				if (a.name > b.name) return 1;
				if (a.name < b.name) return -1;
				
				return 0;
			});
		
			for (var region of country.regions) {
			
				region.cities.sort(function(a, b) {
					
					if (a.mosaics.length > 0 && b.mosaics.length < 1) return -1;
					if (a.mosaics.length < 1 && b.mosaics.length > 0) return 1;
					
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