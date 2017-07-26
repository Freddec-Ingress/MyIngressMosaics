angular.module('CreatortApp', ['FrontModule',
						       'CreatortApp.services', 'CreatortApp.controllers', 'CreatortApp.directives',]);



/* Routing config */

angular.module('CreatortApp').config(function($urlRouterProvider, $stateProvider, $locationProvider) {
	
	$stateProvider
			.state('root.creator', { url: '/creator/:creator', templateUrl: '/static/pages/creator.html', data:{ title: 'creator_TITLE', }, })
});
