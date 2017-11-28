angular.module('FrontModule.controllers').controller('AdmRegionCtrl', function($scope, API) {
	
	/* Country management */
	
	$scope.selectCountry = function(country_id) {
	    
        $scope.regions = [];
        
        var data = { 'country_id':country_id };
        API.sendRequest('/api/region/list/', 'POST', {}, data).then(function(response) {
            
            $scope.regions = response.regions;
        });
	}
	
	/* Region management */
	
	$scope.mergeRegions = function(src_id, dest_id) {
	    
        var data = { 'src_id':src_id, 'dest_id':dest_id };
        API.sendRequest('/api/region/move/', 'POST', {}, data).then(function(response) {
        });
	}
	
	$scope.updateRegion = function(region_id, new_name, new_locale) {
	    
        var data = { 'id':region_id, 'new_name':new_name, 'new_locale':new_locale };
        API.sendRequest('/api/region/update/', 'POST', {}, data).then(function(response) {
        });
	}
	
	/* Page loading */
	
	API.sendRequest('/api/country/list/', 'POST').then(function(response) {
    
        $scope.countries = response.countries;
        
    	$scope.loaded = true;
	});
});