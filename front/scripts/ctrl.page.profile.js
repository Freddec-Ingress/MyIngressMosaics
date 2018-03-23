angular.module('FrontModule.controllers').controller('ProfilePageCtrl', function($scope, $window, $http, $auth, API, UserService) {
	
	$scope.signin = UserService.signin;

	$scope.authenticated = $auth.isAuthenticated();
    
	$('.hidden').each(function() { $(this).removeClass('hidden'); })
	
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

		$auth.removeToken();

		API.sendRequest('/api/user/logout/', 'POST').then(function(response) {
			
			$window.location.href = '/';
		});
	}
	
	/* Page loading */
	
	$scope.current_tab = 'mosaic';
	
	$scope.authenticated = $auth.isAuthenticated();
	
	API.sendRequest('/api/user/details/', 'POST').then(function(response) {
		
		$scope.name = response.name;
		$scope.faction = response.faction;
		$scope.picture = response.picture;
		$scope.superuser = response.superuser;
		$scope.mosaics = response.mosaics;
		$scope.missions = response.missions;
		$scope.like = response.like;
		$scope.todo = response.todo;
		$scope.complete = response.complete;
		$scope.notif = response.notif;
		
		$scope.loaded = true;
	});
});