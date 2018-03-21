angular.module('FrontModule.controllers').controller('NewCityCtrl', function($scope, $window, API, $auth, UserService) {
	
	$scope.signin = UserService.signin;

	$scope.authenticated = $auth.isAuthenticated();
    
	$('.hidden').each(function() { $(this).removeClass('hidden'); })
	
	/* Notification management */
	
	$scope.notify = function() {
		
		if ($scope.authenticated) {
		
			$scope.notified = true;
			
			var data = { 'country_name':$scope.city.country_name, 'region_name':$scope.city.region_name, 'city_name':$scope.city.name }
			API.sendRequest('/api/notif/create', 'POST', {}, data);
		}
		else {
			
			$scope.need_signin = true;
		}
	}
	
	$scope.unnotify = function() {
		
		$scope.notified = false;
		
		var data = { 'country_name':$scope.city.country_name, 'region_name':$scope.city.region_name, 'city_name':$scope.city.name }
		API.sendRequest('/api/notif/delete', 'POST', {}, data);
	}
	
	/* Sorting */
	
	$scope.sortByName = function() {
		
		$scope.sorting = 'by_name';
			
		$scope.mosaics.sort(function(a, b) {
			
			if (a.title > b.title) return 1;
			if (a.title < b.title) return -1;
			
			return 0;
		});
	}
	
	$scope.sortByMissions = function() {
		
		$scope.sorting = 'by_mission_count';
			
		$scope.mosaics.sort(function(a, b) {
			
			if (a.mission_count > b.mission_count) return -1;
			if (a.mission_count < b.mission_count) return 1;
			
			if (a.title > b.title) return 1;
			if (a.title < b.title) return -1;
			
			return 0;
		});
	}
	
	$scope.sortByUniques = function() {
		
		$scope.sorting = 'by_uniques';

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

		$scope.mosaics.sort(function(a, b) {
			
			if (a.id > b.id) return -1;
			if (a.id < b.id) return 1;
			
			return 0;
		});
		
		var index = 0;
		for (var mosaic of $scope.mosaics) {
			mosaic.index_date = Math.floor(index / 25) + 1;
			index += 1;
		}
	}
	
	/* Index management */

	$scope.current_date_index = null;
	$scope.current_name_index = null;
	$scope.current_uniques_index = null;
	$scope.current_missions_index = null;

	$scope.setCurrentDateIndex = function(index) { $scope.current_date_index = index; }
	$scope.setCurrentNameIndex = function(index) { $scope.current_name_index = index; }
	$scope.setCurrentUniquesIndex = function(index) { $scope.current_uniques_index = index; }
	$scope.setCurrentMissionsIndex = function(index) { $scope.current_missions_index = index; }

	/* Page loading */
	
	$scope.current_tab = 'mosaics';
	
	$scope.loadCity = function(country_name, region_name, city_name) {
		
		API.sendRequest('/api/city/' + country_name + '/' + region_name + '/' + city_name + '/', 'GET').then(function(response) {
			
			$scope.city = response.city;
			
			$scope.mosaics = response.mosaics;
			$scope.potentials = response.potentials;
			
			$scope.date_indexes = response.date_indexes;
			$scope.name_indexes = response.name_indexes;
			$scope.uniques_indexes = response.uniques_indexes;
			$scope.missions_indexes = response.missions_indexes;

			/* Mosaic offset */
			for (var mosaic of $scope.mosaics) {
				
				var temp = 0;
				if (mosaic.missions.length > mosaic.cols) {
					temp = mosaic.cols - mosaic.missions.length % mosaic.cols;
					if (temp < 0 || temp > (mosaic.cols - 1)) temp = 0;
				}
				
				mosaic.offset = new Array(temp);
			}

			$scope.current_date_index = $scope.date_indexes[0];
			$scope.current_name_index = $scope.name_indexes[0];
			$scope.current_uniques_index = $scope.uniques_indexes[0];
			$scope.current_missions_index = $scope.missions_indexes[0];

			$scope.sortByMissionCount();
			
			$scope.loaded = true;
		});
	}
});