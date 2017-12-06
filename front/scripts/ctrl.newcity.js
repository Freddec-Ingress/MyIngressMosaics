angular.module('FrontModule.controllers').controller('NewCityCtrl', function($scope, $window, API) {
	
	/* Page loading */
	
	$scope.loadCity = function(country_name, region_name, city_name) {
		
		API.sendRequest('/api/city/' + country_name + '/' + region_name + '/' + city_name + '/', 'GET').then(function(response) {
			
			$scope.city = response.city;
			$scope.mosaics = response.mosaics;
			
			$scope.loaded = true;
		});
	}
});