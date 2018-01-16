angular.module('FrontModule.controllers').controller('AdmRegistationCtrl', function($scope, $window, API, UtilsService) {
	
	/* Potential management */
	
	$scope.refresh_missions = function(potential) {
		
		potential.refreshing_missions = true;
		
		potential.missions = [];
		
		var data = { 'text':potential.name };
		API.sendRequest('/api/new_missions/', 'POST', {}, data).then(function(response) {
			
			potential.missions = response.missions;
			
			potential.refreshing_missions = false;
		});
	}
	
	$scope.exclude = function(potential) {
		
		var index = $scope.potentials.indexOf(potential);
		$scope.potentials.splice(index, 1);
		
		var data = { 'name':potential.name};
		API.sendRequest('/api/adm/potential/exclude', 'POST', {}, data);
	}
	
	$scope.validate = function(potential) {
		
		var index = $scope.potentials.indexOf(potential);
		$scope.potentials.splice(index, 1);
		
		var data = { 'name':potential.name};
		API.sendRequest('/api/adm/potential/validate', 'POST', {}, data);
	}
	
	/* Page loading */
	
	$scope.loaded = true;
	
	$scope.refreshing_potentials = false;
	
	$scope.refresh_potentials = function() {
		
		$scope.refreshing_potentials = true;
		
		$scope.potentials = [];
		
		API.sendRequest('/api/potentials/', 'POST').then(function(response) {
		
			$scope.potentials = response;
			
			$scope.refreshing_potentials = false;
		});
	}
});