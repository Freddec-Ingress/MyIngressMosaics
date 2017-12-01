angular.module('FrontModule.controllers').controller('AdmMosaicCtrl', function($scope, API) {
    
	/* Mosaic management */
	
	$scope.selectMosaic = function(mosaic_ref) {
	    
		API.sendRequest('/api/mosaic/' + mosaic_ref + '/', 'GET').then(function(response) {
            
            $scope.mosaic = response;
        });
	}
	
	$scope.deleteMosaic = function(mosaic) {
	    
	    var data = { 'ref':mosaic.ref }
		API.sendRequest('/api/mosaic/delete/', 'POST', {}, data).then(function(response) {
            
            $scope.mosaic = null;
        });
	}
	
	/* Page loading */
	
    $scope.loaded = true;
});