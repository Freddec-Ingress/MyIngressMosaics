angular.module('FrontModule.controllers').controller('AdmMissionsCtrl', function($scope, API) {
	
	/* Mission management */
	
	$scope.exclude = function(mission) {
		
		var refs = [mission.ref];

		var data = { 'refs':refs };
		API.sendRequest('/api/potential/exclude/', 'POST', {}, data);
			
		var index = $scope.missions.indexOf(mission);
		$scope.missions.splice(index, 1);
	}
	
	$scope.remove_creator = function(creator_name) {
		
		var refs = [];
		var missions = [];
		
		for (var mission of $scope.missions) {
			if (mission.creator == creator_name) {
				
				refs.push(mission.ref);
				missions.push(mission);
			}
		}
		
		var data = { 'refs':refs };
		API.sendRequest('/api/potential/exclude/', 'POST', {}, data);
			
		for (var mission of missions) {
			
			var index = $scope.missions.indexOf(mission);
			$scope.missions.splice(index, 1);
		}
	}
	
	/* Page loading */
	
	$scope.init = function(missions) {
		
		$scope.missions = missions;
		
    	$scope.loaded = true;
	}
});