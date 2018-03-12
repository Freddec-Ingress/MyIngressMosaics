angular.module('FrontModule.controllers').controller('NewCountryCtrl', function($scope, $window, API) {
	
	/* Notification management */
	
	$scope.notify = function() {
		
		$scope.notified = true;
		
		var data = { 'country_name':$scope.country.name }
		API.sendRequest('/api/notif/create', 'POST', {}, data);
	}
	
	$scope.unnotify = function() {
		
		$scope.notified = false;
		
		var data = { 'country_name':$scope.country.name }
		API.sendRequest('/api/notif/delete', 'POST', {}, data);
	}
	
	/* Page loading */
	
	$scope.loadCountry = function(name) {
		
		API.sendRequest('/api/country/' + name + '/', 'GET').then(function(response) {
			
			$scope.count = response.count;
			$scope.country = response.country;
			$scope.notified = response.notified;
			
			$scope.regions = response.regions;
			$scope.regions.sort(function(a, b) {
				return b.mosaics - a.mosaics;
			});
			
			$scope.loaded = true;
		});
	}
});