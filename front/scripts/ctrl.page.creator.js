angular.module('FrontModule.controllers').controller('CreatorPageCtrl', function($scope, $window, API) {
	
	/* Tab management */

    $scope.current_tab = 'mosaics';
        
	/* Page loading */

	$scope.init = function(faction, mosaics, missions) {
		
		$scope.faction = faction;
		
		$scope.mosaics = mosaics;
		$scope.missions = missions;

		$scope.loaded = true;
	}
});