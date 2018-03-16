angular.module('FrontModule.controllers').controller('AdmCompareCtrl', function($scope, API) {
    
	/* Page loading */
	API.sendRequest('/api/adm/compare/', 'POST').then(function(response) {
	    
	    $scope.countries = response.countries;
	    
	    for (var country of $scope.countries) {
	    	
	    	country.displayed = false;
	    	country.open = true;
	    	country.diff = country.compare_count - country.count;
	    	
	    	for (var region of country.regions) {
	    		
	    		region.displayed = false;
		    	region.open = true;
		    	region.diff = region.compare_count - region.count;
		    	
		    	if (region.mosaics.length > 0) {
		    		
		    		country.displayed = true;
		    		region.displayed = true;
		    	}
		    	
				region.mosaics.sort(function(a, b) {
					
					if (a.city_name > b.city_name) return 1;
					if (a.city_name < b.city_name) return -1;
					
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