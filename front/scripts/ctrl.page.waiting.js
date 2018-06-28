angular.module('FrontModule.controllers').controller('WaitingPageCtrl', function($scope, API, UtilsService) {
    
	/* Waiting management */
	
	$scope.getImage = function(index) {
		for (var mission of $scope.missions) {
			if (mission.order == index) {
				return mission.image;
			}
		}
		return null;
	}
	
	$scope.detect_order = function(mission) {
		mission.neworder = UtilsService.getOrderFromMissionName(mission.title);
	}
	
	$scope.detect_order_all = function() {
		for (var mission of $scope.missions) {
			mission.neworder = UtilsService.getOrderFromMissionName(mission.title);
		}
	}
	
	$scope.reorder = function() {
		for (var mission of $scope.missions) {
			API.sendRequest('/api/mosaic/reorder/', 'POST', {}, mission);
		}
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
