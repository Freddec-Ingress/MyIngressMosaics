angular.module('FrontModule.controllers').controller('CountryPageCtrl', function($scope, $window, API, $auth, UserService) {
	
	$scope.signin = UserService.signin;

	$scope.authenticated = $auth.isAuthenticated();
    
	$('.hidden').each(function() { $(this).removeClass('hidden'); })
	
	/* Notification management */

	$scope.notify = function() {
		
		if ($scope.authenticated) {
		
			$scope.country.notified = true;
			
			var data = { 'country_name':$scope.country.name }
			API.sendRequest('/api/notif/create/', 'POST', {}, data);
		}
		else {
			
			$scope.need_signin = true;
		}
	}
	
	$scope.unnotify = function() {
		
		$scope.country.notified = false;
		
		var data = { 'country_name':$scope.country.name }
		API.sendRequest('/api/notif/delete/', 'POST', {}, data);
	}
	
	/* Tab management */

	$scope.current_tab = 'regions';
	
	/* Regions sorting */
	
	$scope.sortRegionsByMosaics = function() {
		
		$scope.regions_sorting = 'by_mosaics';

		$scope.regions.sort(function(a, b) {
			
			if (a.mosaic_count > b.mosaic_count) return -1;
			if (a.mosaic_count < b.mosaic_count) return 1;
			
			if (a.name > b.name) return 1;
			if (a.name < b.name) return -1;
			
			return 0;
		});
	}
	
	$scope.sortRegionsByName = function() {
		
		$scope.regions_sorting = 'by_name';

		$scope.regions.sort(function(a, b) {
			
			if (a.name > b.name) return 1;
			if (a.name < b.name) return -1;
			
			return 0;
		});
	}
	
	/* Page loading */

	$scope.init = function(country, regions) {
		
		$scope.country = country;
		$scope.regions = regions;
		
		$scope.sortRegionsByMosaics();
    	
    	$scope.loaded = true;
	}
});