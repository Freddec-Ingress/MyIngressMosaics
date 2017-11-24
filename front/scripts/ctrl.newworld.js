angular.module('FrontModule.controllers').controller('NewWorldCtrl', function($scope, $window, API) {
	
	/* Page loading */
	
	API.sendRequest('/api/world/', 'GET').then(function(response) {

		$scope.count = response.count;
		$scope.countries = response.countries;
		
		$scope.countries.sort(function(a, b) {
			return b.mosaics - a.mosaics;
		});
		
		$scope.loaded = true;
	});
});