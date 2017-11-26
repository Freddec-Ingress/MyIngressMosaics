angular.module('FrontModule.controllers').controller('NewRegionCtrl', function($scope, $window, API) {
	
	/* Page loading */
	
	$scope.loadRegion = function(country, name) {
		
		API.sendRequest('/api/region/' + country + '/' + name + '/', 'GET').then(function(response) {

			$scope.count = response.count;
			$scope.region = response.region;
			$scope.country = response.country;
			
			$scope.regions = response.regions;
			$scope.regions.sort(function(a, b) {
				return b.mosaics - a.mosaics;
			});
			
			$scope.loaded = true;
		});
	}
});