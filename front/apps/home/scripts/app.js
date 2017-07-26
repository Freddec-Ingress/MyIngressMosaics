angular.module('HomeApp', ['FrontModule',
						   'HomeApp.services', 'HomeApp.controllers', 'HomeApp.directives',]);



/* Routing config */

angular.module('HomeApp').config(function($urlRouterProvider, $stateProvider, $locationProvider) {
	
	$stateProvider
			.state('root.home', { url: '/', templateUrl: '/static/pages/home.html', data: { title: 'home_TITLE', }, })
});
