angular.module('FrontModule.controllers').controller('AdmTagCtrl', function($scope, API) {
	
	/* Tag management */
	
	$scope.addTag = function(tag, mosaic) {
		
		var data = { 'ref':mosaic.ref, 'tag':tag };
		API.sendRequest('/api/mosaic/tag/add/', 'POST', {}, data).then(function(response) {
			
			var index = $scope.mosaics.indexOf(mosaic);
			$scope.mosaics.splice(index, 1);
		});
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
			
			for (var mosaic of response.mosaics) {
				if (mosaic.tags == '') {
					$scope.mosaics.push(mosaic);
				}
			}
			
			$scope.searching = false;
		});
	}
	
	/* Page loading */
	
	$scope.init = function() {
		
		$scope.loaded = true;
	}
});