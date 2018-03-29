angular.module('FrontModule.controllers').controller('AdmChecksCtrl', function($scope, API) {
	
	/* Preview management */
	
	$scope.preview_generating = false;
	
	$scope.preview_total_count = 0;
	$scope.preview_current_count = 0;
	
	var previewCall = function() {
		
		API.sendRequest('/api/mosaic/generate/', 'GET').then(function(response) {
			
			$scope.preview_current_count += 1;
			
			if ($scope.preview_current_count < $scope.preview_total_count) {
				previewCall();
			}
			else {
				$scope.preview_generating = false;
			}
			
		}, function(response) {
			
			$scope.preview_current_count += 1;
			
			if ($scope.preview_current_count < $scope.preview_total_count) {
				previewCall();
			}
			else {
				$scope.preview_generating = false;
			}
		});
	}
	
	$scope.generatePreviews = function() {
		
		$scope.preview_total_count = 0;
		$scope.preview_current_count = 0;
		
		previewCall();
	}
	
	/* Tab management */
	
	$scope.current_tab = 'region';
	
	/* Page loading */
	
	$scope.loaded = true;
});