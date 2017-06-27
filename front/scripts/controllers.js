angular.module('AngularApp.controllers', [])

angular.module('AngularApp.controllers').controller('RootCtrl', function($scope, $stateParams, $translate, $window, UserService) {
	
	var supported_lang = ['en', 'fr'];
	
	var user_lang = 'en';
	
	if ($stateParams.codelang) {
		
		if (supported_lang.indexOf($stateParams.codelang) != -1) user_lang = $stateParams.codelang;
      	$translate.use(user_lang);
	}
	else {
		
		var lang = $window.navigator.language || $window.navigator.userLanguage;
		if (supported_lang.indexOf(lang) != -1) user_lang = lang;
		
    	$window.location.href = '/' + user_lang + '/home';
	}
	
	$scope.user = UserService.data;
	
	$scope.logout = UserService.logout;
});

angular.module('AngularApp.controllers').controller('HomeCtrl', function($scope) {
});

angular.module('AngularApp.controllers').controller('LoginCtrl', function($scope, UserService) {
	
	$scope.loginModel = { username:null, password:null };
	
	$scope.localLogin = UserService.localLogin;
	$scope.socialLogin = UserService.socialLogin;
});

angular.module('AngularApp.controllers').controller('RegisterCtrl', function($scope, UserService) {
	
	$scope.registerModel = { username:null, password1:null, password2:null, email:null };
	
	$scope.register = UserService.register;
});