angular.module('FrontModule.controllers').controller('NewCountryCtrl', function($scope, $window, API) {
	
	/* Page loading */
	
	$scope.loadCountry = function(name) {
		
		API.sendRequest('/api/country/' + name + '/', 'GET').then(function(response) {
			
			$scope.country = response.country;
			$scope.regions = response.regions;
			
			$scope.loaded = true;
		});
	}
});