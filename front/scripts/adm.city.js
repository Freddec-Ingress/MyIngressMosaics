angular.module('FrontModule.controllers').controller('AdmCityCtrl', function($scope, API) {

	/* City management */
	
	$scope.cities = [];

	/* Region management */
	
	$scope.regions = [];
	
	$scope.changeCurrentRegion = function(id) {
		
		$scope.cities = [];
		
		$scope.region_changing = true;
		
		var data = { 'region_id':id, };
		API.sendRequest('/api/location/city/list/', 'POST', {}, data).then(function(response) {

			$scope.cities = response.cities;

			$scope.region_changing = false;
		});
	}
	
	/* Country management */

	$scope.countries = [];
	
	$scope.changeCurrentCountry = function(id) {
		
		$scope.cities = [];
		$scope.regions = [];
		
		$scope.country_changing = true;
		
		var data = { 'country_id':id, };
		API.sendRequest('/api/location/region/list/', 'POST', {}, data).then(function(response) {

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