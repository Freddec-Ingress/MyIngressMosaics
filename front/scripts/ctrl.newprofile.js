angular.module('FrontModule.controllers').controller('NewProfileCtrl', function($scope, $window, $http, $cookies, $auth, API) {
	
	/* User management */
	
	$scope.edit = function(newFaction) {

		var data = { 'faction':newFaction };
		API.sendRequest('/api/user/edit/', 'POST', {}, data);
	}
	
	$scope.logout = function() {
	    
		delete $http.defaults.headers.common.Authorization;
    	delete $cookies.token;
		
		$auth.removeToken();

		API.sendRequest('/api/user/logout/', 'POST').then(function(response) {
			
			$window.location.href = '/';
		});
	}
	
	/* Page loading */
	
	$scope.loaded = true;
});