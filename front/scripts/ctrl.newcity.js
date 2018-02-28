angular.module('FrontModule.controllers').controller('NewCityCtrl', function($scope, $window, API) {
	
	/* Sorting */
	
	$scope.sortByName = function() {
		
		$scope.sorting = 'by_name';
			
		$scope.potentials.sort(function(a, b) {
			
			if (a.title > b.title) return 1;
			if (a.title < b.title) return -1;
			
			return 0;
		});
		
		
		$scope.mosaics.sort(function(a, b) {
			
			if (a.title > b.title) return 1;
			if (a.title < b.title) return -1;
			
			return 0;
		});
	}
	
	$scope.sortByMissionCount = function() {
		
		$scope.sorting = 'by_mission_count';
			
		$scope.potentials.sort(function(a, b) {
			
			if (a.count > b.count) return -1;
			if (a.count < b.count) return 1;
			
			if (a.title > b.title) return 1;
			if (a.title < b.title) return -1;
			
			return 0;
		});
		
		
		$scope.mosaics.sort(function(a, b) {
			
			if (a.missions.length > b.missions.length) return -1;
			if (a.missions.length < b.missions.length) return 1;
			
			if (a.title > b.title) return 1;
			if (a.title < b.title) return -1;
			
			return 0;
		});
	}
	
	$scope.sortByDate = function() {
		
		$scope.sorting = 'by_date';
			
		$scope.potentials.sort(function(a, b) {
			
			if (a.id > b.id) return -1;
			if (a.id < b.id) return 1;
			
			return 0;
		});
		
		
		$scope.mosaics.sort(function(a, b) {
			
			if (a.id > b.id) return -1;
			if (a.id < b.id) return 1;
			
			return 0;
		});
	}
	
	/* Page loading */
	
	$scope.loadCity = function(country_name, region_name, city_name) {
		
		API.sendRequest('/api/city/' + country_name + '/' + region_name + '/' + city_name + '/', 'GET').then(function(response) {
			
			$scope.city = response.city;
			$scope.potentials = response.potentials;
			$scope.mosaics = response.mosaics;
			
			for (var mosaic of $scope.mosaics) {
				
				var temp = 0;
				if (mosaic.missions.length > mosaic.cols) {
					temp = mosaic.cols - mosaic.missions.length % mosaic.cols;
					if (temp < 0 || temp > (mosaic.cols - 1)) temp = 0;
				}
				
				mosaic.offset = new Array(temp);
			}
			
			$scope.sortByMissionCount();
			
			$scope.loaded = true;
		});
	}
});