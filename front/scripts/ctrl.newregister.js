angular.module('FrontModule.controllers').controller('NewRegisterCtrl', function($scope, $window, $auth, $cookies, API) {
	
	$scope.register = function(username, password1, password2, email) {

		var data = { 'username':username, 'password1':password1, 'password2':password2, 'email':email }
		API.sendRequest('/api/user/register/', 'POST', {}, data).then(function(response) {
			
			$auth.setToken(response.token);
			$cookies.token = response.token;

			$window.location.href = '/';
			
		});
	}
	
	/* Page loading */
	
	$scope.loaded = true;
});