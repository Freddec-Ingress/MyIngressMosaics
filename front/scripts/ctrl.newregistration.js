angular.module('FrontModule.controllers').controller('NewRegistrationCtrl', function($scope, $window, toastr, API) {
	
	/* Tab management */
	
	$scope.current_step = 0;
	
	$scope.open_step = function(id) {
		
		$scope.current_step = id;
	}
	
	/* Page loading */
	
	$scope.open_step(1);
	
	$scope.loaded = true;
});