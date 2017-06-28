angular.module('AngularApp', ['ui.router', 'ui.bootstrap', 'pascalprecht.translate', 'satellizer', 'ngCookies', 'toastr',
							  'AngularApp.services', 'AngularApp.controllers', 'AngularApp.directives', ]);



/* Routing config */

angular.module('AngularApp').config(function($urlRouterProvider, $stateProvider, $locationProvider) {
	
	$urlRouterProvider.otherwise('/');
	
	$stateProvider
	
		.state('root', { url: '/:codelang', controller: 'RootCtrl', templateUrl: '/static/front/pages/root.html', resolve: {loadUser: function(UserService) { return UserService.init(); }, }, })

			.state('root.home', { url: '/home', controller: 'HomeCtrl', templateUrl: '/static/front/pages/home.html', data: { title: 'home_TITLE', }})

			.state('root.login', { url: '/login', controller: 'LoginCtrl', templateUrl: '/static/front/pages/login.html', data:{ title: 'login_TITLE', }})
			.state('root.profile', { url: '/profile', controller: 'ProfileCtrl', templateUrl: '/static/front/pages/profile.html', data:{ title: 'profile_TITLE', }})
			.state('root.register', { url: '/register', controller: 'RegisterCtrl', templateUrl: '/static/front/pages/register.html', data:{ title: 'register_TITLE', }})

			.state('root.missions', { url: '/missions', controller: 'MissionsCtrl', templateUrl: '/static/front/pages/missions.html', data:{ title: 'missions_TITLE', }, resolve: {loadMissions: function(UserService) { return UserService.getMissions(); }, }, })
			.state('root.create', { url: '/create', controller: 'CreateCtrl', templateUrl: '/static/front/pages/create.html', data:{ title: 'create_TITLE', }, })
			
	$locationProvider.html5Mode(true);
});



/* Translations config */

angular.module('AngularApp').config(function($translateProvider) {
	
	$translateProvider.useSanitizeValueStrategy(null);
	
	$translateProvider.preferredLanguage('en');
	
	$translateProvider.translations('en', en_translations);
	$translateProvider.translations('fr', fr_translations);
});



/* Satellizer config */

angular.module('AngularApp').config(function($authProvider) {
	
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

angular.module('AngularApp').config(function(toastrConfig) {
	
	angular.extend(toastrConfig, {
		
		target: '#toast-content',
		timeOut: 50000,
	});
});



/* Running */

angular.module('AngularApp').run(function($rootScope, $state, $stateParams) {
	
	$rootScope.state = $state;
	$rootScope.stateParams = $stateParams;
	
	$rootScope.$on('$stateChangeStart', function(event, toState, toParams, fromState, fromParams) {
		$rootScope.route_loading = true;
	});
	
	$rootScope.$on('$stateChangeSuccess', function(event, toState, toParams, fromState, fromParams) {
		$rootScope.route_loading = false;
	});
});
