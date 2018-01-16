angular.module('FrontModule.controllers').controller('AdmMissionCtrl', function($scope, API) {
    
	/* Mission management */
	
	$scope.loading = false;
	
	$scope.selectMission = function(mission_ref) {
	    
	    $scope.loading = true;
	    
	    var data = { 'ref':mission_ref };
		API.sendRequest('/api/mission/details/', 'POST', {}, data).then(function(response) {
            
            $scope.mission = response;
            $scope.loading = false;
        });
	}
	
	$scope.updateMission = function(mission) {
	    
	    $scope.loading = true;
	    
	    var data = { 'ref':mission.ref, 'name':mission.name };
		API.sendRequest('/api/mission/update/', 'POST', {}, data).then(function(response) {
            
            $scope.mission = response;
            $scope.loading = false;
        });
	}
	
	/* Page loading */
	
    $scope.loaded = true;
});