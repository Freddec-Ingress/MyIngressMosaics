angular.module('FrontModule.controllers').controller('AdmPreviewsCtrl', function($scope, API) {
	
	/* Tab management */
	
	$scope.current_tab = '';
	
	/* Preview management */

    var to_generate = [];

	var generate = function() {
	    
	    if (to_generate.length < 1) return;
	    
		var data = { 'ref':to_generate[0].ref,  };
		API.sendRequest('/api/mosaic/preview/generate/', 'POST', {}, data).then(function(response) {
		    
		    to_generate.splice(0, 1);
		    generate();
		});
	}
	
	/* Cleaning management */
	
	$scope.cleaning_chekcing = false;
	$scope.to_be_cleaned = [];
	$scope.cleaning_regions = [];
	$scope.selected_country = null;
	$scope.selected_region = null;
	
	$scope.cleaningSelectCountry = function(id) {
	    
	    $scope.cleaning_regions = [];
	    
    	$scope.selected_country = null;
    	$scope.selected_region = null;
	
	    for (var country in $scope.countries) {
	        if (String(country.id) == String(id)) {
	            $scope.selected_country = country;
	            break;
	        }
	    }
	    
		var data = { 'country_id':$scope.selected_country.id, };
		API.sendRequest('/api/location/region/list/', 'POST', {}, data).then(function(response) {
		    
		    $scope.cleaning_regions = response.regions;
		});
	}
	
	$scope.cleaningSelectRegion = function(id) {
	    
    	$scope.selected_region = null;
	
	    for (var region in $scope.cleaning_regions) {
	        if (String(region.id) == String(id)) {
	            $scope.selected_region = region;
	            break;
	        }
	    }
	}
	
	$scope.checkCleaning = function() {
	    
	    $scope.cleaning_chekcing = true;
	    $scope.to_be_cleaned = [];
	    
		var data = { 'country_id':$scope.selected_country.id, 'region_id':$scope.selected_region.id, };
		API.sendRequest('/api/previews/cleaning/check/', 'POST', {}, data).then(function(response) {
			
    	    $scope.to_be_cleaned = response.mosaics;
    	    $scope.cleaning_chekcing = false;
		});
	}
	
	$scope.generateCleaning = function() {
	    
	    to_generate = $scope.to_be_cleaned;
	    generate();
	}
	
	/* Page loading */
	
	$scope.countries = []
	
	$scope.init = function(countries) {
		
    	$scope.current_tab = 'cleaning';
    	
    	$scope.countries = countries;
    	
		$scope.loaded = true;
	}
});