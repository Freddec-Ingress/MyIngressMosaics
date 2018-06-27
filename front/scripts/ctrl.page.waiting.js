angular.module('FrontModule.controllers').controller('WaitingPageCtrl', function($scope) {
    
	/* Tab management */
	
	$scope.current_tab = 'details';
    
	/* Page init */
	
	$scope.init = function(mosaic, missions) {

		$scope.mosaic = mosaic;
		$scope.missions = missions;
	}
});
