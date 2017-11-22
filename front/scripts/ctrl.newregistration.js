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
		$scope.selected.push(mission);
	}
	
	$scope.selectAll = function() {
		
		for (var mission of $scope.filtered) {
			if (!mission.selected) {
				$scope.selectMission(mission);
			}
		}
	}
	
	$scope.unselectMission = function(mission) {
	
		mission.selected = false;
		
		var index = $scope.selected.indexOf(mission);
		$scope.selected.splice(index, 1);
	}
	
	$scope.removeMission = function(mission) {
		
		var index = $scope.filtered.indexOf(mission);
		$scope.filtered.splice(index, 1);
		
		index = $scope.selected.indexOf(mission);
		$scope.selected.splice(index, 1);
		
		index = $scope.missions.indexOf(mission);
		$scope.missions.splice(index, 1);
		
		var data = { 'ref':mission.ref };
		API.sendRequest('/api/mission/exclude/', 'POST', {}, data);
	}
	
	/* Page loading */

	$scope.refreshMissions();
	
	$scope.open_step(1);
	
	$scope.loaded = true;
});