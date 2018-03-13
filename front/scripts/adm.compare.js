angular.module('FrontModule.controllers').controller('AdmCompareCtrl', function($scope, API) {
    
	/* Page loading */
	API.sendRequest('/api/adm/compare/', 'POST').then(function(response) {
	    
	    $scope.countries = response.countries;
	    
		$scope.countries.sort(function(a, b) {
			
			if (a.diff > b.diff) return -1;
			if (a.diff < b.diff) return 1;
			
			if (a.name > b.name) return 1;
			if (a.name < b.name) return -1;
			
			return 0;
		});
	    
        $scope.loaded = true;
	});
});