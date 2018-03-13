angular.module('FrontModule.controllers').controller('AdmCompareCtrl', function($scope, API) {
    
	/* Page loading */
	API.sendRequest('/api/adm/compare/', 'POST').then(function(response) {
	    
	    $scope.countries = response.countries;
	    
	    for (var country of $scope.countries) {
	    	
	    	country.open = false;
	    	country.diff = country.count - country.compare_count;
	    	
	    	for (var region of country.regions) {
	    		
		    	region.open = false;
		    	region.diff = region.count - region.compare_count;
		    	
		    	for (var city of region.cities) {
	    		
			    	city.open = false;
			    	city.diff = city.count - city.compare_count;
		    	}
		    	
				region.cities.sort(function(a, b) {
					
					if (a.diff > b.diff) return -1;
					if (a.diff < b.diff) return 1;
					
					if (a.name > b.name) return 1;
					if (a.name < b.name) return -1;
					
					return 0;
				});
	    	}
	    	
			country.regions.sort(function(a, b) {
				
				if (a.diff > b.diff) return -1;
				if (a.diff < b.diff) return 1;
				
				if (a.name > b.name) return 1;
				if (a.name < b.name) return -1;
				
				return 0;
			});
	    }
	    
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