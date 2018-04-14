angular.module('FrontModule.controllers').controller('ManagePageCtrl', function($scope, API) {
	
	/* Tab management */
	
	$scope.current_tab = 'details';
	
	/* Page loading */
	
	$scope.init = function(mosaic, missions) {

		$scope.mosaic = mosaic;
		$scope.missions = missions;
		
		$scope.loaded = true;
	}
});