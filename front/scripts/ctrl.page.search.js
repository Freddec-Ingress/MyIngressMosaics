angular.module('FrontModule.controllers').controller('SearchPageCtrl', function($scope, $window, API) {
	
	/* Search management */
	
	$scope.mosaics = null;
	$scope.waitings = null;
	$scope.potentials = null;
	$scope.missions = null;
	
	$scope.searching = false;

	$scope.search = function(text) {
		
		if (!text) return;
		
		if (text.length < 3) return;
		
		$scope.searching = true;
		
		$scope.mosaics = null;
		$scope.waitings = null;
		$scope.potentials = null;
		$scope.missions = null;
		
		var data = { 'text':text };
		API.sendRequest('/api/search/', 'POST', {}, data).then(function(response) {
			
			$scope.mosaics = response.mosaics;
			
			$scope.mosaics.sort(function(a, b) {
				
				if (a.mission_count > b.mission_count) return -1;
				if (a.mission_count < b.mission_count) return 1;
				
				return 0;
			});
			
			for (var mosaic of $scope.mosaics) {
				
				var temp = 0;
				if (mosaic.mission_count > mosaic.column_count) {
					temp = mosaic.column_count - mosaic.mission_count % mosaic.column_count;
					if (temp < 0 || temp > (mosaic.column_count - 1)) temp = 0;
				}
				
				mosaic.offset = new Array(temp);
			}

			$scope.waitings = response.waitings;
			
			$scope.waitings.sort(function(a, b) {
				
				if (a.mission_count > b.mission_count) return -1;
				if (a.mission_count < b.mission_count) return 1;
				
				return 0;
			});
			
			$scope.potentials = response.potentials;

			$scope.potentials.sort(function(a, b) {
				
				if (a.count > b.count) return -1;
				if (a.count < b.count) return 1;
				
				return 0;
			});
			
			$scope.missions = response.missions;
			
			$scope.missions.sort(function(a, b) {
				
				if (a.title > b.title) return 1;
				if (a.title < b.title) return -1;
				
				return 0;
			});
			
			$scope.current_tab = 'mosaic';
			if ($scope.mosaics.length < 1) {
				$scope.current_tab = 'potential';
				if ($scope.potentials.length < 1) {
					$scope.current_tab = 'mission';
					if ($scope.missions.length < 1) {
						$scope.current_tab = 'mosaic';
					}
				}
			}
			
			$scope.searching = false;
		});
	}
	
	/* Page loading */
	
	$scope.current_tab = 'mosaic';
	
	$scope.init = function(text, tags) {
	
		$scope.tags = tags;
	
		$scope.search(text);

		$scope.loaded = true;
	}
});