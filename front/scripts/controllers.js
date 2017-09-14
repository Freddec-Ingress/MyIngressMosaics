angular.module('FrontModule.controllers', [])

angular.module('FrontModule.controllers').controller('RootCtrl', function($rootScope, $scope, $translate, $window, UserService) {
	
	var supported_lang = ['en', 'fr'];
	
	var user_lang = 'en';
	
	var lang = $window.navigator.language || $window.navigator.userLanguage;
	if (supported_lang.indexOf(lang) != -1) user_lang = lang;
	
  	$translate.use(user_lang);

	$rootScope.user_loading = true;
	
	UserService.init().then(function(response) {
		
		$rootScope.user = UserService.data;
		
		$scope.logout = UserService.logout;
		
		if ($rootScope.user.authenticated) $('#authenticated_block').removeClass('hidden');
		if (!$rootScope.user.authenticated) $('#anonymous_block').removeClass('hidden');
		
		$scope.user_loading = false;
		
		$('#page-content').removeClass('hidden');
		
		$rootScope.$broadcast('user-loaded');
	});
	
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

angular.module('FrontModule.controllers').controller('HomeCtrl', function($scope, DataService) {
	
	$scope.latest_loading = true;
	
	DataService.loadLatest().then(function(response) {
		
		$scope.mosaics = response;
		
		$scope.latest_loading = false;
		
		$('#latest_block').removeClass('hidden');
	});

	$scope.countries_loading = true;
	
	DataService.loadCountriesFromWorld().then(function(response) {

		response.sort(function(a, b) {
			return b.mosaics - a.mosaics;
		});
		
		$scope.countries = response;
		
		$scope.countries_loading = false;
		
		$('#countries_block').removeClass('hidden');
	});
});

angular.module('FrontModule.controllers').controller('SearchCtrl', function($scope, toastr, $filter, SearchService) {
	
	/* Search */
	
	$scope.search_loading = false;
	
	$scope.searchModel = {text:SearchService.data.search_text};

	$scope.no_result = SearchService.data.no_result;
	
	$scope.mosaics = SearchService.data.mosaics;

	$('#result_block').removeClass('hidden');

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
});

angular.module('FrontModule.controllers').controller('MissionsCtrl', function($scope, UserService, CreateService) {

	var mosaics = [];
	var missions = [];
	
	$scope.missions_loading = true;
	
	UserService.getMissions().then(function(response) {
		
		var mis = UserService.data.missions;
		for (var mission of mis) {
			
			/* Mosaic name */
			var mosaic_name = mission.name;
			mosaic_name = mosaic_name.replace(/0|1|2|3|4|5|6|7|8|9|#/g, '');
			mosaic_name = mosaic_name.replace(/０|１|２|３|４|５|６|７|８|９/g, '');
			mosaic_name = mosaic_name.replace(/①|②|③|④|⑤|⑥/g, '');
			mosaic_name = mosaic_name.replace('.', '');
			mosaic_name = mosaic_name.replace('(', '');
			mosaic_name = mosaic_name.replace(')', '');
			mosaic_name = mosaic_name.replace('/', '');
			mosaic_name = mosaic_name.replace('[', '');
			mosaic_name = mosaic_name.replace(']', '');
			mosaic_name = mosaic_name.replace('-', '');
			mosaic_name = mosaic_name.replace('-', '');
			mosaic_name = mosaic_name.replace(':', '');
			mosaic_name = mosaic_name.replace('of ', '');
			mosaic_name = mosaic_name.replace(' of', '');
			mosaic_name = mosaic_name.replace('part ', '');
			mosaic_name = mosaic_name.replace(' part', '');
			mosaic_name = mosaic_name.replace('Part ', '');
			mosaic_name = mosaic_name.replace(' Part', '');
			mosaic_name = mosaic_name.replace('  ', ' ');
			mosaic_name = mosaic_name.replace('  ', ' ');
			mosaic_name = mosaic_name.replace('　', ' ');
			mosaic_name = mosaic_name.trim();
			
			/* Find existing mosaic */
			var existing_mosaic = null;
			for (var mosaic of mosaics) {
				if (mosaic.name.toLowerCase() == mosaic_name.toLowerCase()) {
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
		
		/* Sort mosaics by missions count */
		mosaics.sort(function(a, b) {
			return b.missions.length - a.missions.length;
		});
	
		$scope.mosaics = mosaics;
		$scope.missions = null;
		
		CreateService.init();
		
		$scope.selected_missions = CreateService.data.missions;
	
		UserService.sortMissionsByName('asc');
		
		$scope.sortName = 'asc';
		
		$scope.missions_loading = false;
	
		$scope.sortCreator = '';
		
		$('#missions_block').removeClass('hidden');
		
		$('#block-loading').addClass('hidden');
		$('#block-data').removeClass('hidden');
	});
	
	/* Create mosaic */
	$scope.createMosaic = function(mosaic) {
		
		CreateService.createWithMosaic(mosaic, $scope.createMosaicCallback);
	}
	$scope.createMosaicCallback = function(mosaic) {
		
		mosaic.creating = false;
		$scope.mosaics.splice($scope.mosaics.indexOf(mosaic), 1);
	}
	
	/* Delete mosaic */
	$scope.deleteMosaic = function(mosaic) {
		
		for (var item of mosaic.missions) {
			UserService.deleteMission(item);
		}
		
		$scope.mosaics.splice($scope.mosaics.indexOf(mosaic), 1);
	}
	
	/* Delete mission */
	$scope.delete = function(mosaic, item, index) {
		
		UserService.deleteMission(item);
		mosaic.missions.splice(index, 1);
	}
});

angular.module('FrontModule.controllers').controller('PluginCtrl', function() {
});

angular.module('FrontModule.controllers').controller('MosaicCtrl', function(API, $rootScope, $scope, $window, $filter, toastr, MosaicService) {

	$scope.loadMosaic = function(ref) {
		
		MosaicService.getMosaic(ref).then(function(response) {
			
			API.sendRequest('/api/mosaic/' + ref + '/', 'GET').then(function(response) {
			
				MosaicService.data.mosaic = response;
				
				$scope.mosaic = MosaicService.data.mosaic;
				$scope.potentials = MosaicService.data.potentials;
				
				$scope.initMap();
	
				$('#block-loading').addClass('hidden');
				
				if ($scope.mosaic) {
					
					$('#block-mosaic').removeClass('hidden');
					
					if ($rootScope.user && $rootScope.user.authenticated && ($rootScope.user.name == $scope.mosaic.registerer.name || $rootScope.user.superuser)) {
						
						$('#block-edit').removeClass('hidden');
					}
				}
				else {
					
					$('#block-nomosaic').removeClass('hidden');
				}
			});
		});
	}
		
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
		$scope.reorderMode = false;
		$scope.addMode = false;
		$scope.deleteMode = false;
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

		$scope.editMode = false;
		$scope.reorderMode = true;
		$scope.addMode = false;
		$scope.deleteMode = false;
	}
	
	$scope.closeReorder = function() {
		
		$scope.reorderMode = false;
	}
	
	$scope.remove = function(mission_ref, index) {

		$scope.reorderModel.missions.splice(index, 1);
		MosaicService.remove(mission_ref);
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
		
		$scope.editMode = false;
		$scope.reorderMode = false;
		$scope.addMode = true;
		$scope.deleteMode = false;
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
	
	$scope.deleteMode = false;
	
	$scope.deleteModel = {name:null};
	
	$scope.openDelete = function() {
		
		$scope.editMode = false;
		$scope.reorderMode = false;
		$scope.addMode = false;
		$scope.deleteMode = true;
	}
	
	$scope.closeDelete = function() {
		
		$scope.deleteMode = false;
	}
	
	$scope.delete = function() {
		
		if ($scope.deleteModel.name == $scope.mosaic.title) {
			
			MosaicService.delete();
			$window.location.href = '/';
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
			fullscreenControl: true,
			center: {lat: $scope.mosaic.missions[0].lat, lng: $scope.mosaic.missions[0].lng},
		});
		
		var latlngbounds = new google.maps.LatLngBounds();
		
		var image = {
			scaledSize: new google.maps.Size(35, 35),
			origin: new google.maps.Point(0, 0),
			anchor: new google.maps.Point(17, 18),
			labelOrigin: new google.maps.Point(17, 19),
			url: 'https://www.myingressmosaics.com/static/img/neutral.png',
		};
		
		var lineSymbol = {
			path: 'M 0,0 0,-5',
			strokeOpacity: 1,
			scale: 1
		};
		
		var circleSymbol = {
			path: google.maps.SymbolPath.CIRCLE
		};
		
		var nextlatLng = null;
		var previouslatLng = null;
		
		for (var m of $scope.mosaic.missions) {
		
			/* Mission marker */
			
			var label = {};
			if ($scope.mosaic.type == 'sequence') {
				label = { text:String(m.order), color:'#FFFFFF', fontFamily:'Coda', fontSize:'.5rem', fontWeight:'400', }
			}
			
	        var marker = new google.maps.Marker({
	        	
				map: map,
				icon: image,
				label: label,
				position: {lat: m.lat, lng: m.lng},
	        });
	        
	        var mlatLng = new google.maps.LatLng(m.lat, m.lng);
	        latlngbounds.extend(mlatLng);
	        
	        /* Mission transit */
	        
	        nextlatLng = mlatLng;
	        
	        if (nextlatLng && previouslatLng && $scope.mosaic.type == 'sequence') {
	        	
				var transitRoadmapCoordinates= [];
				
		        transitRoadmapCoordinates.push(previouslatLng);
		        transitRoadmapCoordinates.push(nextlatLng);
		        
				var transitRoadmap = new google.maps.Polyline({
					path: transitRoadmapCoordinates,
					geodesic: true,
					strokeColor: '#ebbc4a',
					strokeOpacity: 0,
					strokeWeight: 1,
					icons: [{
						icon: lineSymbol,
						offset: '0',
						repeat: '10px'
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
					icon: circleSymbol,
					offset: '100%',
				},],
			});
	        
	        roadmap.setMap(map);
	        
		}
		
		map.setCenter(latlngbounds.getCenter());
		map.fitBounds(latlngbounds); 
	}
});

angular.module('FrontModule.controllers').controller('MapCtrl', function($scope, $rootScope, $cookies, toastr, $filter, $compile, MapService) {
	
	/* Map */
	
	var refArray = [];

	$rootScope.infowindow = new google.maps.InfoWindow({
		content: '',
		pixelOffset: new google.maps.Size(5, 5)
	});

	$scope.initLocation = null;

	$scope.initMap = function(location) {
		
		$scope.initLocation = location;
		
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
		
		var geocoder = new google.maps.Geocoder();
        
        if (location) {
        	
        	document.getElementById('address').value = location;
			geocoder.geocode({'address': location}, function(results, status) {
				
				if (status === 'OK') {
					
					map.setCenter(results[0].geometry.location);
					map.fitBounds(results[0].geometry.bounds);
					
				} else {
					
					toastr.error('Geocode was not successful for the following reason: ' + status);
				}
			});
        }
		
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
		            map.setZoom(15);
		        });
		    }
		}
	
		var geolocationDiv = document.createElement('div');
		var geolocationControl = new GeolocationControl(geolocationDiv, map);
		
		map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(geolocationDiv);
		
		var image = {
		    scaledSize: new google.maps.Size(25, 25),
			origin: new google.maps.Point(0, 0),
			anchor: new google.maps.Point(12, 13),
			url: 'https://commondatastorage.googleapis.com/ingress.com/img/map_icons/marker_images/enl_lev8.png',
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
					
					var contentLoading =
							'<div class="loading">' +
								'<img src="/static/img/loading.png" />' +
							'</div>'
					;
					
					for (var item of response) {
					
						if (refArray.indexOf(item.ref) == -1) {
							
							refArray.push(item.ref);

							var latLng = new google.maps.LatLng(item._startLat, item._startLng);
							var marker = new google.maps.Marker({
								position: latLng,
								map: map,
								icon: image,
							});
							
							google.maps.event.addListener(marker, 'click', (function (marker, ref, infowindow) {
								
								return function () {
									
									var contentDiv = angular.element('<div/>');
									contentDiv.append(contentLoading);
									
									var compiledContent = $compile(contentDiv)($scope);
									
									infowindow.setContent(compiledContent[0]);
									infowindow.open($scope.map, marker);
									
									MapService.getMosaicDetails(ref).then(function(response) {
										
										if (response) {
											
											var details = response[0];
										
											var contentImage = '';
											for (var m of details.missions.reverse()) {
												
												contentImage +=	
													'<div style="flex:0 0 16.666667%;">' +
													    '<img src="/static/img/mask.png" style="width:100%; background-color:#000000; background-image:url(' + m.image + '=s10); background-size: 85% 85%; background-position: 50% 50%; float:left; background-repeat: no-repeat;" />' +
													'</div>'
												;
											}
											
											var contentString =
												'<a class="infoBlock" href="/mosaic/' + details.ref + '">' +
													'<div class="image">' + contentImage + '</div>' +
													'<div class="detail">' +
														'<div class="title">' + details.title + '</div>' +
														'<div class="info">' + details.count + ' missions <br> ' + details._distance.toFixed(2) + ' km &middot; ' + details.type + '</div>' +
													'</div>' +
												'</a>'
											;

											contentDiv = angular.element('<div/>');
											contentDiv.append(contentString);
											
											var compiledContent = $compile(contentDiv)($scope);
											
											infowindow.setContent(compiledContent[0]);
										}			
									});
								};
								
							})(marker, item.ref, $rootScope.infowindow));
						}
					}
				}
			});
		});
		
		if (startLat == 0.0 && startLng == 0.0 && !location) {
			
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
		
		function geocodeAddress(geocoder, resultsMap) {
			
			var address = document.getElementById('address').value;
			geocoder.geocode({'address': address}, function(results, status) {
				
				if (status === 'OK') {
					
					resultsMap.setCenter(results[0].geometry.location);
					resultsMap.fitBounds(results[0].geometry.bounds);
					
				} else {
					
					toastr.error('Geocode was not successful for the following reason: ' + status);
				}
			});
		}

    	document.getElementById('submit').addEventListener('click', function() {
        	geocodeAddress(geocoder, map);
        });
	}

	$scope.$on('user-loaded', function(event, args) {
		$scope.initMap($scope.initLocation);
	});
});

angular.module('FrontModule.controllers').controller('LoginCtrl', function($scope, UserService) {
	
	$scope.loginModel = { username:null, password:null };
	
	$scope.localLogin = UserService.localLogin;
	$scope.socialLogin = UserService.socialLogin;
});

angular.module('FrontModule.controllers').controller('RegisterCtrl', function($scope, UserService) {
	
	$scope.registerModel = { username:null, password1:null, password2:null, email:null };
	
	$scope.register = UserService.register;
});

angular.module('FrontModule.controllers').controller('ProfileCtrl', function($scope, UserService, toastr, $filter) {

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

angular.module('FrontModule.controllers').controller('SearchCtrl', function($scope, toastr, $filter, $window, SearchService) {
	
	/* Search */
	
	$('#result_block').removeClass('hidden');
	
	$scope.search_loading = false;
	
	$scope.searchModel = {text:SearchService.data.search_text};

	$scope.no_result = SearchService.data.no_result;
	
	$scope.mosaics = SearchService.data.mosaics;

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
});
