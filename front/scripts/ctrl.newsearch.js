angular.module('FrontModule.controllers').controller('NewSearchCtrl', function($scope, $window, API) {
	
	/* Init management */
	
	$scope.searchtext = null;
	
	$scope.init = function(text) {
		
		if (!text) return;
		
		$scope.searchtext = text;
		$scope.search(text);
	}
	
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
			
			$scope.mosaics.sort(function(a, b) {
				
				if (a.title > b.title) return -1;
				if (a.title < b.title) return 1;
				
				return 0;
			});

			$scope.searching = false;
		});
	}
	
	/* Page loading */
	
	$scope.loaded = true;
});