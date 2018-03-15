angular.module('FrontModule.controllers').controller('NewCountryCtrl', function($scope, $window, API) {

	$scope.notify = function() {
		
		$scope.notified = true;
		
		var data = { 'country_name':$scope.country_name }
		API.sendRequest('/api/notif/create', 'POST', {}, data);
	}
	
	$scope.unnotify = function() {
		
		$scope.notified = false;
		
		var data = { 'country_name':$scope.country_name }
		API.sendRequest('/api/notif/delete', 'POST', {}, data);
	}

	$scope.init = function(country_name, notified) {
		
		$scope.country_name = country_name;
		$scope.notified = notified;
	}
});