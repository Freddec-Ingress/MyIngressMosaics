angular.module('FrontModule.controllers').controller('AdmChecksCtrl', function($scope, API) {
	
	/* Preview management */
	
	$scope.preview_generating = false;
	
	$scope.preview_total_count = 0;
	$scope.preview_current_count = 0;
	
	var refs = null;
	
	var previewCall = function() {
		
		var ref = refs[$scope.preview_current_count];
		API.sendRequest('/api/mosaic/generate/', 'POST', {}, { 'ref':ref }).then(function(response) {
			
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
		
		API.sendRequest('/api/mosaic/getall/', 'POST', {}, null).then(function(response) {
			
			refs = response.refs;
			
			$scope.preview_generating = true;
			$scope.preview_total_count = refs.length;
			
			previewCall();
		});
	}
	
	/* Tab management */
	
	$scope.current_tab = 'region';
	
	/* Page loading */
	
	$scope.loaded = true;
});