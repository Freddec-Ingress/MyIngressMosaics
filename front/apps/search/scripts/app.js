angular.module('SearchApp', ['FrontModule',
						     'SearchApp.services', 'SearchApp.controllers', 'SearchApp.directives',]);



/* Routing config */

angular.module('SearchApp').config(function($urlRouterProvider, $stateProvider, $locationProvider) {
	
	$stateProvider
			.state('root.search', { url: '/search', templateUrl: '/static/pages/search.html', data:{ title: 'search_TITLE', }, })
});
