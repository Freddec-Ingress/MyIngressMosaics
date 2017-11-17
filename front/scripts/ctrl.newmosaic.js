angular.module('FrontModule.controllers').controller('NewMosaicCtrl', function($scope, $window, API) {

	/* Lovers management */

	$scope.toggle_love = function() {
		
		$scope.mosaic.is_loved = !$scope.mosaic.is_loved;
		
		if ($scope.mosaic.is_loved) {
			
			$scope.mosaic.lovers += 1;
			
			var data = { 'ref':$scope.mosaic.ref };
    		API.sendRequest('/api/mosaic/love/', 'POST', {}, data);
		}
		else {
			
			$scope.mosaic.lovers -= 1;
			
			var data = { 'ref':$scope.mosaic.ref };
    		API.sendRequest('/api/mosaic/unlove/', 'POST', {}, data);
		}
	}
	
	/* Tab management */
	
	$scope.current_tab = 0;
	
	$scope.open_tab = function(id) {
		
		$scope.current_tab = id;
	}
	
	/* Page loading */
	
	$scope.load_mosaic = function(ref) {
		
		API.sendRequest('/api/mosaic/' + ref + '/', 'GET').then(function(response) {
		
			$scope.mosaic = response;
			
			$scope.open_tab(1);
			
			$scope.loaded = true;
		});
	}
});