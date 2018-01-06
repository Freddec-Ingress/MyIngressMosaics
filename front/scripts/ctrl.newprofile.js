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
	
	$scope.current_tab = 'mosaic';
	
	API.sendRequest('/api/user/details/', 'POST').then(function(response) {
		
		$scope.mosaics = response.mosaics;
		$scope.missions = response.missions;
		
		$scope.loaded = true;
	});
});