angular.module('FrontModule.controllers').controller('NewRegionCtrl', function($scope, $window, API) {
	
	/* Index management */
	
	$scope.indexes = [];
	
	$scope.current_index = null;
	
	$scope.setCurrentIndex = function(index) {
		
		$scope.current_index = index;
	}
	
	/* Page loading */
	
	$scope.loadRegion = function(country_name, region_name) {
		
		API.sendRequest('/api/new_region/' + country_name + '/' + region_name + '/', 'GET').then(function(response) {

			$scope.region = response.region_data;
			$scope.cities = response.list_of_city_data;

			$scope.cities.sort(function(a, b) {
				if (a.name > b.name) return -1;
				if (a.name < b.name) return 1;
				return 0;
			});

			/* Index & Offset */
			
			for (var city of $scope.cities) {
				
				var index = city.name[0];
				if ($scope.indexes.indexOf(index) == -1) $scope.indexes.push(index);
				
				for (var mosaic of city.mosaics) {
					
					var temp = 0;
					if (mosaic.missions.length > mosaic.cols) {
						temp = mosaic.cols - mosaic.missions.length % mosaic.cols;
						if (temp < 0 || temp > (mosaic.cols - 1)) temp = 0;
					}
					
					mosaic.offset = new Array(temp);
				}
			}
			
			$scope.indexes.sort();
			$scope.setCurrentIndex($scope.indexes[0]);
			
			$scope.loaded = true;
		});
	}
});