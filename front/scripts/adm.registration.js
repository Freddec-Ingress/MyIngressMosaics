angular.module('FrontModule.controllers').controller('AdmRegistationCtrl', function($scope, $window, API, UtilsService) {
	
	/* Potential management */
	
	$scope.refresh_missions = function(potential) {
		
		potential.refreshing_missions = true;
		
		potential.missions = [];
		
		var data = { 'text':potential.name };
		API.sendRequest('/api/new_missions/', 'POST', {}, data).then(function(response) {
			
			potential.missions = response.missions;
			
			for (var mission of potential.missions) {
				
				var order = UtilsService.getOrderFromMissionName(mission.title);
				if (order < 1) order = $scope.selected.indexOf(mission) + 1;
				mission.order = order;
			}
			
			potential.missions.sort(UtilsService.sortMissionsByOrderTitleAsc);
			
			potential.refreshing_missions = false;
		});
	}
	
	$scope.exclude = function(potential) {
		
		var index = $scope.potentials.indexOf(potential);
		$scope.potentials.splice(index, 1);
		
		var data = { 'name':potential.name};
		API.sendRequest('/api/adm/potential/exclude', 'POST', {}, data);
	}
	
	$scope.rename = function(potential, new_name) {
		
		var data = { 'name':potential.name, 'new_name':new_name };
		API.sendRequest('/api/adm/potential/rename', 'POST', {}, data).then(function(response) {
			
			potential.name = new_name;
			
			$scope.refresh_missions(potential);
		});
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
		
		API.sendRequest('/api/potentials/tovalidate/', 'POST').then(function(response) {
		
			$scope.potentials = response;
			
			$scope.refreshing_potentials = false;
		});
	}
});