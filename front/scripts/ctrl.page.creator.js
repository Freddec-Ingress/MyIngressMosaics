angular.module('FrontModule.controllers').controller('CreatorPageCtrl', function($scope, $window, API) {
	
	/* Tab management */

    $scope.current_tab = 'mosaics';
        
	/* Page loading */

	$scope.init = function(name, faction, mosaics, missions) {
		
		$scope.name = name;
		$scope.faction = faction;
		
		$scope.mosaics = mosaics;
		$scope.missions = missions;

		$scope.loaded = true;
	}
});