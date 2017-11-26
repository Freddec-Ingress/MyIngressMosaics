angular.module('FrontModule.controllers').controller('NewRegionCtrl', function($scope, $window, API) {
	
	/* Sort management */
	
	$scope.current_sort = 'by_city';
	
	$scope.sortByCity = function() {
		
		$scope.current_sort = 'by_city';
	}
	
	$scope.sortByMissions = function() {
		
		$scope.current_sort = 'by_missions';
	}
	
	$scope.sortByDate = function() {
		
		$scope.current_sort = 'by_date';
	}
	
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
			
			$scope.bycities = response.cities;
			$scope.bymissions = response.by_missions;
			$scope.bydate = response.by_date;

			$scope.sortByCity();
			
			$scope.loaded = true;
		});
	}
});