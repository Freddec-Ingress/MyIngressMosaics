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
	
	$scope.loadRegion = function(country_name, region_name) {
		
		API.sendRequest('/api/new_region/' + country_name + '/' + region_name + '/', 'GET').then(function(response) {

			$scope.country = response.country_data;
			
			$scope.region = response.region_data;
			
			$scope.regions = response.list_of_region_data;
			$scope.regions.sort(function(a, b) {
				return b.mosaics - a.mosaics;
			});
			
			var mosaics = response.list_of_mosaic_data;
			
			$scope.count = mosaics.length;
			
			/* By city list */
			
			$scope.by_city_list = [];
			for (var city_name of response.list_of_city_name) {
				
				var obj = { 'name':city_name, 'mosaics':[] };
				for (var mosaic of mosaics) {
					if (mosaic.city.name == city_name) obj.mosaics.push(mosaic);
				}
				
				obj.mosaics.sort(function(a, b) {
					return a.mission_count - b.mission_count;
				});
				
				$scope.by_city_list.push(obj);
			}
			
			$scope.by_city_list.sort(function(a, b) {
				
				if (a.name > b.name) return 1;
				if (a.name < b.name) return -1;
				
				return 0;
			});
			
			/* By mission list */
			
			/* By date list */
			
			$scope.by_date_list = mosaics.slice();
			$scope.by_date_list.sort(function(a, b) {
				return b.id - a.id;
			});
			
			$scope.sortByCity();
			
			$scope.loaded = true;
		});
	}
});