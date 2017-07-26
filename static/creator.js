angular.module('CreatorApp.services', [])
angular.module('CreatorApp.directives', [])
angular.module('CreatortApp.controllers', [])

angular.module('CreatortApp.controllers').controller('CreatorCtrl', function($scope, $state, $stateParams, DataService) {
	
	$scope.creator_loading = true;

	$scope.creator_name = $stateParams.creator;
	
	DataService.loadMosaicsFromCreator($scope.creator_name).then(function(response) {
		
		$scope.creator_loading = false;
		
		$scope.faction = response.faction;
		$scope.mosaics = response.mosaics;
		
		DataService.sortByMissions('desc', $scope.mosaics);
	});

	/* Go to a mosaic page */
	
	$scope.go = function(item) {
		
		$state.go('root.mosaic', {'ref':item.ref});
	}
	
	/* Sort mosaics by missions */
	
	$scope.sortMissions = 'desc';
	
	$scope.sortMosaicsByMissions = function() {
		
		if ($scope.sortMissions == '' || $scope.sortMissions == 'asc') {
			
			DataService.sortMosaicsByMissions('desc');
			$scope.sortMissions = 'desc';
		}
		
		else if ($scope.sortMissions == 'desc') {
			
			DataService.sortMosaicsByMissions('asc');
			$scope.sortMissions = 'asc';
		}
	}
});
angular.module('CreatortApp', ['FrontModule',
						       'CreatortApp.services', 'CreatortApp.controllers', 'CreatortApp.directives',]);



/* Routing config */

angular.module('CreatortApp').config(function($urlRouterProvider, $stateProvider, $locationProvider) {
	
	$stateProvider
			.state('root.creator', { url: '/creator/:creator', templateUrl: '/static/pages/creator.html', data:{ title: 'creator_TITLE', }, })
});
