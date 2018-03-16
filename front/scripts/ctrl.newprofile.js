angular.module('FrontModule.controllers').controller('NewProfileCtrl', function($scope, $window, $http, $cookies, $auth, API, UserService) {
	
	$scope.unotify = function(notif) {
		
		var index = $scope.notif.indexOf(notif);
		$scope.notif.splice(index, 1);
		
		var data = { 'country_name':notif.country_name, 'region_name':notif.region_name, 'city_name':notif.city_name }
		API.sendRequest('/api/notif/delete', 'POST', {}, data);
	}
	
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
	
	UserService.loadUser($scope.user);
	
	API.sendRequest('/api/user/details/', 'POST').then(function(response) {
		
		$scope.mosaics = response.mosaics;
		$scope.missions = response.missions;
		$scope.like = response.like;
		$scope.todo = response.todo;
		$scope.complete = response.complete;
		$scope.notif = response.notif;
		
		$scope.loaded = true;
	});
});