angular.module('AccountApp', ['FrontModule',
						      'AccountApp.services', 'AccountApp.controllers', 'AccountApp.directives',]);



/* Routing config */

angular.module('AccountApp').config(function($urlRouterProvider, $stateProvider, $locationProvider) {
	
	$stateProvider
			.state('root.login', { url: '/account/login', controller: 'LoginCtrl', templateUrl: '/static/pages/login.html', data:{ title: 'login_TITLE', }})
			.state('root.profile', { url: '/account/profile', controller: 'ProfileCtrl', templateUrl: '/static/pages/profile.html', data:{ title: 'profile_TITLE', }})
			.state('root.register', { url: '/account/register', controller: 'RegisterCtrl', templateUrl: '/static/pages/register.html', data:{ title: 'register_TITLE', }})
});
