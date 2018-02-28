angular.module('FrontModule.controllers').controller('NewRegionCtrl', function($scope, $window, API) {
	
	/* Sorting */
	
	$scope.sortByName = function(city) {
		
		city.sorting = 'by_name';
			
		city.potentials.sort(function(a, b) {
			
			if (a.title > b.title) return 1;
			if (a.title < b.title) return -1;
			
			return 0;
		});
		
		
		city.mosaics.sort(function(a, b) {
			
			if (a.title > b.title) return 1;
			if (a.title < b.title) return -1;
			
			return 0;
		});
	}
	
	$scope.sortByMissionCount = function(city) {
		
		city.sorting = 'by_mission_count';
			
		city.potentials.sort(function(a, b) {
			
			if (a.count > b.count) return -1;
			if (a.count < b.count) return 1;
			
			if (a.title > b.title) return 1;
			if (a.title < b.title) return -1;
			
			return 0;
		});
		
		
		city.mosaics.sort(function(a, b) {
			
			if (a.missions.length > b.missions.length) return -1;
			if (a.missions.length < b.missions.length) return 1;
			
			if (a.title > b.title) return 1;
			if (a.title < b.title) return -1;
			
			return 0;
		});
	}
	
	$scope.sortByDate = function(city) {
		
		city.sorting = 'by_date';
			
		city.potentials.sort(function(a, b) {
			
			if (a.id > b.id) return -1;
			if (a.id < b.id) return 1;
			
			return 0;
		});
		
		
		city.mosaics.sort(function(a, b) {
			
			if (a.id > b.id) return -1;
			if (a.id < b.id) return 1;
			
			return 0;
		});
	}
	
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
			$scope.indexes = response.index_data;
			
			$scope.city_count = 0;
			
			/* Index & Offset */
			
			for (var index of $scope.indexes) {
				
				for (var city of index.cities) {
					for (var mosaic of city.mosaics) {
						
						var temp = 0;
						if (mosaic.missions.length > mosaic.cols) {
							temp = mosaic.cols - mosaic.missions.length % mosaic.cols;
							if (temp < 0 || temp > (mosaic.cols - 1)) temp = 0;
						}
						
						mosaic.offset = new Array(temp);
					}
				}
				
				index.cities.sort(function(a, b) {
					
					if (a.name > b.name) return -1;
					if (a.name < b.name) return 1;
					
					return 0;
				});
				
				if (!$scope.current_index && index.cities.length > 0) $scope.current_index = index;
				
				$scope.city_count += index.cities.length;
			}
			
			$scope.loaded = true;
		});
	}
});