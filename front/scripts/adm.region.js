angular.module('FrontModule.controllers').controller('AdmRegionCtrl', function($scope, API) {

	/* Region management */
	
	$scope.regions = [];
	
	$scope.merge = function(src_region_id, dst_region_id) {
		
		var data = { 'src_region_id':src_region_id, 'dst_region_id':dst_region_id, };
		API.sendRequest('/api/location/region/merge/', 'POST', {}, data).then(function(response) {
			
			var index = 0;
			for (var region of $scope.regions) {
				
				if (region.id == src_region_id) break;
				index += 1;
			}
			
			$scope.regions.splice(index, 1);
		});
	}

	/* Country management */

	$scope.countries = [];
	
	$scope.changeCurrentCountry = function(id) {
		
		$scope.regions = [];
		
		$scope.country_changing = true;
		
		var data = { 'country_id':id, };
		API.sendRequest('/api/location/region/list/', 'POST', {}, data).then(function(response) {

			$scope.regions = response.regions;

			$scope.country_changing = false;
		});
	}
	
	/* Page loading */
	
	API.sendRequest('/api/location/country/list/', 'POST', {}, null).then(function(response) {
	
		$scope.countries = response.countries;
	
		$scope.loaded = true;
	});
});