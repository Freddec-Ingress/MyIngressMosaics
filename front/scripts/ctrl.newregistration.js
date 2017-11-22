angular.module('FrontModule.controllers').controller('NewRegistrationCtrl', function($scope, $window, toastr, API, UtilsService) {
	
	/* Tab management */
	
	$scope.current_step = 0;
	
	$scope.open_step = function(id) {
		
		$scope.current_step = id;
	}
	
	/* Step #1 management */
	
	$scope.missions = [];
	$scope.filtered = [];
	$scope.selected = [];
	
	$scope.refreshing = false;
	
	$scope.filter = '';
	
	$scope.refreshMissions = function() {
		
		$scope.refreshing = true;
		
		$scope.missions = [];
		$scope.filtered = [];
		
		API.sendRequest('/api/missions/', 'POST').then(function(response) {
			
			$scope.missions = response.missions;
			if (!$scope.missions) $scope.missions = [];

			$scope.missions.sort(UtilsService.sortMissionsByCreatorTitleAsc);

			$scope.filterMissions($scope.filter);
			
			$scope.refreshing = false;
		});
	}
	
	$scope.filterMissions = function(text) {
		
		$scope.filter = text;
		$scope.filtered = [];
		
		if (!$scope.filter) $scope.filtered = $scope.missions.slice();
		else  {
			
			for (var item of $scope.missions) {
				
				if (item.title.indexOf(text) != -1 || item.creator.indexOf(text) != -1) {
					$scope.filtered.push(item);
				}
			}
		}
	}
	
	$scope.selectMission = function(mission) {
	
		mission.selected = true;
	}
	
	$scope.unselectMission = function(mission) {
	
		mission.selected = false;
	}
	
	/* Page loading */

	$scope.refreshMissions();
	
	$scope.open_step(1);
	
	$scope.loaded = true;
});