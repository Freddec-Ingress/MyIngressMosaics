angular.module('FrontModule.controllers').controller('CreatorPageCtrl', function($scope, $window, API) {
	
	/* Tab management */

    $scope.current_tab = 'mosaics';
        
	/* Page loading */

	$scope.init = function(mosaics, missions) {
		
		$scope.mosaics = mosaics;
		$scope.missions = missions;

		$scope.loaded = true;
	}
});