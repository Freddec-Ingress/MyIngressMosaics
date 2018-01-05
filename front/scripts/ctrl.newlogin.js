angular.module('FrontModule.controllers').controller('NewLoginCtrl', function($scope, $window, $auth, $cookies, API) {
	
	/* Login management */
	
	$scope.socialLogin = function(provider, next) {
			
		$auth.authenticate(provider).then(function(response) {
			
			console.log(response.data.token);
			
			$auth.setToken(response.data.token);
			$cookies.token = response.data.token;
			
			$window.location.href = next;
		});
	}
	
	$scope.localLogin = function(username, password) {

		var data = { 'username':username, 'password':password }
		API.sendRequest('/api/user/login/', 'POST', {}, data).then(function(response) {
			
			$auth.setToken(response.token);
			$cookies.token = response.token;
			
			$window.location.href = '/';
			
		});
	}
	
	/* Page loading */
	
	$scope.loaded = true;
});