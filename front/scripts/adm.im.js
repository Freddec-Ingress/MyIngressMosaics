angular.module('FrontModule.controllers').controller('AdmImCtrl', function($scope, API) {

	$scope.cities = [];
	$scope.regions = [];
	$scope.countries = [];
	
	/* Country management */

	$scope.changeCurrentCountry = function(country) {
	
		console.log(country);
	
		$scope.country_changing = true;
		
		$scope.cities = [];
		$scope.regions = country.regions;
		
		$scope.country_changing = false;
	}

	/* Page loading */
	
	$scope.init = function(countries) {
	
		$scope.countries = countries;
		
		$scope.loaded = true;
	};
});