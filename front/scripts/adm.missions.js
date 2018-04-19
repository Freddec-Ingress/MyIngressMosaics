angular.module('FrontModule.controllers').controller('AdmMissionsCtrl', function($scope, API) {
	
	/* Page loading */
	
	$scope.init = function(missions) {
		
		$scope.missions = missions;
		
    	$scope.loaded = true;
	}
});