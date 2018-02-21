angular.module('FrontModule.controllers').controller('AdmMosaicCtrl', function($scope, API) {
    
	/* Mosaic management */
	
	$scope.selectMosaic = function(mosaic_ref) {
	    
	    $scope.loading = true;
	    
		API.sendRequest('/api/mosaic/' + mosaic_ref + '/', 'GET').then(function(response) {
            
            $scope.mosaic = response;
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
	    
	    var data = { 'ref':mosaic.ref, 'city':mosaic.city, 'type':mosaic.type, 'cols':mosaic.cols, 'title':mosaic.title }
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