angular.module('FrontModule.controllers').controller('AdmCompareCtrl', function($scope, API) {
    
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
	
    $scope.loaded = true;
});