angular.module('FrontModule.controllers').controller('NewRegionCtrl', function($scope, $window, API) {
	
	/* Notification management */
	
	$scope.notify = function() {
		
		$scope.region.notified = true;
		
		var data = { 'country_name':$scope.region.country_name, 'region_name':$scope.region.name }
		API.sendRequest('/api/notif/create', 'POST', {}, data);
	}
	
	$scope.unnotify = function() {
		
		$scope.region.notified = false;
		
		var data = { 'country_name':$scope.region.country_name, 'region_name':$scope.region.name }
		API.sendRequest('/api/notif/delete', 'POST', {}, data);
	}
	
	/* Sorting */
	
	$scope.sortByLocation = function() {
		
		$scope.sorting = 'by_location';
		
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
	
	$scope.sortByUniques = function() {
		
		$scope.sorting = 'by_uniques';
			
		$scope.potentials.sort(function(a, b) {
			
			if (a.count > b.count) return -1;
			if (a.count < b.count) return 1;
			
			if (a.title > b.title) return 1;
			if (a.title < b.title) return -1;
			
			return 0;
		});
		
		
		$scope.mosaics.sort(function(a, b) {
			
			if (a.uniques > b.uniques) return -1;
			if (a.uniques < b.uniques) return 1;
			
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
	
	/* Index management */
	
	$scope.indexes = [];
	
	$scope.current_index = null;
	
	$scope.setCurrentIndex = function(index) {
		
		$scope.current_index = index;
	}
	
	/* Page loading */
	
	$scope.loadRegion = function(country_name, region_name) {
		
		API.sendRequest('/api/new_region/' + country_name + '/' + region_name + '/', 'GET').then(function(response) {

			$scope.region = response.region;
			
			$scope.cities = response.cities;
			$scope.mosaics = response.mosaics;
			$scope.potentials = response.potentials;
			
			$scope.location_indexes = response.location_indexes;

			/* Mosaic offset */
			for (var mosaic of $scope.mosaics) {
				
				var temp = 0;
				if (mosaic.missions.length > mosaic.cols) {
					temp = mosaic.cols - mosaic.missions.length % mosaic.cols;
					if (temp < 0 || temp > (mosaic.cols - 1)) temp = 0;
				}
				
				mosaic.offset = new Array(temp);
			}

			$scope.current_index = $scope.location_indexes[0];

			$scope.sortByLocation();

			$scope.loaded = true;
		});
	}
});