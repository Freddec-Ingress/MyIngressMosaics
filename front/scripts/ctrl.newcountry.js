angular.module('FrontModule.controllers').controller('NewCountryCtrl', function($rootScope, $scope, $window, API) {

	$scope.notify = function() {
		
		if ($rootScope.user.name) {
		
			$scope.notified = true;
			
			var data = { 'country_name':$scope.country_name }
			API.sendRequest('/api/notif/create', 'POST', {}, data);
		}
		else {
			$scope.need_signin = true;
		}
	}
	
	$scope.unnotify = function() {
		
		$scope.notified = false;
		
		var data = { 'country_name':$scope.country_name }
		API.sendRequest('/api/notif/delete', 'POST', {}, data);
	}

	$scope.init = function(country_name, notified) {
		
		$scope.country_name = country_name;
		
		if (notified=='False') $scope.notified = false;
		if (notified=='True') $scope.notified = true;
		
		$scope.need_signin = false;
    
	    $('.hidden').each(function() { $(this).removeClass('hidden'); })
	}
});