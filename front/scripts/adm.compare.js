angular.module('FrontModule.controllers').controller('AdmCompareCtrl', function($scope, API) {
    
	/* Mosaic management */
    
    $scope.die = function(mosaic) {
    	
    	var data = { 'id':mosaic.id, }
    	API.sendRequest('/api/im/mosaic/die/', 'POST', {}, data);
    	
    	mosaic.dead = true;
    	mosaic.notregistered_count -= 1;
    	mosaic.notregistered = false;
    }
     
    $scope.exclude = function(mosaic) {
    	
    	var data = { 'id':mosaic.id, }
    	API.sendRequest('/api/im/mosaic/exclude/', 'POST', {}, data);
    	
    	mosaic.excluded = true;
    	mosaic.notregistered_count -= 1;
    	mosaic.notregistered = false;
    }
    
    $scope.register = function(mosaic) {
    	
    	var data = { 'id':mosaic.id, }
    	API.sendRequest('/api/im/mosaic/register/', 'POST', {}, data);
    	
    	mosaic.registered = true;
    	mosaic.notregistered_count -= 1;
    	mosaic.notregistered = false;
    }
   
	/* Page loading */
	
	$scope.init = function(cities) {
		
		$scope.cities = cities;
		
		$scope.cities.sort(function(a, b) {
			
			if (a.notregistered_count > b.notregistered_count) return -1;
			if (a.notregistered_count < b.notregistered_count) return 1;
			
			if (a.name > b.name) return 1;
			if (a.name < b.name) return -1;
			
			return 0;
		});
		
        $scope.loaded = true;
	};
});