angular.module('FrontModule.controllers').controller('AdmCompareCtrl', function($scope, API) {
    
	/* Page loading */
	
	$scope.init = function(cities) {
		
		$scope.cities = cities;
		
        $scope.loaded = true;
	};
});