angular.module('FrontModule.controllers').controller('TagPageCtrl', function($scope, $window, API) {
	
	/* Page loading */
	
	$scope.init = function(mosaics) {
	
		$scope.mosaics_sorting ='by_date';
	
		$scope.mosaics_by_date = mosaics.slice();
		$scope.mosaics_by_missions = mosaics.slice();
		
		$scope.mosaics_by_date.sort(function(a, b) {
			
			if (a.id > b.id) return -1;
			if (a.id < b.id) return 1;
			
			return 0;
		});
		
		$scope.mosaics_by_missions.sort(function(a, b) {
			
			if (a.mission_count > b.mission_count) return -1;
			if (a.mission_count < b.mission_count) return 1;
			
			if (a.title > b.title) return 1;
			if (a.title < b.title) return -1;
			
			return 0;
		});
		
		var country_code_array = [];
		
		$scope.indexes_by_country = []
		for (var mosaic of $scope.mosaics_by_date) {
			
			var country_code = mosaic.country_code;
			
			var index = country_code_array.indexOf(country_code);
			
			var index_by_country = null;
			
			if (index == -1) {
				
				index_by_country = {
					
					'code':mosaic.country_code,
					'name':mosaic.country_name,
					
					'mosaics':[],
				}
				
				country_code_array.push(country_code);
				$scope.indexes_by_country.push(index_by_country);
			}
			else {
				
				index_by_country = $scope.indexes_by_country[index]
			}
			
			index_by_country.mosaics.push(mosaic);
		}
		
		$scope.current_by_country_index = $scope.indexes_by_country[0];
		$scope.mosaics_by_country = $scope.current_by_country_index.mosaics;
		
		$scope.loaded = true;
	}
});