angular.module('FrontModule.controllers').controller('TagPageCtrl', function($scope, $window, API) {
	
	/* Page loading */
	
	$scope.init = function(mosaics) {
	
		$scope.mosaics = mosaics;
		
		$scope.loaded = true;
	}
});