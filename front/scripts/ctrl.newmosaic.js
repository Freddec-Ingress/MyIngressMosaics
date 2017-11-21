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

	/* Completers management */

	$scope.toggle_complete = function() {
		
		$scope.mosaic.is_completed = !$scope.mosaic.is_completed;
		
		if ($scope.mosaic.is_completed) {
			
			$scope.mosaic.completers += 1;
			
			var data = { 'ref':$scope.mosaic.ref };
    		API.sendRequest('/api/mosaic/complete/', 'POST', {}, data);
		}
		else {
			
			$scope.mosaic.completers -= 1;
			
			var data = { 'ref':$scope.mosaic.ref };
    		API.sendRequest('/api/mosaic/uncomplete/', 'POST', {}, data);
		}
	}
	
	/* Mission details displaying */

	$scope.mission_selected = null;

	$scope.displayMissionDetails = function(mission) {
		
		$scope.mission_selected = mission;
	}

	$scope.closeMissionDetails = function() {
		
		$scope.mission_selected = null;
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