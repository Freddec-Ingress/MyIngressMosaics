angular.module('FrontModule.controllers').controller('NewProfileCtrl', function($scope, $window, $http, $cookies, $auth, API) {
	
	/* User management */
	
	$scope.edit = function(newName, newFaction) {

		var data = { 'name':newName, 'faction':newFaction };
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
	
	/* Tab management */
	
	$scope.current_tab = 0;
	
	$scope.open_tab = function(id) {
		
		$scope.current_tab = id;
	}
	
	/* Page loading */
	
	API.sendRequest('/api/user/details/', 'POST').then(function(response) {
	
	    $scope.loved = response.loved;
	    $scope.completed = response.completed;
	    
		$scope.open_tab(1);
		
		$scope.loaded = true;
	});
});