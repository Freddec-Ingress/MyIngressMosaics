angular.module('FrontModule.controllers').controller('AdmMissionCtrl', function($scope, API) {
    
	/* Mosaic management */
	
	$scope.loading = false;
	
	$scope.selectMission = function(mission_ref) {
	    
	    $scope.loading = true;
	    
		API.sendRequest('/api/mission/details/' + mission_ref + '/', 'GET').then(function(response) {
            
            $scope.mission = response;
            $scope.loading = false;
        });
	}
	
	/* Page loading */
	
    $scope.loaded = true;
});