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
			
			if (a.diff > b.diff) return -1;
			if (a.diff < b.diff) return 1;
			
			if (a.name > b.name) return 1;
			if (a.name < b.name) return -1;
			
			return 0;
		});
		
        $scope.loaded = true;
	};
});