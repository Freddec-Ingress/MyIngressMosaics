angular.module('FrontModule.controllers').controller('AdmCityCtrl', function($scope, API) {

	/* City management */
	
	$scope.cities = [];

	/* Region management */
	
	$scope.regions = [];
	
	/* Country management */

	$scope.countries = [];
	
	$scope.changeCurrentCountry = function(id) {
		
		$scope.cities = [];
		$scope.regions = [];
		
		$scope.country_changing = true;
		
		var data = { 'country_id':id, };
		API.sendRequest('/api/location/country/list/', 'POST', {}, data).then(function(response) {

			$scope.regions = response.regions;

			$scope.country_changing = false;
		});
	}
	
	/* Page loading */
	
	API.sendRequest('/api/location/country/list/', 'POST', {}, null).then(function(response) {
	
		$scope.countries = response.countries;
	
		$scope.loaded = true;
	});
});