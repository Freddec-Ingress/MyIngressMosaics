angular.module('FrontModule.controllers').controller('AdmMissionsCtrl', function($scope, API) {
	
	/* Mission management */
	
	$scope.exclude = function(mission) {
		
		var refs = [mission.ref];

		var data = { 'refs':refs };
		API.sendRequest('/api/potential/exclude/', 'POST', {}, data).then(function(esponse) {
			
			var index = $scope.missions.indexOf(mission);
			$scope.missions.splice(index, 1);
		});
	}
	
	/* Page loading */
	
	$scope.init = function(missions) {
		
		$scope.missions = missions;
		
    	$scope.loaded = true;
	}
});