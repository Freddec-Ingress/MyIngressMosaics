angular.module('FrontModule.controllers').controller('AdmMissionCtrl', function($scope, API) {
    
	/* Mission management */
	
	$scope.loading = false;
	
	$scope.selectMission = function(mission_ref) {
	    
	    $scope.loading = true;
	    
	    $scope.mission = null;
	    
	    var data = { 'ref':mission_ref };
		API.sendRequest('/api/mission/details/', 'POST', {}, data).then(function(response) {
            
            $scope.mission = response.mission;
            $scope.loading = false;
        });
	}
	
	$scope.updateMission = function() {
	    
	    $scope.loading = true;
        
	    var data = { 'ref':$scope.mission.ref, 'name':$scope.mission.name };
		API.sendRequest('/api/mission/update/', 'POST', {}, data).then(function(response) {
            
            $scope.mission = response.mission;
            $scope.loading = false;
        });
	}
	
	/* Page loading */
	
	$scope.mission = null;
	
    $scope.loaded = true;
});