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
		mission.order = UtilsService.getOrderFromMissionName(mission.title);
	}
	
	$scope.detect_order_all = function() {
		for (var mission of $scope.missions) {
			mission.order = UtilsService.getOrderFromMissionName(mission.title);
		}
	}
	
	$scope.reorder = function() {
		
		for (var mission of $scope.missions) {
			API.sendRequest('/api/mission/reorder/', 'POST', {}, mission);
		}
		
		$scope.missions.sort(function(a, b) {
			
			if (parseInt(a.order) < parseInt(b.order))
				return -1;
				
			if (parseInt(a.order) > parseInt(b.order))
				return 1;
			
			return 0;
		});
		
		$scope.current_tab = 'details';
		window.scrollTo(0, 0);
	}
	
	/* Tab management */
	
	$scope.current_tab = 'details';
    
	/* Page init */
	
	$scope.init = function(waiting, missions, creators) {

		$scope.waiting = waiting;
		$scope.creators = creators;
		$scope.missions = missions;
		
		$scope.range = [];
	    for (var i = 0; i < $scope.waiting.mission_count; i++) {
	    	$scope.range.push(i);
	    }

		$scope.missions.sort(function(a, b) {
			
			if (parseInt(a.order) < parseInt(b.order))
				return -1;
				
			if (parseInt(a.order) > parseInt(b.order))
				return 1;
			
			return 0;
		});
		
		$scope.loaded = true;
	}
});
