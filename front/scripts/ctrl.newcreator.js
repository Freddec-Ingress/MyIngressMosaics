angular.module('FrontModule.controllers').controller('NewCreatorCtrl', function($scope, $window, API, UserService) {
	
	/* Page loading */
	
	UserService.loadUser($scope.user);
	
	$scope.load = function(name) {
		
		API.sendRequest('/api/creator/' + name + '/', 'GET').then(function(response) {
			
			$scope.name = response.name;
			$scope.faction = response.faction;
			
			$scope.mosaics = response.mosaics;
			$scope.missions = response.missions;

            $scope.current_tab = 'mosaic';

			$scope.loaded = true;
		});
	}
});