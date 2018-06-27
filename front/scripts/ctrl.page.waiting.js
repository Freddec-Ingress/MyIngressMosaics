angular.module('FrontModule.controllers').controller('WaitingPageCtrl', function($scope) {
    
	/* Waiting management */
	
	$scope.getImage = function(index) {
		for (var mission of $scope.missions) {
			if (mission.order == index) {
				return mission.image;
			}
		}
		return null;
	}
	
	/* Tab management */
	
	$scope.current_tab = 'details';
    
	/* Page init */
	
	$scope.init = function(waiting, missions) {

		$scope.waiting = waiting;
		$scope.missions = missions;
		
		$scope.range = [];
	    for (var i = 0; i < $scope.waiting.mission_count; i++) {
	    	$scope.range.push(i);
	    }

		$scope.loaded = true;
	}
});
