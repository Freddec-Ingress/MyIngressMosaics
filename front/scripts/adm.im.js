angular.module('FrontModule.controllers').controller('AdmImCtrl', function($scope, API) {

	$scope.cities = [];
	$scope.regions = [];
	$scope.countries = [];
	
	/* Country management */

	$scope.changeCurrentCountry = function(country) {
	
		$scope.cities = [];
		$scope.regions = country.regions;
		
		$scope.country_changing = true;
	}

	/* Page loading */
	
	$scope.init = function(countries) {
	
		$scope.countries = countries;
		
		$scope.loaded = true;
	};
});