angular.module('AngularApp.controllers', [])

angular.module('AngularApp.controllers').controller('RootCtrl', function($rootScope, $scope, $stateParams, $translate, $window, UserService) {
	
	var supported_lang = ['en', 'fr'];
	
	var user_lang = 'en';
	
	if ($stateParams.codelang) {
		
		if (supported_lang.indexOf($stateParams.codelang) != -1) user_lang = $stateParams.codelang;
      	$translate.use(user_lang);
	}
	else {
		
		var lang = $window.navigator.language || $window.navigator.userLanguage;
		if (supported_lang.indexOf(lang) != -1) user_lang = lang;
		
    	$window.location.href = '/' + user_lang + '/home';
	}
	
	$scope.user = UserService.data;
	
	$scope.logout = UserService.logout;
	
	$rootScope.menu_open = false;
	
	$scope.openMenu = function() {
		$rootScope.menu_open = true;
	}
	
	$scope.closeMenu = function() {
		$rootScope.menu_open = false;
	}
});

angular.module('AngularApp.controllers').controller('HomeCtrl', function($scope) {
	
	$scope.page_title = 'home_TITLE';
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
	
	$scope.missions = UserService.data.missions;
});

angular.module('AngularApp.controllers').controller('CreateCtrl', function($scope, $state, CreateService) {
	
	$scope.page_title = 'create_TITLE';
	
	$scope.data = null;

	if (CreateService.data.missions.length < 1) {
		$state.go('root.missions');
	}
	
	var geocoder = new google.maps.Geocoder;
	
	var latlng = {
		lat: parseFloat(CreateService.data.missions[0].lat),
		lng: parseFloat(CreateService.data.missions[0].lng),
	};

	geocoder.geocode({'location': latlng}, function(results, status) {
		
		if (status === 'OK') {
			if (results[1]) {
				
				for (var item of results[1].address_components) {
					
					if (item.types[0] == 'country') CreateService.data.country = item.long_name;
					if (item.types[0] == 'locality') CreateService.data.city = item.long_name;
					if (item.types[0] == 'administrative_area_level_1') CreateService.data.region = item.long_name;
				}
		
				$scope.$apply();
			}
		}
	});

	CreateService.default();

	$scope.data = CreateService.data;
	$scope.create = CreateService.create;

	$scope.rows = function() {
		
		var temp = 1;
		if ($scope.data.count > 0 && $scope.data.cols > 0) temp = Math.ceil($scope.data.count / $scope.data.cols);
		if (!temp) temp = 1;
		
		var rows = [];
		for (var i = 0; i < temp; i++) {
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
	
	$scope.rows = function() {
		
		var temp = 1;
		if ($scope.mosaic.count > 0 && $scope.mosaic.cols > 0) temp = Math.ceil($scope.mosaic.count / $scope.mosaic.cols);
		if (!temp) temp = 1;
		
		var rows = [];
		for (var i = 0; i < temp; i++) {
			rows.push(i);
		}
		
		return rows;
	}
	
	$scope.cols = function() {
		
		var temp = 1;
		if ($scope.mosaic.cols > 0) temp = $scope.mosaic.cols;
		if (!temp) temp = 1;
		
		var cols = [];
		for (var i = 0; i < temp; i++) {
			cols.push(i);
		}
		
		return cols;
	}
	
	$scope.getImage = function(i, j) {
		
		var order = (i * $scope.mosaic.cols + j) + 1;
		return MosaicService.getImageByOrder(order);
	}
	
	/* Edit */
	
	$scope.editMode = false;
	$scope.editLoading = false;
	
	$scope.editModel = {ref:null, city:null, region:null, desc:null, type:null, cols:null, count:null, title:null, country:null};
	
	$scope.openEdit = function() {
		
		$scope.editModel.ref = $scope.mosaic.ref;
		$scope.editModel.city = $scope.mosaic.city;
		$scope.editModel.desc = $scope.mosaic.desc;
		$scope.editModel.type = $scope.mosaic.type;
		$scope.editModel.cols = $scope.mosaic.cols;
		$scope.editModel.count = $scope.mosaic.count;
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
		
		MosaicService.add(item.ref);
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
			center: {lat: $scope.mosaic.missions[0].lat, lng: $scope.mosaic.missions[0].lng},
		});
		
		var latlngbounds = new google.maps.LatLngBounds();
		
		var roadmapCoordinates= [];
		
		var image = {
			size: new google.maps.Size(50, 50),
			origin: new google.maps.Point(0, 0),
			anchor: new google.maps.Point(25, 25),
			labelOrigin: new google.maps.Point(25, 27),
			url: 'https://www.myingressmosaics.com/static/front/img/neutral.png',
		};
		
		for (var m of $scope.mosaic.missions) {
		
	        var marker = new google.maps.Marker({
	        	
				map: map,
				icon: image,
				label: { text:String(m.order), color:'#FFFFFF', fontFamily:'Coda', fontSize:'.75rem', fontWeight:'400', },
				position: {lat: m.lat, lng: m.lng},
	        });
	        
	        var latLng = new google.maps.LatLng(m.lat,m.lng);
	        latlngbounds.extend(latLng);
	        
	        roadmapCoordinates.push(latLng);
		}
		
		var roadmap = new google.maps.Polyline({
			path: roadmapCoordinates,
			geodesic: true,
			strokeColor: '#ebbc4a',
			strokeOpacity: 0.95,
			strokeWeight: 4,
        });

        roadmap.setMap(map);
        
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

angular.module('AngularApp.controllers').controller('SearchCtrl', function($scope, $state, toastr, $filter, DataService) {
	
	/* Search */
	
	$scope.search_loading = false;
	
	$scope.searchModel = {text:null};
	
	$scope.search = function() {
		
		$scope.search_loading = true;
		
		$scope.cities = null;
		$scope.regions = null;
		$scope.mosaics = null;
		$scope.creators = null;
		$scope.countries = null;
		
		if ($scope.searchModel.text) {
			
			if ($scope.searchModel.text.length > 2) {
				
				DataService.search($scope.searchModel.text).then(function(response) {
					
					$scope.cities = response.cities;
					$scope.regions = response.regions;
					$scope.mosaics = response.mosaics;
					$scope.creators = response.creators;
					$scope.countries = response.countries;
					
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