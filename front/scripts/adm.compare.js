angular.module('FrontModule.controllers').controller('AdmCompareCtrl', function($scope, API) {
    
	/* Page loading */
	
	$scope.init = function(cities) {
		
		$scope.cities = cities;
		
		$scope.cities.sort(function(a, b) {
			
			if (a.notregistered_count > b.notregistered_count) return -1;
			if (a.notregistered_count < b.notregistered_count) return 1;
			
			if (a.name > b.name) return 1;
			if (a.name < b.name) return -1;
			
			return 0;
		});
		
        $scope.loaded = true;
	};
});