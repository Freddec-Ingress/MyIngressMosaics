angular.module('FrontModule.controllers').controller('AdmCompareCtrl', function($scope, API) {
    
	/* City management */
    
    $scope.done = function(city) {
    	
    	var data = { 'id':city.id, }
    	API.sendRequest('/api/im/city/done/', 'POST', {}, data);
    }
    
	/* Mosaic management */
    
    $scope.die = function(mosaic) {
    	
    	var data = { 'id':mosaic.id, }
    	API.sendRequest('/api/im/mosaic/die/', 'POST', {}, data);
    	
    	mosaic.dead = true;
    }
     
    $scope.exclude = function(mosaic) {
    	
    	var data = { 'id':mosaic.id, }
    	API.sendRequest('/api/im/mosaic/exclude/', 'POST', {}, data);
    	
    	mosaic.excluded = true;
    }
    
    $scope.register = function(mosaic) {
    	
    	var data = { 'id':mosaic.id, }
    	API.sendRequest('/api/im/mosaic/register/', 'POST', {}, data);
    	
    	mosaic.registered = true;
    }
   
	/* Page loading */
	
    $scope.loaded = true;
});