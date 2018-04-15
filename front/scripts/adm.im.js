angular.module('FrontModule.controllers').controller('AdmRegionCtrl', function($scope, API) {

	/* Page loading */
	
	$scope.init = function(countries) {
	
		$scope.countries = countries;
		
		$scope.loaded = true;
	};
});