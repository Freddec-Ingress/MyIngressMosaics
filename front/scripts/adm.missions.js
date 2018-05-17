angular.module('FrontModule.controllers').controller('AdmMissionsCtrl', function($scope, API) {
	
	/* Tab management */
	
	$scope.current_tab = 'tobereviewed';
	
	/* Page loading */
	
	$scope.init = function(missions, reviewed) {
		
		$scope.missions = missions;
		$scope.reviewed = reviewed;
		
    	$scope.loaded = true;
	}
});