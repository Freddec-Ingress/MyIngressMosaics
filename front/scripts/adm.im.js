angular.module('FrontModule.controllers').controller('AdmImCtrl', function($scope, API) {

	/* Page loading */
	
	$scope.init = function(countries) {
	
		$scope.countries = countries;
		
		$scope.loaded = true;
	};
});