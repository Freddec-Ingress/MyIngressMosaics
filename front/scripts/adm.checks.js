angular.module('FrontModule.controllers').controller('AdmChecksCtrl', function($scope, API) {
	
	/* Tab management */
	
	$scope.current_tab = 'mosaic';
	
	/* Tag management */
	
	$scope.addTag = function(mosaic, tag) {
		
		var data = { 'ref':mosaic.ref, 'tag':tag };
		API.sendRequest('/api/mosaic/tag/add/', 'POST', {}, data).then(function() {
			
			var index = $scope.mosaics_to_tag.indexOf(mosaic);
			$scope.mosaics_to_tag.splice(index, 1);
		});
	}
	
	$scope.exitTag = function(mosaic) {
		
		var index = $scope.mosaics_to_tag.indexOf(mosaic);
		$scope.mosaics_to_tag.splice(index, 1);
	}
	
	/* Preview management */
	
	$scope.preview_generation = false;
	
	$scope.startPreviewGeneration = function() {

		$scope.preview_generation = true;
		generatePreview();
	}
	
	function generatePreview() {

		if ($scope.refs_without_preview.length < 1) {
			
			$scope.preview_generation = false;
			return
		}
		
		var ref = $scope.refs_without_preview[0];
		
		var data = { 'ref':ref };
		API.sendRequest('/api/mosaic/preview/generate/', 'POST', {}, data).then(function() {
			
			$scope.refs_without_preview.splice(0, 1);
			generatePreview();
			
		}, function() {
			
			$scope.refs_without_preview.splice(0, 1);
			generatePreview();
		});
	}
	
	/* Computing management */
	
	$scope.computing = false;
	
	$scope.startComputing = function() {

		$scope.computing = true;
		compute();
	}
	
	function compute() {

		if ($scope.refs_without_mission_count.length < 1) {
			
			$scope.computing = false;
			return
		}
		
		var ref = $scope.refs_without_mission_count[0];
		
		var data = { 'ref':ref };
		API.sendRequest('/api/mosaic/compute/', 'POST', {}, data).then(function() {
			
			$scope.refs_without_mission_count.splice(0, 1);
			compute();
			
		}, function() {
			
			$scope.refs_without_mission_count.splice(0, 1);
			compute();
		});
	}
	
	/* Page loading */
	
	$scope.refs_without_preview = [];
	
	$scope.init = function(refs_without_preview, refs_without_mission_count, regionsids_without_locale, mosaics_to_tag) {

		$scope.refs_without_preview = refs_without_preview;
		$scope.refs_without_mission_count = refs_without_mission_count;
		
		$scope.regionsids_without_locale = regionsids_without_locale;
		
		$scope.mosaics_to_tag = mosaics_to_tag;
		
		$scope.loaded = true;
	}
});