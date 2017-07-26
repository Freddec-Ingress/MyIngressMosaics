angular.module('FrontModule.controllers', [])

angular.module('FrontModule.controllers').controller('RootCtrl', function($rootScope, $scope, $stateParams, $translate, $window, UserService) {
	
	var supported_lang = ['en', 'fr'];
	
	var user_lang = 'en';
	
	var lang = $window.navigator.language || $window.navigator.userLanguage;
	if (supported_lang.indexOf(lang) != -1) user_lang = lang;
	
  	$translate.use(user_lang);

	$scope.user = UserService.data;
	
	$scope.logout = UserService.logout;
	
	$rootScope.menu_open = false;
	
	$scope.openMenu = function() {
		$rootScope.menu_open = true;
	}
	
	$scope.closeMenu = function() {
		$rootScope.menu_open = false;
	}
	
	$scope.changeLang = function(lang) {
		$translate.use(lang);
	}
});