angular.module('FrontModule.controllers').controller('AdmTagCtrl', function($scope, API) {
	
	/* Search management */
	
	$scope.mosaics = null;
	
	$scope.searching = false;

	$scope.search = function(text) {
		
		if (!text) return;
		if (text.length < 3) return;
		
		$scope.searching = true;
		
		$scope.mosaics = null;
		
		var data = { 'text':text };
		API.sendRequest('/api/search/', 'POST', {}, data).then(function(response) {
			
			$scope.mosaics = response.mosaics;
			$scope.searching = false;
		});
	}
	
	/* Page loading */
	
	$scope.init = function() {
		
		$scope.loaded = true;
	}
});