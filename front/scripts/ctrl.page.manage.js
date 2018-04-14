angular.module('FrontModule.controllers').controller('ManagePageCtrl', function($scope, API) {
	
	$scope.init = function(mosaic, missions) {

		$scope.mosaic = mosaic;
		
		$scope.loaded = true;
	}
});