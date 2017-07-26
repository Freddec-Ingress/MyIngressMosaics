angular.module('HomeApp.controllers', [])

angular.module('HomeApp.controllers').controller('HomeCtrl', function($scope, DataService) {
	
	$scope.latest_loading = true;
	
	DataService.loadLatest().then(function(response) {
		
		$scope.latest_loading = false;
		
		$scope.mosaics = response;
	});
});

