angular.module('FrontModule.controllers').controller('WaitingPageCtrl', function($scope) {
    
	/* Waiting management */
	
	$scope.getImage = function(index) {
		for (var mission of $scope.missions) {
			if (mission.order == index) {
				return mission.image;
			}
		}
		var i = $scope.missing_missions.indexOf(index);
		if (i == -1) {
			$scope.missing_missions += index + ', ';
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
