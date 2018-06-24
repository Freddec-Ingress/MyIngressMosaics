angular.module('FrontModule.controllers').controller('AdmMissionsCtrl', function($scope, API) {
	
	/* Tab management */
	
	$scope.current_tab = 'tobereviewed';
	
	/* Waiting management */
	
	$scope.delete_waiting = function(index, ref) {
		
		$scope.waitings.splice(index, 1);
		
		var data = { 'ref':ref };
		API.sendRequest('/api/waiting/delete/', 'POST', {}, data)
	}
	
	/* Page loading */
	
	$scope.init = function(missions, reviewed, waitings) {
		
		$scope.missions = missions;
		$scope.reviewed = reviewed;
		$scope.waitings = waitings;
		
    	$scope.loaded = true;
	}
});