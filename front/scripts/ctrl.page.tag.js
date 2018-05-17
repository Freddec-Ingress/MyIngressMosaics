angular.module('FrontModule.controllers').controller('TagPageCtrl', function($scope, $window, API) {
	
	/* Index management */
	
	$scope.indexes_by_country = []
	$scope.mosaics_by_country = null;
	$scope.current_by_country_index = null;
	
	$scope.setByCountryIndex = function(index) {
		
		$scope.mosaics_by_country = index.mosaics;
		$scope.current_by_country_index = index;
	}
	
	/*----------*/
	
	$scope.indexes_by_mission = []
	$scope.mosaics_by_mission = null;
	$scope.current_by_mission_index = null;
	
	$scope.setByMissionIndex = function(index) {
		
		$scope.mosaics_by_mission = index.mosaics;
		$scope.current_by_mission_index = index;
	}
	
	/* Page loading */
	
	$scope.init = function(mosaics) {
	
		$scope.indexes_by_country = []
		var country_code_array = [];
		
		$scope.indexes_by_mission = []
		var mission_count_array = [];
		
		for (var mosaic of mosaics) {
			
			var index_by_country = null;
			
			var country_code = mosaic.country_code;
			var index = country_code_array.indexOf(country_code);
			if (index == -1) {
				
				index_by_country = {
					
					'code':mosaic.country_code,
					'name':mosaic.country_code.toUpperCase(),
					
					'mosaics':[],
				}
				
				country_code_array.push(country_code);
				$scope.indexes_by_country.push(index_by_country);
			}
			else {
				
				index_by_country = $scope.indexes_by_country[index]
			}
			
			index_by_country.mosaics.push(mosaic);
			
			/*----------*/
			
			var index_by_mission = null;
			
			var mission_count = mosaic.mission_count;
			var index = mission_count_array.indexOf(mission_count);
			if (index == -1) {
				
				index_by_mission = {
					
					'count':mosaic.mission_count,

					'mosaics':[],
				}
				
				mission_count_array.push(mission_count);
				$scope.indexes_by_mission.push(index_by_mission);
			}
			else {
				
				index_by_mission = $scope.indexes_by_mission[index]
			}
			
			index_by_mission.mosaics.push(mosaic);
		}
		
		$scope.indexes_by_country.sort(function(a, b) {

			if (a.name > b.name) return 1;
			if (a.name < b.name) return -1;
			
			return 0;
		});

		for (var index of $scope.indexes_by_country) {
			
			index.mosaics.sort(function(a, b) {
	
				if (a.city_name > b.city_name) return 1;
				if (a.city_name < b.city_name) return -1;
					
				if (a.name > b.name) return 1;
				if (a.name < b.name) return -1;
				
				return 0;
			});
		}

		$scope.current_by_country_index = $scope.indexes_by_country[0];
		$scope.mosaics_by_country = $scope.current_by_country_index.mosaics;
		
		/*----------*/
		
		$scope.indexes_by_mission.sort(function(a, b) {

			if (a.count > b.count) return 1;
			if (a.count < b.count) return -1;
			
			return 0;
		});

		for (var index of $scope.indexes_by_mission) {
			
			index.mosaics.sort(function(a, b) {
	
				if (a.name > b.name) return 1;
				if (a.name < b.name) return -1;
				
				return 0;
			});
		}

		$scope.current_by_mission_index = $scope.indexes_by_mission[0];
		$scope.mosaics_by_mission = $scope.current_by_mission_index.mosaics;
		
		$scope.mosaics_sorting = 'by_country';
		
		$scope.loaded = true;
	}
});