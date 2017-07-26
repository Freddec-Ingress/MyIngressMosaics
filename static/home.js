angular.module('HomeApp.services', [])

angular.module('HomeApp.directives', [])

angular.module('HomeApp.controllers', [])

angular.module('HomeApp.controllers').controller('HomeCtrl', function($scope, DataService) {
	
	$scope.latest_loading = true;
	
	DataService.loadLatest().then(function(response) {
		
		$scope.latest_loading = false;
		
		$scope.mosaics = response;
	});
});


angular.module('HomeApp', ['FrontModule',
						   'HomeApp.services', 'HomeApp.controllers', 'HomeApp.directives',]);



/* Routing config */

angular.module('HomeApp').config(function($urlRouterProvider, $stateProvider, $locationProvider) {
	
	$stateProvider
			.state('root.home', { url: '/', templateUrl: '/static/pages/home.html', data: { title: 'home_TITLE', }, })
});
