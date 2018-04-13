angular.module('FrontModule.controllers').controller('AdmCityCtrl', function($scope, API) {

	/* Country management */

	$scope.countries = [];
  
	/* Page loading */
	
	API.sendRequest('/api/location/country/list/', 'POST', {}, null).then(function(response) {
	
		$scope.countries = response.countries;
	
		$scope.loaded = true;
	});
});