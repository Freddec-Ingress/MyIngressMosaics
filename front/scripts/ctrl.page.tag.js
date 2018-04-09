angular.module('FrontModule.controllers').controller('TagPageCtrl', function($scope, $window, API) {
	
	/* Page loading */
	
	$scope.init = function(mosaics) {
	
		$scope.mosaics_sorting ='by_date';
	
		$scope.mosaics_by_date = mosaics;
		$scope.mosaics_by_missions = mosaics;
		
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
		
		$scope.loaded = true;
	}
});