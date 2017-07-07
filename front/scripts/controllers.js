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

angular.module('AngularApp.controllers').controller('MosaicCtrl', function($scope, $timeout, $window, $filter, toastr, MosaicService) {

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
	
	$scope.editModel = {ref:null, city:null, desc:null, type:null, cols:null, count:null, title:null, country:null};
	
	$scope.openEdit = function() {
		
		$scope.editModel.ref = $scope.mosaic.ref;
		$scope.editModel.city = $scope.mosaic.city;
		$scope.editModel.desc = $scope.mosaic.desc;
		$scope.editModel.type = $scope.mosaic.type;
		$scope.editModel.cols = $scope.mosaic.cols;
		$scope.editModel.count = $scope.mosaic.count;
		$scope.editModel.title = $scope.mosaic.title;
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
	
	$scope.add = function(item) {
		
		var index = $scope.potentials.indexOf(item);
		if (index > -1) {
		    $scope.potentials.splice(index, 1);
		}
		
		MosaicService.add(item.ref);
	}
	
	/* Delete */
	
	$scope.deleteModel = {name:null};
	
	$scope.delete = function() {
		
		if ($scope.deleteModel.name == $scope.mosaic.title) {
			
			MosaicService.delete();
		}
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
});

angular.module('AngularApp.controllers').controller('MyMosaicsCtrl', function($scope, $state, UserService) {
	
	$scope.page_title = 'mymosaics_TITLE';

	$scope.mosaics = UserService.data.mosaics;
	
	$scope.go = function(item) {
		$state.go('root.mosaic', {ref: item.ref});
	}
});

angular.module('AngularApp.controllers').controller('CountriesCtrl', function($scope, $state, DataService) {
	
	$scope.go = function(item) {
		
		DataService.setCountry(item.name);
		$state.go('root.cities');
	}

	/* Sort mosaics */
	
	DataService.sortCountriesByMosaics('desc');
	
	$scope.sortMosaics = 'desc';
	
	$scope.sortCountriesByMosaics = function() {
		
		$scope.sortName = '';
		
		if ($scope.sortMosaics == '' || $scope.sortMosaics == 'asc') {
			
			DataService.sortCountriesByMosaics('desc');
			$scope.sortMosaics = 'desc';
		}
		
		else if ($scope.sortMosaics == 'desc') {
			
			DataService.sortCountriesByMosaics('asc');
			$scope.sortMosaics = 'asc';
		}
	}
	
	/* Sort name */
	
	$scope.sortName = '';
	
	$scope.sortCountriesByName = function() {
		
		$scope.sortMosaics = '';
		
		if ($scope.sortName == '' || $scope.sortName == 'asc') {
			
			DataService.sortCountriesByName('desc');
			$scope.sortName = 'desc';
		}
		
		else if ($scope.sortName == 'desc') {
			
			DataService.sortCountriesByName('asc');
			$scope.sortName = 'asc';
		}
	}

	$scope.countries = DataService.countries;
});

angular.module('AngularApp.controllers').controller('CitiesCtrl', function($scope, $state, DataService) {

	$scope.country = DataService.current_country;

	$scope.go = function(item) {
		
		DataService.setCity(item.name);
		$state.go('root.mosaics');
	}

	/* Sort mosaics */
	
	DataService.sortCitiesByMosaics('desc');
	
	$scope.sortMosaics = 'desc';
	
	$scope.sortCitiesByMosaics = function() {
		
		$scope.sortName = '';
		
		if ($scope.sortMosaics == '' || $scope.sortMosaics == 'asc') {
			
			DataService.sortCountriesByMosaics('desc');
			$scope.sortMosaics = 'desc';
		}
		
		else if ($scope.sortMosaics == 'desc') {
			
			DataService.sortCitiesByMosaics('asc');
			$scope.sortMosaics = 'asc';
		}
	}
	
	/* Sort name */
	
	$scope.sortName = '';
	
	$scope.sortCitiesByName = function() {
		
		$scope.sortMosaics = '';
		
		if ($scope.sortName == '' || $scope.sortName == 'asc') {
			
			DataService.sortCitiesByName('desc');
			$scope.sortName = 'desc';
		}
		
		else if ($scope.sortName == 'desc') {
			
			DataService.sortCitiesByName('asc');
			$scope.sortName = 'asc';
		}
	}
	
	$scope.cities = DataService.cities;
});

angular.module('AngularApp.controllers').controller('MosaicsCtrl', function($scope, $state, DataService) {

	$scope.city = DataService.current_city;
	
	$scope.go = function(item) {
		
		$state.go('root.mosaic', {ref: item.ref});
	}
	
	/* Sort missions */
	
	DataService.sortMosaicsByMissions('desc');
	
	$scope.sortMissions = '';
	
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
	
	$scope.mosaics = DataService.mosaics;
});