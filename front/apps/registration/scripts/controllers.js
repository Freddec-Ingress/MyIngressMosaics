angular.module('RegistrationApp.controllers', [])

angular.module('RegistrationApp.controllers').controller('MissionsCtrl', function($scope, $state, UserService, CreateService) {

	var mosaics = [];
	var missions = [];
	
	var mis = UserService.data.missions;
	for (var mission of mis) {
		
		/* Mosaic name */
		var mosaic_name = mission.name;
		mosaic_name = mosaic_name.replace(/0|1|2|3|4|5|6|7|8|9|#/g, '');
		mosaic_name = mosaic_name.replace('.', '');
		mosaic_name = mosaic_name.replace('(', '');
		mosaic_name = mosaic_name.replace(')', '');
		mosaic_name = mosaic_name.replace('/', '');
		mosaic_name = mosaic_name.trim();
		mosaic_name = mosaic_name.replace('of  ', '');
		mosaic_name = mosaic_name.replace('  of', '');
		mosaic_name = mosaic_name.replace('[ - ] ', '');
		mosaic_name = mosaic_name.replace('[] ', '');
		mosaic_name = mosaic_name.replace('of : ', '');
		mosaic_name = mosaic_name.replace('[ of ] ', '');
		mosaic_name = mosaic_name.replace('  ', ' ');
		
		/* Find existing mosaic */
		var existing_mosaic = null;
		for (var mosaic of mosaics) {
			if (mosaic.name == mosaic_name) {
				existing_mosaic = mosaic;
				break;
			}
		}
		
		/* If not existing mosaic then create new mosaic */
		var futur_mosaic = null;
		if (existing_mosaic) futur_mosaic = existing_mosaic;
		else {
			futur_mosaic = {
				'name': mosaic_name,
				'missions': [],
				'creating': false,
			}
			mosaics.push(futur_mosaic);
		}
		
		/* Mission order */
		var order = 0;
		var found = mission.name.match(/[0-9]+/);
		if (found) order = parseInt(found[0]);
		mission.order = order;

		/* Add mission to future mosaic */
		futur_mosaic.missions.push(mission);
	}
	
	/* Sort mosaic missions by order */
	for (var mosaic of mosaics) {
		
		mosaic.missions = mosaic.missions.sort(function(a, b) {
			
			if (a.order < b.order) { return -1; }
			if (a.order > b.order) { return  1; }
			return 0;
		});
	}
	
	/* Create mosaic */
	$scope.createMosaic = function(mosaic) {
		
		mosaic.creating = true;
		CreateService.createWithMosaic(mosaic, $scope.createMosaicCallback);
	}
	$scope.createMosaicCallback = function(mosaic) {
		
		mosaic.creating = false;
		$scope.mosaics.splice($scope.mosaics.indexOf(mosaic), 1);
	}
	
	/* Standalone missions */
	for (var mosaic of mosaics) {
		if (mosaic.missions.length < 3) {
			missions = missions.concat(mosaic.missions);
			mosaics.splice(mosaics.indexOf(mosaic), 1);
		}
	}
	
	/* Delete mosaic */
	$scope.deleteMosaic = function(mosaic) {
		
		for (var item of mosaic.missions) {
			UserService.deleteMission(item);
		}
		
		$scope.mosaics.splice($scope.mosaics.indexOf(mosaic), 1);
	}
	
	$scope.mosaics = mosaics;
	$scope.missions = missions;
	
	CreateService.init();
	
	$scope.selected_missions = CreateService.data.missions;
	
	$scope.isSelected = function(ref) {
		
		if (CreateService.getRefArray().indexOf(ref) != -1) {
			return true;
		} else {
			return false;
		}
	}
	
	$scope.toggle = function(index, event, item) {
		
		if (event.shiftKey) {
			event.preventDefault();
			
			if (index > $scope.lastSelectedIndex) {
				
				for (var i = ($scope.lastSelectedIndex + 1); i <= index; i++) {
					
					var m = $scope.missions[i];
					if (!$scope.isSelected(m.ref)) {
						CreateService.add(m);
					}
				}
			}
			else {
				
				for (var i = index; i < $scope.lastSelectedIndex; i++) {
					
					var m = $scope.missions[i];
					if (!$scope.isSelected(m.ref)) {
						CreateService.add(m);
					}
				}
			}
		}
		else {
			
			if ($scope.isSelected(item.ref)) {
				CreateService.remove(item);
			}
			else {
				CreateService.add(item);
			}
		}
		
		$scope.lastSelectedIndex = index;
	}
	
	$scope.unselectAll = function() {
		
		CreateService.removeAll();
	}
	
	$scope.hasSelected = function() {
		
		if (CreateService.data.missions.length > 0) {
			return true;
		} else {
			return false;
		}
	}
	
	$scope.nextStep = function() {
		$state.go('root.create');
	}
	
	$scope.delete = function(item) {
		UserService.deleteMission(item);
	}
	
	$scope.deleteAll = function() {
		
		for (var item of $scope.missions) {
			UserService.deleteMission(item);
		}
	}
	
	/* Sort name */
	
	UserService.sortMissionsByName('asc');
	
	$scope.sortName = 'asc';
	
	$scope.sortMissionsByName = function() {
		
		$scope.sortCreator = '';
		
		if ($scope.sortName == '' || $scope.sortName == 'asc') {
			
			UserService.sortMissionsByName('desc');
			$scope.sortName = 'desc';
		}
		
		else if ($scope.sortName == 'desc') {
			
			UserService.sortMissionsByName('asc');
			$scope.sortName = 'asc';
		}
	}
	
	/* Sort creator */
	
	$scope.sortCreator = '';
	
	$scope.sortMissionsByCreator = function() {
		
		$scope.sortName = '';
		
		if ($scope.sortCreator == '' || $scope.sortCreator == 'asc') {
			
			UserService.sortMissionsByCreator('desc');
			$scope.sortCreator = 'desc';
		}
		
		else if ($scope.sortCreator == 'desc') {
			
			UserService.sortMissionsByCreator('asc');
			$scope.sortCreator = 'asc';
		}
	}
});

angular.module('RegistrationApp.controllers').controller('CreateCtrl', function($scope, $state, CreateService) {
	
	$scope.data = null;

	if (CreateService.data.missions.length < 1) {
		$state.go('root.missions');
	}
	
	CreateService.default();
	
	var geocoder = new google.maps.Geocoder;
	
	var latlng = {
		lat: parseFloat(CreateService.data.missions[0].lat),
		lng: parseFloat(CreateService.data.missions[0].lng),
	};

	geocoder.geocode({'location': latlng}, function(results, status) {
		
		if (status === 'OK') {
			if (results[1]) {
				
				var admin2 = null;
				var admin3 = null;
				
				for (var item of results[1].address_components) {
					
					if (item.types[0] == 'country') CreateService.data.country = item.long_name;
					if (item.types[0] == 'locality') CreateService.data.city = item.long_name;
					if (item.types[0] == 'administrative_area_level_1') CreateService.data.region = item.long_name;
					if (item.types[0] == 'administrative_area_level_2') admin2 = item.long_name;
					if (item.types[0] == 'administrative_area_level_3') admin3 = item.long_name;
				}
				
				if (!CreateService.data.city && admin2) CreateService.data.city = item.admin2;
				if (!CreateService.data.city && admin3) CreateService.data.city = item.admin3;
				
				$scope.$apply();
			}
		}
	});

	$scope.data = CreateService.data;
	$scope.create = CreateService.create;

	$scope.rows = function() {
		
		var rows = [];
		for (var i = 0; i < $scope.data.rows; i++) {
			rows.push(i);
		}
		
		return rows;
	}
	
	$scope.cols = function() {
		
		var temp = 1;
		if ($scope.data.cols > 0) temp = $scope.data.cols;
		if (!temp) temp = 1;
		
		var cols = [];
		for (var i = 0; i < temp; i++) {
			cols.push(i);
		}
		
		return cols;
	}
	
	$scope.getImage = function(i, j) {
		
		var order = (i * $scope.data.cols + j) + 1;
		return CreateService.getImageByOrder(order);
	}
});

angular.module('RegistrationApp.controllers').controller('PluginCtrl', function() {
});