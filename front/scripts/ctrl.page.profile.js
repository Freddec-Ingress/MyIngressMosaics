angular.module('FrontModule.controllers').controller('ProfilePageCtrl', function($scope, $window, $http, $auth, API, UserService) {
	
	$scope.signin = UserService.signin;

	$scope.authenticated = $auth.isAuthenticated();
    
	$('.hidden').each(function() { $(this).removeClass('hidden'); })
	
	/* Notification management */
	
	$scope.unotify = function(notif) {
		
		var index = $scope.notif.indexOf(notif);
		$scope.notif.splice(index, 1);
		
		var data = { 'country_name':notif.country_name, 'region_name':notif.region_name, 'city_name':notif.city_name }
		API.sendRequest('/api/notif/delete/', 'POST', {}, data);
	}
	
	/* User management */
	
	$scope.edit = function(newFaction) {

		$scope.faction = newFaction;

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
	
	/* Tab management */
	
	$scope.current_tab = 'mosaics';
	
	/* Page loading */
	
	$scope.init = function(faction, likes, todos, notifs, mosaics, missions, completes) {
		
		$scope.faction = faction;
		
		$scope.likes = likes;
		$scope.todos = todos;
		$scope.notifs = notifs;
		$scope.mosaics = mosaics;
		$scope.missions = missions;
		$scope.completes = completes;
		
		$scope.loaded = true;
	}
});