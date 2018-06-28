angular.module('FrontModule.controllers').controller('CityPageCtrl', function($scope, $window, API, $auth, UserService) {
	
	$scope.signin = UserService.signin;

	$scope.authenticated = $auth.isAuthenticated();
    
	$('.hidden').each(function() { $(this).removeClass('hidden'); })
	
	/* Notification management */
	
	$scope.notify = function() {
		
		if ($scope.authenticated) {
		
			$scope.city.notified = true;
			
			var data = { 'country_name':$scope.city.country_name, 'region_name':$scope.city.region_name, 'city_name':$scope.city.name }
			API.sendRequest('/api/notif/create/', 'POST', {}, data);
		}
		else {
			
			$scope.need_signin = true;
		}
	}
	
	$scope.unnotify = function() {
		
		$scope.city.notified = false;
		
		var data = { 'country_name':$scope.city.country_name, 'region_name':$scope.city.region_name, 'city_name':$scope.city.name }
		API.sendRequest('/api/notif/delete/', 'POST', {}, data);
	}
	
	/* Tab management */
	
	$scope.current_tab = 'mosaics';
	
	/* Sorting */
	
	$scope.sortMosaicsByName = function() {
		
		$scope.mosaics_sorting = 'by_name';

		$scope.mosaics.sort(function(a, b) {
			
			if (a.title > b.title) return 1;
			if (a.title < b.title) return -1;
			
			return 0;
		});
	}
	
	$scope.sortMosaicsByUniques = function() {
		
		$scope.mosaics_sorting = 'by_uniques';

		$scope.mosaics.sort(function(a, b) {
			
			if (a.unique_count > b.unique_count) return 1;
			if (a.unique_count < b.unique_count) return -1;
			
			if (a.images.length > b.images.length) return 1;
			if (a.images.length < b.images.length) return -1;
			
			return 0;
		});
		
		for (var mosaic of $scope.mosaics) {
			mosaic.index_uniques = Math.floor(mosaic.unique_count / 100);
		}
	}
	
	$scope.sortMosaicsByDate = function() {
		
		$scope.mosaics_sorting = 'by_date';

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
	
	$scope.sortMosaicsByMissions = function() {
		
		$scope.mosaics_sorting = 'by_missions';

		$scope.mosaics.sort(function(a, b) {
			
			if (a.images.length > b.images.length) return -1;
			if (a.images.length < b.images.length) return 1;
			
			if (a.title > b.title) return 1;
			if (a.title < b.title) return -1;
			
			return 0;
		});
	}
	
	/* Index management */

	$scope.current_mosaics_date_index = null;
	$scope.current_mosaics_name_index = null;
	$scope.current_mosaics_uniques_index = null;
	$scope.current_mosaics_missions_index = null;

	$scope.setCurrentMosaicsDateIndex = function(index) { $scope.current_mosaics_date_index = index; }
	$scope.setCurrentMosaicsNameIndex = function(index) { $scope.current_mosaics_name_index = index; }
	$scope.setCurrentMosaicsUniquesIndex = function(index) { $scope.current_mosaics_uniques_index = index; }
	$scope.setCurrentMosaicsMissionsIndex = function(index) { $scope.current_mosaics_missions_index = index; }

	/* Page loading */

	$scope.init = function(city, mosaics, waitings, potentials, mosaics_date_indexes, mosaics_name_indexes, mosaics_uniques_indexes, mosaics_missions_indexes) {

		$scope.city = city;
		
		$scope.mosaics = mosaics;
		$scope.waitings = waitings;
		$scope.potentials = potentials;
		
		$scope.mosaics_date_indexes = mosaics_date_indexes;
		$scope.mosaics_name_indexes = mosaics_name_indexes;
		$scope.mosaics_uniques_indexes = mosaics_uniques_indexes;
		$scope.mosaics_missions_indexes = mosaics_missions_indexes;

		for (var mosaic of $scope.mosaics) {
			
			var temp = 0;
			if (mosaic.mission_count > mosaic.column_count) {
				temp = mosaic.column_count - mosaic.mission_count % mosaic.column_count;
				if (temp < 0 || temp > (mosaic.column_count - 1)) temp = 0;
			}
			
			mosaic.offset = new Array(temp);
		}

		$scope.current_mosaics_date_index = $scope.mosaics_date_indexes[0];
		$scope.current_mosaics_name_index = $scope.mosaics_name_indexes[0];
		$scope.current_mosaics_uniques_index = $scope.mosaics_uniques_indexes[0];
		$scope.current_mosaics_missions_index = $scope.mosaics_missions_indexes[0];

		$scope.sortMosaicsByMissions();
		
		$scope.loaded = true;
		
		$scope.current_tab = 'mosaics';
		if ($scope.mosaics.length < 1) $scope.current_tab = 'waitings';
		if ($scope.waitings.length < 1) $scope.current_tab = 'potentials';
	}
});