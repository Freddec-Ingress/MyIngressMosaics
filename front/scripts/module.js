angular.module('FrontModule', ['ui.router', 'ui.bootstrap', 'pascalprecht.translate', 'satellizer', 'ngCookies', 'toastr',
							   'FrontModule.services', 'FrontModule.controllers', 'FrontModule.directives', ]);



/* Routing config */

angular.module('FrontModule').config(function($urlRouterProvider, $stateProvider, $locationProvider) {
	
	$stateProvider
	
		.state('root', { templateUrl: '/static/pages/root.html', controller: 'RootCtrl', resolve: {loadUser: function(UserService) { return UserService.init(); }, }, })

		
	$locationProvider.html5Mode(true);
});



/* Translations config */

angular.module('FrontModule').config(function($translateProvider) {
	
	$translateProvider.useSanitizeValueStrategy(null);
	
	$translateProvider.preferredLanguage('en');
	
	$translateProvider.translations('en', en_translations);
	$translateProvider.translations('fr', fr_translations);
});



/* Satellizer config */

angular.module('FrontModule').config(function($authProvider) {
	
	$authProvider.facebook({
		
		url: '/login/social/token_user/facebook',
		clientId: '237811833398918'
	});

	$authProvider.google({
		
		url: '/login/social/token_user/google-oauth2',
		clientId: '949801101013-ss1st02gn04q6oisp1chpp35l8m4itbm.apps.googleusercontent.com'
  });

	$authProvider.authToken = 'Token';
	$authProvider.tokenType = 'Token';
});



/* Toastr config */

angular.module('FrontModule').config(function(toastrConfig) {
	
	angular.extend(toastrConfig, {
		
		target: '#toast-content',
		timeOut: 10000,
		preventDuplicates: true,
    	preventOpenDuplicates: true,
	});
});



/* Running */

angular.module('FrontModule').run(function($rootScope, $state, $stateParams) {
	
	$rootScope.state = $state;
	$rootScope.stateParams = $stateParams;
	
	$rootScope.$on('$stateChangeStart', function(event, toState, toParams, fromState, fromParams) {
		$rootScope.route_loading = true;
	});
	
	$rootScope.$on('$stateChangeSuccess', function(event, toState, toParams, fromState, fromParams) {
		
		$rootScope.route_loading = false;
	});
});



/* Filter */

angular.module('FrontModule').filter('reverse', function() {
	
	return function(items) {
		return items.slice().reverse();
	};
});