angular.module('FrontModule.controllers').controller('AdmPreviewsCtrl', function($scope, API) {
	
	/* Tab management */
	
	$scope.current_tab = '';
	
	/* Preview management */

    var to_generate = [];

	var generate = function() {
	    
	    if (to_generate.length < 1) return;
	    
		var data = { 'ref':to_generate[0].ref,  };
		API.sendRequest('/api/mosaic/preview/generate/', 'POST', {}, data).then(function(response) {
		    
		    to_generate = to_generate.splice(0, 1);
		    generate();
		});
	}
	
	/* Cleaning management */
	
	$scope.cleaning_chekcing = false;
	$scope.to_be_cleaned = [];
	
	$scope.checkCleaning = function() {
	    
	    $scope.cleaning_chekcing = true;
	    $scope.to_be_cleaned = [];
	    
		var data = { };
		API.sendRequest('/api/previews/cleaning/check/', 'POST', {}, data).then(function(response) {
			
    	    $scope.to_be_cleaned = response.mosaics;
    	    $scope.cleaning_chekcing = false;
		});
	}
	
	$scope.generateCleaning = function() {
	    
	    to_generate = $scope.to_be_cleaned;
	    generate();
	}
	
	/* Page loading */
	
	$scope.init = function() {
		
    	$scope.current_tab = 'cleaning';
    	
		$scope.loaded = true;
	}
});