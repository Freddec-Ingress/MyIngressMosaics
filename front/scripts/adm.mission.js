angular.module('FrontModule.controllers').controller('AdmMissionCtrl', function($scope, API) {
    
	/* Mission management */
	
	$scope.loading = false;
	
	$scope.selectMission = function(mission_ref) {
	    
	    $scope.loading = true;
	    
	    $scope.mission = null;
	    
	    var data = { 'ref':mission_ref };
		API.sendRequest('/api/mission/details/', 'POST', {}, data).then(function(response) {
            
            $scope.mission = response;
            $scope.loading = false;
            
            console.log($scope.mission);
        });
	}
	
	$scope.updateMission = function(mission) {
	    
	    $scope.loading = true;
	    
        console.log($scope.mission);
        
	    var data = { 'ref':$scope.mission.ref, 'name':$scope.mission.name };
	    console.log(data);
		API.sendRequest('/api/mission/update/', 'POST', {}, data).then(function(response) {
            
            $scope.mission = response;
            $scope.loading = false;
        });
	}
	
	/* Page loading */
	
	$scope.mission = null;
	
    $scope.loaded = true;
});