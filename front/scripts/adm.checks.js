angular.module('FrontModule.controllers').controller('AdmChecksCtrl', function($scope, API) {
	
	/* Tab management */
	
	$scope.current_tab = 'misc';
	
	/* Preview management */
	
	$scope.preview_generation = false;
	
	$scope.startPreviewGeneration = function() {
		
		console.log('startPreviewGeneration');
		
		$scope.preview_generation = true;
		generatePreview();
	}
	
	function generatePreview() {
		
		console.log('generatePreview');
		
		if ($scope.refs_without_preview.length < 1) {
			
			$scope.preview_generation = false;
			return
		}
		
		var ref = $scope.refs_without_preview[0];
		
		var data = { 'ref':ref };
		API.sendRequest('/api/mosaic/preview/generate/', 'POST', {}, data).then(function() {
			
			$scope.refs_without_preview.splice(0, 1);
			generatePreview();
		});
	}
	
	/* Page loading */
	
	$scope.refs_without_preview = [];
	
	$scope.init = function(refs_without_preview) {
		
		console.log('init');
		
		$scope.refs_without_preview = refs_without_preview;
		
		$scope.loaded = true;
	}
});