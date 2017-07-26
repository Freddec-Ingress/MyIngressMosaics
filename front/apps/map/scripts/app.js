angular.module('MapApp', ['FrontModule',
						  'MapApp.services', 'MapApp.controllers', 'MapApp.directives',]);



/* Routing config */

angular.module('MapApp').config(function($urlRouterProvider, $stateProvider, $locationProvider) {
	
	$stateProvider
			.state('root.map', { url: '/map', templateUrl: '/static/pages/map.html', data:{ title: 'map_TITLE', }, })
});
