angular.module('FrontModule.controllers').controller('AdmRegionCtrl', function($scope, API) {
	
	/* Country management */
	
	var selected_country_id = null;
	
	$scope.selectCountry = function(country_id) {
	    
	    selected_country_id = country_id;
	    
        $scope.regions = [];
        
        var data = { 'country_id':country_id };
        API.sendRequest('/api/region/list/', 'POST', {}, data).then(function(response) {
            
            $scope.regions = response.regions;
        });
	}
	
	$scope.refreshCountry = function() {
	    
	    $scope.selectCountry(selected_country_id);
	}
	
	/* Region management */
	
	$scope.createRegion = function(country_id, name, locale) {
	    
        var data = { 'country_id':country_id, 'name':name, 'locale':locale };
        API.sendRequest('/api/region/create/', 'POST', {}, data).then(function(response) {
            
            $scope.refreshCountry();
        });
	}
	
	$scope.mergeRegions = function(src_id, dest_id) {
	    
        var data = { 'src_id':src_id, 'dest_id':dest_id };
        API.sendRequest('/api/region/move/', 'POST', {}, data).then(function(response) {
            
            $scope.refreshCountry();
        });
	}
	
	$scope.updateRegion = function(region_id, new_name, new_locale) {
	    
        var data = { 'id':region_id, 'new_name':new_name, 'new_locale':new_locale };
        API.sendRequest('/api/region/update/', 'POST', {}, data).then(function(response) {
            
            $scope.refreshCountry();
        });
	}
	
	$scope.deleteRegion = function(region_id) {
	    
        var data = { 'id':region_id };
        API.sendRequest('/api/region/delete/', 'POST', {}, data).then(function(response) {
            
            $scope.refreshCountry();
        });
	}
	
	/* Page loading */
	
	$scope.current_tab = 'mosaics';
	
	API.sendRequest('/api/country/list/', 'POST').then(function(response) {
    
        $scope.countries = response.countries;
        
    	$scope.loaded = true;
	});
});