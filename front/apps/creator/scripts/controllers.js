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