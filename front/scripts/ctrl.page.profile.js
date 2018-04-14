angular.module('FrontModule.controllers').controller('ProfilePageCtrl', function($scope, $window, $http, $auth, API, UserService) {
	
	$scope.signin = UserService.signin;

	$scope.authenticated = $auth.isAuthenticated();
    
	$('.hidden').each(function() { $(this).removeClass('hidden'); })
	
	/* Notification management */
	
	$scope.unotify = function(notif) {
		
		var index = $scope.notifs.indexOf(notif);
		$scope.notifs.splice(index, 1);
		
		var data = { 'country_name':notif.country_name, 'region_name':notif.region_name, 'city_name':notif.city_name }
		API.sendRequest('/api/notif/delete/', 'POST', {}, data);
	}
	
	/* User management */
	
	$scope.edit = function(newFaction) {

		$scope.faction = newFaction;

		var data = { 'faction':newFaction };
		API.sendRequest('/api/user/edit/', 'POST', {}, data);
	}
	
	$scope.editAgentName = function(newAgentName) {

		$scope.agent_name = newAgentName;

		var data = { 'name':newAgentName };
		API.sendRequest('/api/user/editagentname/', 'POST', {}, data);
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
	
	$scope.init = function(faction, agent_name, likes, todos, notifs, mosaics, missions, completes) {
		
		$scope.faction = faction;
		$scope.agent_name = agent_name;
		
		$scope.likes = likes;
		$scope.todos = todos;
		$scope.notifs = notifs;
		$scope.mosaics = mosaics;
		$scope.missions = missions;
		$scope.completes = completes;
		
		for (var mosaic of $scope.likes) {
			
			var temp = 0;
			if (mosaic.mission_count > mosaic.column_count) {
				temp = mosaic.column_count - mosaic.mission_count % mosaic.column_count;
				if (temp < 0 || temp > (mosaic.column_count - 1)) temp = 0;
			}
			
			mosaic.offset = new Array(temp);
		}
		
		for (var mosaic of $scope.todos) {
			
			var temp = 0;
			if (mosaic.mission_count > mosaic.column_count) {
				temp = mosaic.column_count - mosaic.mission_count % mosaic.column_count;
				if (temp < 0 || temp > (mosaic.column_count - 1)) temp = 0;
			}
			
			mosaic.offset = new Array(temp);
		}
		
		for (var mosaic of $scope.mosaics) {
			
			var temp = 0;
			if (mosaic.mission_count > mosaic.column_count) {
				temp = mosaic.column_count - mosaic.mission_count % mosaic.column_count;
				if (temp < 0 || temp > (mosaic.column_count - 1)) temp = 0;
			}
			
			mosaic.offset = new Array(temp);
		}
		
		for (var mosaic of $scope.completes) {
			
			var temp = 0;
			if (mosaic.mission_count > mosaic.column_count) {
				temp = mosaic.column_count - mosaic.mission_count % mosaic.column_count;
				if (temp < 0 || temp > (mosaic.column_count - 1)) temp = 0;
			}
			
			mosaic.offset = new Array(temp);
		}
		
		$scope.loaded = true;
	}
});