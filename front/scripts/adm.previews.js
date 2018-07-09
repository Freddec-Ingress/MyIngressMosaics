angular.module('FrontModule.controllers').controller('AdmPreviewsCtrl', function($scope, API) {
	
	/* Tab management */
	
	$scope.current_tab = '';
	
	/* Cleaning management */
	
	$scope.cleaning_chekcing = false;
	$scope.to_be_cleaned = [];
	
	$scope.checkCleaning = function() {
	    
	    $scope.cleaning_chekcing = true;
	    $scope.to_be_cleaned = [];
	    
		var data = { };
		API.sendRequest('/previews/cleaning/check', 'POST', {}, data).then(function(response) {
			
    	    $scope.to_be_cleaned = response;
    	    $scope.cleaning_chekcing = false;
		});
	}
	
	/* Page loading */
	
	$scope.init = function() {
		
    	$scope.current_tab = 'cleaning';
    	
		$scope.loaded = true;
	}
});