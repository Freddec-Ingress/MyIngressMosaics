angular.module('FrontModule.controllers').controller('NewCityCtrl', function($scope, $window, API) {
	
	/* Page loading */
	
	$scope.loadCity = function(country_name, region_name, city_name) {
		
		API.sendRequest('/api/city/' + country_name + '/' + region_name + '/' + city_name + '/', 'GET').then(function(response) {
			
			$scope.city = response.city;
			$scope.mosaics = response.mosaics;
			
			$scope.mosaics.sort(function(a, b) {
				
				if (a.missions.length > b.missions.length) return 1;
				if (a.missions.length < b.missions.length) return -1;
				
				return 0;
			});
			
			for (var mosaic of $scope.mosaics) {
				
				var temp = 0;
				if (mosaic.missions.length > mosaic.cols) {
					temp = mosaic.cols - mosaic.missions.length % mosaic.cols;
					if (temp < 0 || temp > (mosaic.cols - 1)) temp = 0;
				}
				
				mosaic.offset = new Array(temp);
			}
			
			$scope.loaded = true;
		});
	}
});