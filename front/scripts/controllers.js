angular.module('AngularApp.controllers', [])

angular.module('AngularApp.controllers').controller('RootCtrl', function($rootScope, $scope, $stateParams, $translate, $window, UserService) {
	
	var supported_lang = ['en', 'fr'];
	
	var user_lang = 'en';
	
	var lang = $window.navigator.language || $window.navigator.userLanguage;
	if (supported_lang.indexOf(lang) != -1) user_lang = lang;
	
  	$translate.use(user_lang);

	$scope.user = UserService.data;
	
	$scope.logout = UserService.logout;
	
	$rootScope.menu_open = false;
	
	$scope.openMenu = function() {
		$rootScope.menu_open = true;
	}
	
	$scope.closeMenu = function() {
		$rootScope.menu_open = false;
	}
	
	$scope.changeLang = function(lang) {
		$translate.use(lang);
	}
});

angular.module('AngularApp.controllers').controller('HomeCtrl', function($scope, DataService) {
	
	$scope.latest_loading = true;
	
	DataService.loadLatest().then(function(response) {
		
		$scope.latest_loading = false;
		
		$scope.mosaics = response;
	});
});

angular.module('AngularApp.controllers').controller('LoginCtrl', function($scope, UserService) {
	
	$scope.page_title = 'login_TITLE';
	
	$scope.loginModel = { username:null, password:null };
	
	$scope.localLogin = UserService.localLogin;
	$scope.socialLogin = UserService.socialLogin;
});

angular.module('AngularApp.controllers').controller('RegisterCtrl', function($scope, UserService) {
	
	$scope.page_title = 'register_TITLE';
	
	$scope.registerModel = { username:null, password1:null, password2:null, email:null };
	
	$scope.register = UserService.register;
});

angular.module('AngularApp.controllers').controller('ProfileCtrl', function($scope, UserService, toastr, $filter) {

	$scope.user = UserService.data;
	
	/* Edit */
	
	$scope.editMode = false;
	$scope.editLoading = false;
	
	$scope.editModel = {name:null};
	
	$scope.openEdit = function() {
		
		$scope.editModel.name = $scope.user.name;
		
		$scope.editMode = true;
	}
	
	$scope.closeEdit = function() {
		
		$scope.editMode = false;
	}
	
	$scope.edit = function() {
		
		$scope.editLoading = true;
			
		UserService.updateName($scope.editModel.name).then(function(response) {
			
			toastr.success($filter('translate')('success_EDIT'));

			$scope.editMode = false;
			$scope.editLoading = false;
			
		}, function(response) {
			
			$scope.editMode = false;
			$scope.editLoading = false;
		});
	}
});

angular.module('AngularApp.controllers').controller('MissionsCtrl', function($scope, $state, UserService, CreateService) {

	$scope.mosaics = [];
	
	var missions = UserService.data.missions;
	for (var mission of missions) {
		
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
		
		/* Find existing mosaic */
		var existing_mosaic = null;
		for (var mosaic of $scope.mosaics) {
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
			}
			$scope.mosaics.push(futur_mosaic);
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
	for (var mosaic of $scope.mosaics) {
		
		mosaic.missions = mosaic.missions.sort(function(a, b) {
			
			if (a.order < b.order) { return -1; }
			if (a.order > b.order) { return  1; }
			return 0;
		});
	}
	
	/* Create mosaic */
	$scope.createMosaic = function(mosaic) {
		
		CreateService.createWithMosaic(mosaic);
		$scope.mosaics.splice($scope.mosaics.indexOf(mosaic), 1);
	}
	
	/* Standalone missions */
	$scope.missions = [];
	for (var mosaic of $scope.mosaics) {
		if (mosaic.missions.length < 3) {
			for (var mission of mosaic.missions) {
				$scope.missions.push(mission);
			}
			$scope.mosaics.splice($scope.mosaics.indexOf(mosaic), 1);
		}
	}
	
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

angular.module('AngularApp.controllers').controller('CreateCtrl', function($scope, $state, CreateService) {
	
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

angular.module('AngularApp.controllers').controller('MosaicCtrl', function($scope, $state, $timeout, $window, $filter, toastr, MosaicService) {

	$scope.mosaic = MosaicService.data.mosaic;
	$scope.potentials = MosaicService.data.potentials;
	
	$scope.remove = MosaicService.remove;
	
	/* Edit */
	
	$scope.editMode = false;
	$scope.editLoading = false;
	
	$scope.editModel = {ref:null, city:null, region:null, desc:null, type:null, cols:null, rows:null, title:null, country:null};
	
	$scope.openEdit = function() {
		
		$scope.editModel.ref = $scope.mosaic.ref;
		$scope.editModel.city = $scope.mosaic.city;
		$scope.editModel.desc = $scope.mosaic.desc;
		$scope.editModel.type = $scope.mosaic.type;
		$scope.editModel.cols = $scope.mosaic.cols;
		$scope.editModel.rows = $scope.mosaic.rows;
		$scope.editModel.title = $scope.mosaic.title;
		$scope.editModel.region = $scope.mosaic.region;
		$scope.editModel.country = $scope.mosaic.country;
		
		$scope.editMode = true;
	}
	
	$scope.closeEdit = function() {
		
		$scope.editMode = false;
	}
	
	$scope.edit = function() {
		
		$scope.editLoading = true;
			
		MosaicService.edit($scope.editModel).then(function(response) {
			
			toastr.success($filter('translate')('success_EDIT'));

			$scope.editMode = false;
			$scope.editLoading = false;
			
		}, function(response) {
			
			$scope.editMode = false;
			$scope.editLoading = false;
		});
	}
	
	/* Reorder */
	
	$scope.reorderMode = false;
	$scope.reorderLoading = false;
	
	$scope.reorderModel = {ref:null, missions:null};
	
	$scope.openReorder = function() {
		
		$scope.reorderModel.ref = $scope.mosaic.ref;
		$scope.reorderModel.missions = $scope.mosaic.missions;

		$scope.reorderMode = true;
	}
	
	$scope.closeReorder = function() {
		
		$scope.reorderMode = false;
	}
	
	$scope.reorder = function() {
		
		$scope.reorderLoading = true;
			
		MosaicService.reorder($scope.reorderModel).then(function(response) {
			
			toastr.success($filter('translate')('success_REORDER'));

			$scope.reorderMode = false;
			$scope.reorderLoading = false;
			
		}, function(response) {
			
			$scope.reorderMode = false;
			$scope.reorderLoading = false;
		});
	}
	
	/* Add */
	
	$scope.addMode = false;
	
	$scope.openAdd = function() {
		
		$scope.addMode = true;
	}
	
	$scope.closeAdd = function() {
		
		$scope.addMode = false;
	}
	
	$scope.add = function(item, order) {
		
		var index = $scope.potentials.indexOf(item);
		if (index > -1) {
		    $scope.potentials.splice(index, 1);
		}
		
		item.order = order
		
		MosaicService.add(item.ref, order);
	}
	
	/* Delete */
	
	$scope.deleteModel = {name:null};
	
	$scope.delete = function() {
		
		if ($scope.deleteModel.name == $scope.mosaic.title) {
			
			MosaicService.delete();
		}
	}
	
	/* Repair */
	
	$scope.repair = function() {
		
		MosaicService.repair().then(function(response) {
			
			$state.reload();
		});
	}
	
	/* Map */

	$scope.initMap = function() {
		
		var style = [{featureType:"all",elementType:"all",stylers:[{visibility:"on"},{hue:"#131c1c"},{saturation:"-50"},{invert_lightness:!0}]},{featureType:"water",elementType:"all",stylers:[{visibility:"on"},{hue:"#005eff"},{invert_lightness:!0}]},{featureType:"poi",stylers:[{visibility:"off"}]},{featureType:"transit",elementType:"all",stylers:[{visibility:"off"}]},{featureType:"road",elementType:"labels.icon",stylers:[{invert_lightness:!0}]}];
		
		var map = new google.maps.Map(document.getElementById('map'), {
			
			zoom: 8,
			styles : style,
			zoomControl: true,
			disableDefaultUI: true,
			fullscreenControl: true,
			center: {lat: $scope.mosaic.missions[0].lat, lng: $scope.mosaic.missions[0].lng},
		});
		
		var latlngbounds = new google.maps.LatLngBounds();
		
		var image = {
			size: new google.maps.Size(50, 50),
			origin: new google.maps.Point(0, 0),
			anchor: new google.maps.Point(25, 25),
			labelOrigin: new google.maps.Point(25, 27),
			url: 'https://www.myingressmosaics.com/static/front/img/neutral.png',
		};
		
		var lineSymbol = {
			path: 'M 0,0 0,-5',
			strokeOpacity: 1,
			scale: 2
		};
		
		var arrowSymbol = {
			path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW
		};
		
		var nextlatLng = null;
		var previouslatLng = null;
		
		for (var m of $scope.mosaic.missions) {
		
			/* Mission marker */
			
	        var marker = new google.maps.Marker({
	        	
				map: map,
				icon: image,
				label: { text:String(m.order), color:'#FFFFFF', fontFamily:'Coda', fontSize:'.75rem', fontWeight:'400', },
				position: {lat: m.lat, lng: m.lng},
	        });
	        
	        var mlatLng = new google.maps.LatLng(m.lat, m.lng);
	        latlngbounds.extend(mlatLng);
	        
	        /* Mission transit */
	        
	        nextlatLng = mlatLng;
	        
	        if (nextlatLng && previouslatLng) {
	        	
				var transitRoadmapCoordinates= [];
				
		        transitRoadmapCoordinates.push(previouslatLng);
		        transitRoadmapCoordinates.push(nextlatLng);
		        
				var transitRoadmap = new google.maps.Polyline({
					path: transitRoadmapCoordinates,
					geodesic: true,
					strokeColor: '#ebbc4a',
					strokeOpacity: 0,
					strokeWeight: 2,
					icons: [{
						icon: lineSymbol,
						offset: '0',
						repeat: '20px'
					},],
		        });
		        
		        transitRoadmap.setMap(map);
	        }

			/* Mission roadmap */
			
			var roadmapCoordinates= [];
		
			for (var p of m.portals) {
				
				if (p.lat != 0.0 && p.lng != 0.0) {
					
			        var platLng = new google.maps.LatLng(p.lat, p.lng);
			        roadmapCoordinates.push(platLng);
			        
			        previouslatLng = platLng;
				}
			}
	        
			var roadmap = new google.maps.Polyline({
				path: roadmapCoordinates,
				geodesic: true,
				strokeColor: '#ebbc4a',
				strokeOpacity: 0.95,
				strokeWeight: 2,
				icons: [{
					icon: arrowSymbol,
					offset: '100%',
				},],
			});
	        
	        roadmap.setMap(map);
	        
		}
		
		map.setCenter(latlngbounds.getCenter());
		map.fitBounds(latlngbounds); 
	}
	
	/* Go to a creator page */
	
	$scope.goToCreator = function(creator) {
		
		$state.go('root.creator', {'creator':creator});
	}
	
	/* Go to a location page */
	
	$scope.goToCountry = function() {
		
		$state.go('root.country', {'country':$scope.mosaic.country});
	}
	
	$scope.goToRegion = function() {
		
		$state.go('root.region', {'country':$scope.mosaic.country, 'region':$scope.mosaic.region});
	}
	
	$scope.goToCity = function() {
		
		$state.go('root.city', {'country':$scope.mosaic.country, 'region':$scope.mosaic.region, 'city':$scope.mosaic.city});
	}
});

angular.module('AngularApp.controllers').controller('MyMosaicsCtrl', function($scope, $state, UserService) {
	
	$scope.page_title = 'mymosaics_TITLE';

	$scope.mosaics = UserService.data.mosaics;
	
	$scope.go = function(item) {
		$state.go('root.mosaic', {ref: item.ref});
	}
});

angular.module('AngularApp.controllers').controller('WorldCtrl', function($scope, $state, DataService) {
	
	$scope.world_loading = true;
	
	DataService.loadCountriesFromWorld().then(function(response) {
		
		$scope.world_loading = false;
		
		$scope.countries = response;
		
		DataService.sortByMosaics('desc', $scope.countries);
	});

	/* Go to a country page */
	
	$scope.go = function(item) {
		
		$state.go('root.country', {'country':item.name});
	}

	/* Sort countries by mosaics */
	
	$scope.sortMosaics = 'desc';
	
	$scope.sortByMosaics = function() {
		
		$scope.sortName = '';
		
		if ($scope.sortMosaics == '' || $scope.sortMosaics == 'asc') {
			
			DataService.sortByMosaics('desc', $scope.countries);
			$scope.sortMosaics = 'desc';
		}
		
		else if ($scope.sortMosaics == 'desc') {
			
			DataService.sortByMosaics('asc', $scope.countries);
			$scope.sortMosaics = 'asc';
		}
	}
	
	/* Sort countries by name */
	
	$scope.sortName = '';
	
	$scope.sortByName = function() {
		
		$scope.sortMosaics = '';
		
		if ($scope.sortName == '' || $scope.sortName == 'asc') {
			
			DataService.sortByName('desc', $scope.countries);
			$scope.sortName = 'desc';
		}
		
		else if ($scope.sortName == 'desc') {
			
			DataService.sortByName('asc', $scope.countries);
			$scope.sortName = 'asc';
		}
	}
	
	/* Rename country */
	
	$scope.renameCountryModel = {oldValue:null, newValue:null};
	
	$scope.renameCountry = function() {
		
		DataService.renameCountry($scope.renameCountryModel.oldValue, $scope.renameCountryModel.newValue).then(function(response) {
			
			$state.reload();
		});
	}
});

angular.module('AngularApp.controllers').controller('CountryCtrl', function($scope, $state, $stateParams, DataService) {
	
	$scope.country_loading = true;
	
	$scope.country_name = $stateParams.country;
	
	DataService.loadRegionsFromCountry($scope.country_name).then(function(response) {
		
		$scope.country_loading = false;
		
		$scope.regions = response;
		
		DataService.sortByMosaics('desc', $scope.regions);
	});

	/* Go to a region page */

	$scope.go = function(item) {
		
		$state.go('root.region', {'country':$scope.country_name, 'region':item.name});
	}

	/* Sort regions by mosaics */
	
	$scope.sortMosaics = 'desc';
	
	$scope.sortByMosaics = function() {
		
		$scope.sortName = '';
		
		if ($scope.sortMosaics == '' || $scope.sortMosaics == 'asc') {
			
			DataService.sortByMosaics('desc', $scope.regions);
			$scope.sortMosaics = 'desc';
		}
		
		else if ($scope.sortMosaics == 'desc') {
			
			DataService.sortByMosaics('asc', $scope.regions);
			$scope.sortMosaics = 'asc';
		}
	}
	
	/* Sort regions by name */
	
	$scope.sortName = '';
	
	$scope.sortByName = function() {
		
		$scope.sortMosaics = '';
		
		if ($scope.sortName == '' || $scope.sortName == 'asc') {
			
			DataService.sortByName('desc', $scope.regions);
			$scope.sortName = 'desc';
		}
		
		else if ($scope.sortName == 'desc', $scope.regions) {
			
			DataService.sortByName('asc');
			$scope.sortName = 'asc';
		}
	}
});

angular.module('AngularApp.controllers').controller('RegionCtrl', function($scope, $state, $stateParams, DataService) {
	
	$scope.region_loading = true;
	
	$scope.country_name = $stateParams.country;
	$scope.region_name = $stateParams.region;
	
	DataService.loadCitiesFromRegion($scope.country_name, $scope.region_name).then(function(response) {
		
		$scope.region_loading = false;
		
		$scope.cities = response;
		
		DataService.sortByMosaics('desc', $scope.cities);
	});

	/* Breadcrumb */

	$scope.goToCountry = function() {
		
		$state.go('root.country', {'country':$scope.country_name});
	}

	/* Go to a city page */

	$scope.go = function(item) {
		
		$state.go('root.city', {'country':$scope.country_name, 'region':$scope.region_name, 'city':item.name});
	}

	/* Sort cities by mosaics */
	
	$scope.sortMosaics = 'desc';
	
	$scope.sortByMosaics = function() {
		
		$scope.sortName = '';
		
		if ($scope.sortMosaics == '' || $scope.sortMosaics == 'asc') {
			
			DataService.sortByMosaics('desc', $scope.cities);
			$scope.sortMosaics = 'desc';
		}
		
		else if ($scope.sortMosaics == 'desc') {
			
			DataService.sortByMosaics('asc', $scope.cities);
			$scope.sortMosaics = 'asc';
		}
	}
	
	/* Sort cities by name */
	
	$scope.sortName = '';
	
	$scope.sortByName = function() {
		
		$scope.sortMosaics = '';
		
		if ($scope.sortName == '' || $scope.sortName == 'asc') {
			
			DataService.sortByName('desc', $scope.cities);
			$scope.sortName = 'desc';
		}
		
		else if ($scope.sortName == 'desc', $scope.cities) {
			
			DataService.sortByName('asc');
			$scope.sortName = 'asc';
		}
	}
	
	/* Set region */
	
	$scope.setRegionyModel = {city:null, region:null};
	
	$scope.setRegion = function() {
		
		DataService.setRegion($scope.setRegionyModel.city, $scope.setRegionyModel.region).then(function(response) {
			
			$state.reload();
		});
	}
	
	/* Rename country */
	
	$scope.renameCityModel = {oldValue:null, newValue:null};
	
	$scope.renameCity = function() {
		
		DataService.renameCity($scope.renameCityModel.oldValue, $scope.renameCityModel.newValue).then(function(response) {
			
			$state.reload();
		});
	}
});

angular.module('AngularApp.controllers').controller('CityCtrl', function($scope, $state, $stateParams, DataService) {
	
	$scope.city_loading = true;
	
	$scope.country_name = $stateParams.country;
	$scope.region_name = $stateParams.region;
	$scope.city_name = $stateParams.city;
	
	DataService.loadMosaicsFromCity($scope.country_name, $scope.region_name, $scope.city_name).then(function(response) {
		
		$scope.city_loading = false;
		
		$scope.mosaics = response;
		
		DataService.sortByMissions('desc', $scope.mosaics);
	});

	/* Breadcrumb */

	$scope.goToCountry = function() {
		
		$state.go('root.country', {'country':$scope.country_name});
	}
	
	$scope.goToRegion = function() {
		
		$state.go('root.region', {'country':$scope.country_name, 'region':$scope.region_name});
	}

	/* Go to a mosaic page */
	
	$scope.go = function(item) {
		
		$state.go('root.mosaic', {'ref':item.ref});
	}
	
	/* Sort mosaics by missions */
	
	$scope.sortMissions = 'desc';
	
	$scope.sortMosaicsByMissions = function() {
		
		if ($scope.sortMissions == '' || $scope.sortMissions == 'asc') {
			
			DataService.sortMosaicsByMissions('desc');
			$scope.sortMissions = 'desc';
		}
		
		else if ($scope.sortMissions == 'desc') {
			
			DataService.sortMosaicsByMissions('asc');
			$scope.sortMissions = 'asc';
		}
	}
});

angular.module('AngularApp.controllers').controller('CreatorCtrl', function($scope, $state, $stateParams, DataService) {
	
	$scope.creator_loading = true;

	$scope.creator_name = $stateParams.creator;
	
	DataService.loadMosaicsFromCreator($scope.creator_name).then(function(response) {
		
		$scope.creator_loading = false;
		
		$scope.faction = response.faction;
		$scope.mosaics = response.mosaics;
		
		DataService.sortByMissions('desc', $scope.mosaics);
	});

	/* Go to a mosaic page */
	
	$scope.go = function(item) {
		
		$state.go('root.mosaic', {'ref':item.ref});
	}
	
	/* Sort mosaics by missions */
	
	$scope.sortMissions = 'desc';
	
	$scope.sortMosaicsByMissions = function() {
		
		if ($scope.sortMissions == '' || $scope.sortMissions == 'asc') {
			
			DataService.sortMosaicsByMissions('desc');
			$scope.sortMissions = 'desc';
		}
		
		else if ($scope.sortMissions == 'desc') {
			
			DataService.sortMosaicsByMissions('asc');
			$scope.sortMissions = 'asc';
		}
	}
});

angular.module('AngularApp.controllers').controller('SearchCtrl', function($scope, $state, toastr, $filter, SearchService) {
	
	/* Search */
	
	$scope.search_loading = false;
	
	$scope.searchModel = {text:SearchService.data.search_text};

	$scope.no_result = SearchService.data.no_result;
	
	$scope.cities = SearchService.data.cities;
	$scope.regions = SearchService.data.regions;
	$scope.mosaics = SearchService.data.mosaics;
	$scope.creators = SearchService.data.creators;
	$scope.countries = SearchService.data.countries;
	
	$scope.search = function() {
		
		$scope.search_loading = true;
		
		$scope.no_result = false;
		
		$scope.cities = null;
		$scope.regions = null;
		$scope.mosaics = null;
		$scope.creators = null;
		$scope.countries = null;
	
		SearchService.reset();
		
		if ($scope.searchModel.text) {
			
			if ($scope.searchModel.text.length > 2) {
		
				SearchService.search($scope.searchModel.text).then(function(response) {
					
					$scope.no_result = SearchService.data.no_result;
					
					$scope.cities = SearchService.data.cities;
					$scope.regions = SearchService.data.regions;
					$scope.mosaics = SearchService.data.mosaics;
					$scope.creators = SearchService.data.creators;
					$scope.countries = SearchService.data.countries;
	
					$scope.search_loading = false;
				});
			}
			else {
					
				$scope.search_loading = false;
				
				toastr.error($filter('translate')('error_ATLEAST3CHAR'));
			}
		}
		else {
				
			$scope.search_loading = false;
			
			toastr.error($filter('translate')('error_ATLEAST3CHAR'));
		}
	}
	
	/* Go to ... */
	
	$scope.goToCreator = function(creator) {
		
		$state.go('root.creator', {'creator':creator.name});
	}

	$scope.goToCountry = function(country) {
		
		$state.go('root.country', {'country':country.name});
	}
	
	$scope.goToRegion = function(region) {
		
		$state.go('root.region', {'country':region.country, 'region':region.name});
	}
	
	$scope.goToCity = function(city) {
		
		$state.go('root.city', {'country':city.country, 'region':city.region, 'city':city.name});
	}
	
	$scope.goToMosaic = function(mosaic) {
		
		$state.go('root.mosaic', {'ref':mosaic.ref});
	}
});

angular.module('AngularApp.controllers').controller('MapCtrl', function($scope, $rootScope, $cookies, toastr, $filter, $compile, MapService) {
	
	/* Map */
	
	var refArray = [];

	$rootScope.infowindow = new google.maps.InfoWindow({
		content: '',
		pixelOffset: new google.maps.Size(5, 5)
	});

	$scope.initMap = function() {
		
		var style = [{featureType:"all",elementType:"all",stylers:[{visibility:"on"},{hue:"#131c1c"},{saturation:"-50"},{invert_lightness:!0}]},{featureType:"water",elementType:"all",stylers:[{visibility:"on"},{hue:"#005eff"},{invert_lightness:!0}]},{featureType:"poi",stylers:[{visibility:"off"}]},{featureType:"transit",elementType:"all",stylers:[{visibility:"off"}]},{featureType:"road",elementType:"labels.icon",stylers:[{invert_lightness:!0}]}];
		
		var startLat = parseFloat($cookies.get('startLat'));
		var startLng = parseFloat($cookies.get('startLng'));
		
		if (!startLat) startLat = 0.0;
		if (!startLng) startLng = 0.0;
		
		var startZoom = parseInt($cookies.get('startZoom'));
		
		if (!startZoom) startZoom = 15;
		
		var map = new google.maps.Map(document.getElementById('map'), {
			
			zoom: startZoom,
			styles : style,
			zoomControl: true,
			disableDefaultUI: true,
			center: {lat: startLat, lng: startLng},
		});
		
		function GeolocationControl(controlDiv, map) {
		
		    var controlUI = document.createElement('div');
		    controlUI.style.backgroundColor = '#FFFFFF';
		    controlUI.style.borderStyle = 'solid';
		    controlUI.style.borderWidth = '1px';
		    controlUI.style.borderColor = 'white';
		    controlUI.style.cursor = 'pointer';
		    controlUI.style.textAlign = 'center';
		    controlUI.style.marginRight = '.65rem';
		    controlUI.style.padding = '.375rem';
		    controlUI.style.borderRadius = '.125rem';
		    controlDiv.appendChild(controlUI);
		
		    var controlText = document.createElement('div');
		    controlText.style.fontFamily = 'Arial,sans-serif';
		    controlText.style.fontSize = '1rem';
		    controlText.style.color = '#000000';
		    controlText.innerHTML = '<i class="fa fa-crosshairs"></i>';
		    controlUI.appendChild(controlText);
		
		    google.maps.event.addDomListener(controlUI, 'click', geolocate);
		}
		
		function geolocate() {
		
		    if (navigator.geolocation) {
		
		        navigator.geolocation.getCurrentPosition(function (position) {
		
		            var pos = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
		            map.setCenter(pos);
		        });
		    }
		}
	
		var geolocationDiv = document.createElement('div');
		var geolocationControl = new GeolocationControl(geolocationDiv, map);
		
		map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(geolocationDiv);
		
		var image = {
			size: new google.maps.Size(30, 30),
			origin: new google.maps.Point(0, 0),
			anchor: new google.maps.Point(15, 15),
			labelOrigin: new google.maps.Point(15, 17),
			url: 'https://www.myingressmosaics.com/static/front/img/marker.png',
		};
		
		map.addListener('idle', function(e) {
			
			var center = map.getCenter();
			
			$cookies.put('startLat', center.lat());
			$cookies.put('startLng', center.lng());
			
			$cookies.put('startZoom', map.getZoom());
			
			var bds = map.getBounds();
			
			var South_Lat = bds.getSouthWest().lat();
			var South_Lng = bds.getSouthWest().lng();
			var North_Lat = bds.getNorthEast().lat();
			var North_Lng = bds.getNorthEast().lng();
			
			MapService.getMosaics(South_Lat, South_Lng, North_Lat, North_Lng).then(function(response) {
				
				if (response) {
					
					for (var item of response) {
					
						if (refArray.indexOf(item.ref) == -1) {
							
							refArray.push(item.ref);
							
							var contentImage = '';
							for (var m of item.missions.reverse()) {
								
								contentImage +=	
									'<div style="flex:0 0 16.666667%;">' +
									    '<img src="/static/front/img/mask.png" style="width:100%; background-color:#000000; background-image:url(' + m.image + '=s10); background-size: 85% 85%; background-position: 50% 50%; float:left; background-repeat: no-repeat;" />' +
									'</div>'
								;
							}
							
							var contentString =
								'<a class="infoBlock" ui-sref="root.mosaic({ref: \'' + item.ref + '\'})">' +
									'<div class="image">' + contentImage + '</div>' +
									'<div class="detail">' +
										'<div class="title">' + item.title + '</div>' +
										'<div class="info">' + item.count + ' missions <br> ' + item._distance.toFixed(2) + ' km &middot; ' + item.type + '</div>' +
									'</div>' +
								'</a>'
							;
            
							var latLng = new google.maps.LatLng(item._startLat, item._startLng);
							var marker = new google.maps.Marker({
								position: latLng,
								map: map,
								icon: image,
							});
							
							google.maps.event.addListener(marker, 'click', (function (marker, content, infowindow) {
								return function () {
									
									var contentDiv = angular.element('<div/>');
									contentDiv.append(content);
									
									var compiledContent = $compile(contentDiv)($scope);
									
									infowindow.setContent(compiledContent[0]);
									infowindow.open($scope.map, marker);
								};
							})(marker, contentString, $rootScope.infowindow));
						}
					}
				}
			});
		});
		
		if (startLat == 0.0 && startLng == 0.0) {
			
			if (navigator.geolocation) {
				
				navigator.geolocation.getCurrentPosition(function(position) {
					
					var pos = {
						lat: position.coords.latitude,
						lng: position.coords.longitude
					};
				
					map.setCenter(pos);
	
				}, function() {
					
					toastr.error($filter('translate')('error_GEOLOCFAILED'));
				});
				
			} else {
				
				toastr.error($filter('translate')('error_GEOLOCSUPPORT'));
			}
		}
		
		var geocoder = new google.maps.Geocoder();
		
		function geocodeAddress(geocoder, resultsMap) {
			
			var address = document.getElementById('address').value;
			geocoder.geocode({'address': address}, function(results, status) {
				
				if (status === 'OK') {
					
					resultsMap.setCenter(results[0].geometry.location);
					
				} else {
					
					toastr.error('Geocode was not successful for the following reason: ' + status);
				}
			});
		}

    	document.getElementById('submit').addEventListener('click', function() {
        	geocodeAddress(geocoder, map);
        });
	}
});

angular.module('AngularApp.controllers').controller('PluginCtrl', function() {
});