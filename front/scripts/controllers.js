angular.module('FrontModule.controllers', [])

angular.module('FrontModule.controllers').controller('RootCtrl', function($rootScope, $auth, API) {
	
	API.sendRequest('/api/user/', 'GET').then(function(response) {
		
		if (response) {
			
			$rootScope.user = {
				name: response.name,
				faction: response.faction,
				superuser: response.superuser,
				authenticated: $auth.isAuthenticated(),
			}
		}
		else {
			
			$rootScope.user = {
				name: null,
				faction: null,
				superuser: false,
				authenticated: false,
			}
		}
		
		$rootScope.$broadcast('user-loaded');
	});

	$rootScope.menu_open = false;
	
	$rootScope.openMenu = function() {
		$rootScope.menu_open = true;
	}
	
	$rootScope.closeMenu = function() {
		$rootScope.menu_open = false;
	}
});

angular.module('FrontModule.controllers').controller('MosaicCtrl', function($scope, $window, API) {

	$scope.loadMosaic = function(ref) {
		
		API.sendRequest('/api/mosaic/' + ref + '/', 'GET').then(function(response) {
		
			$scope.mosaic = response;
			$scope.mosaic.cols = $scope.mosaic.cols.toString();

			$('#page-loading').addClass('hidden');
			$('#page-content').removeClass('hidden');
		});
	}

	$scope.toggleMission = function(item) {
		
		if (!item.expanded) item.expanded = true;
		else item.expanded = false;
	}

	$scope.remove = function(mission_ref, index) {

		var data = { 'ref':$scope.mosaic.ref, 'mission':$scope.mosaic.missions[index].ref };
		return API.sendRequest('/api/mosaic/remove/', 'POST', {}, data).then(function(response) {
				
			$scope.mosaic.creators = response.creators;
			$scope.mosaic.distance = response.distance;
			$scope.mosaic.missions = response.missions;
		});
	}

	function compareOrderAsc(a, b) {
		
		if (parseInt(a.order) < parseInt(b.order))
			return -1;
			
		if (parseInt(a.order) > parseInt(b.order))
			return 1;
		
		if (a.title < b.title)
			return -1;
			
		if (a.title > b.title)
			return 1;
			
		return 0;
	}
	
	$scope.reorderMission = function(index, ref, newOrder) {
		
		var data = { 'ref':ref, 'order':newOrder };
		API.sendRequest('/api/mission/order/', 'POST', {}, data);
		
		$scope.mosaic.missions[index].order = newOrder;
		$scope.mosaic.missions.sort(compareOrderAsc);
	}
	
	$scope.delete = function(name) {
		
		if (name == $scope.mosaic.title) {
			
			var data = { 'ref':$scope.mosaic.ref };
			API.sendRequest('/api/mosaic/delete/', 'POST', {}, data);
			
			$window.location.href = '/';
		}
	}

	$scope.mapInited = false;
	$scope.initMap = function() {
		
		if ($scope.mapInited) return;
		$scope.mapInited = true;
		
		var style = [{featureType:"all",elementType:"all",stylers:[{visibility:"on"},{hue:"#131c1c"},{saturation:"-50"},{invert_lightness:!0}]},{featureType:"water",elementType:"all",stylers:[{visibility:"on"},{hue:"#005eff"},{invert_lightness:!0}]},{featureType:"poi",stylers:[{visibility:"off"}]},{featureType:"transit",elementType:"all",stylers:[{visibility:"off"}]},{featureType:"road",elementType:"labels.icon",stylers:[{invert_lightness:!0}]}];
		
		var map = new google.maps.Map(document.getElementById('map'), {
			
			zoom: 8,
			styles : style,
			zoomControl: true,
			disableDefaultUI: true,
			fullscreenControl: true,
			center: {lat: $scope.mosaic.missions[0].startLat, lng: $scope.mosaic.missions[0].startLng},
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
		
			if (m.ref.indexOf('Unavailable') !== -1) {
				continue;
			}
		
			/* Mission marker */
			
			var label = {};
			if ($scope.mosaic.type == 'sequence') {
				label = { text:String(m.order), color:'#FFFFFF', fontFamily:'Coda', fontSize:'.5rem', fontWeight:'400', }
			}
			
	        var marker = new google.maps.Marker({
	        	
				map: map,
				icon: image,
				label: label,
				position: {lat: m.startLat, lng: m.startLng},
	        });
	        
	        var mlatLng = new google.maps.LatLng(m.startLat, m.startLng);
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
	
	$scope.love = function() {
	    
	    if (!$scope.mosaic.is_loved) {
	        
    		var data = { 'ref':$scope.mosaic.ref };
    		API.sendRequest('/api/mosaic/love/', 'POST', {}, data);
    	    
    	    $scope.mosaic.lovers += 1;
    	    $scope.mosaic.is_loved = true;
	    }
	    else if ($scope.mosaic.is_loved) {
	        
    		var data = { 'ref':$scope.mosaic.ref };
    		API.sendRequest('/api/mosaic/unlove/', 'POST', {}, data);
    	    
    	    $scope.mosaic.lovers -= 1;
    	    $scope.mosaic.is_loved = false;
	    }
	}
	
	$scope.complete = function() {
	    
	    if (!$scope.mosaic.is_completed) {
	        
    		var data = { 'ref':$scope.mosaic.ref };
    		API.sendRequest('/api/mosaic/complete/', 'POST', {}, data);
    	    
    	    $scope.mosaic.completers += 1;
    	    $scope.mosaic.is_completed = true;
	    }
	    else if ($scope.mosaic.is_completed) {
	        
    		var data = { 'ref':$scope.mosaic.ref };
    		API.sendRequest('/api/mosaic/uncomplete/', 'POST', {}, data);
    	    
    	    $scope.mosaic.completers -= 1;
    	    $scope.mosaic.is_completed = false;
	    }
	}
	
	$scope.updateMosaic = function() {
		
		$scope.updating = true;
		
		var data = { 'ref':$scope.mosaic.ref, 'city':$scope.mosaic.city, 'type':$scope.mosaic.type, 'cols':parseInt($scope.mosaic.cols), 'title':$scope.mosaic.title, 'region':$scope.mosaic.region, 'country':$scope.mosaic.country };
		API.sendRequest('/api/mosaic/edit/', 'POST', {}, data).then(function(response) {
			
			$scope.updating = false;
		});
	}
	
	$scope.addComment = false;
	$scope.addingComment = false;
	$scope.createComment = function(text) {
		
		if (!text) return;
		
		$scope.addingComment = true;
		
		var data = {'ref':$scope.mosaic.ref, 'text':text}
		API.sendRequest('/api/comment/add/', 'POST', {}, data).then(function(response) {
			
			$scope.mosaic.comments.push(response);
			
			$scope.addComment = false;
			$scope.addingComment = false;
		});
	}
	
	$scope.editComment = function(comment) {
		
		if (!comment.text) return;
		
		comment.editing = true;
		
		var data = {'id':comment.id, 'text':comment.text}
		API.sendRequest('/api/comment/update/', 'POST', {}, data).then(function(response) {
		
			comment.edit = false;
			comment.editing = false;
		});
	}
	
	$scope.deleteComment = function(id, index) {
		
		var data = {'id':id}
		API.sendRequest('/api/comment/delete/', 'POST', {}, data).then(function(response) {
			
			$scope.mosaic.comments.splice(index, 1);
		});
	}
	
	/* Adding fake missions */
	
	$scope.addFake = function(fakeorder) {
		
		var item = {
			'ref': 'Unavailable',
			'order': fakeorder,
			'title': 'Fake mission',
		}
		
		$scope.mosaic.missions.push(item);
		$scope.mosaic.missions.sort(compareOrderAsc);

		var data = {'ref':$scope.mosaic.ref, 'mission':item.ref, 'order':item.order};
		API.sendRequest('/api/mosaic/add/', 'POST', {}, data);
	}
	
	/* Adding missing missions */
	
	$scope.missions = []
	
	$scope.searching = false;
	
	$scope.displayResults = false;
	
	function compareOrderAsc(a, b) {
		
		if (parseInt(a.order) < parseInt(b.order))
			return -1;
			
		if (parseInt(a.order) > parseInt(b.order))
			return 1;
		
		if (a.title < b.title)
			return -1;
			
		if (a.title > b.title)
			return 1;
			
		return 0;
	}
	
	function compareCreatorTitleAsc(a, b) {
		
		if (a.creator < b.creator)
			return -1;
			
		if (a.creator > b.creator)
			return 1;
		
		if (a.title < b.title)
			return -1;
			
		if (a.title > b.title)
			return 1;
		
		return 0;
	}
	
	$scope.searchMission = function(searchtext) {
		
		$scope.missions = []
		$scope.searching = true;
		$scope.displayResults = true;
		
		var data = {'text':searchtext};
		API.sendRequest('/api/mosaic/missions/', 'POST', {}, data).then(function(response) {
			
			$scope.missions = response.missions;
			if (!$scope.missions) $scope.missions = [];
			else $scope.missions.sort(compareCreatorTitleAsc);
			
			$scope.searching = false;
		});
	}
	
	$scope.addMission = function(item) {
		
		$scope.missions.splice($scope.missions.indexOf(item), 1);

		$scope.mosaic.missions.push(item);
		$scope.mosaic.missions.sort(compareOrderAsc);

		var data = {'ref':$scope.mosaic.ref, 'mission':item.ref, 'order':item.order};
		API.sendRequest('/api/mosaic/add/', 'POST', {}, data);
	}
});

angular.module('FrontModule.controllers').controller('SearchCtrl', function($scope, API) {
	
	$scope.searchtext = null;
	$scope.mosaics = null;
	$scope.search_loading = false;
	
	$('#page-loading').addClass('hidden');
	$('#page-content').removeClass('hidden');

	$scope.init = function(text) {
		
		if (!text) return;
		
		$scope.searchtext = text;
		$scope.search(text);
	}

	$scope.search = function(text) {
		
		$scope.search_loading = true;
		
		$scope.mosaics = null;

		if (text) {
			
			if (text.length > 2) {
		
				var data = { 'text':text };
				API.sendRequest('/api/search/', 'POST', {}, data).then(function(response) {
					
					$scope.mosaics = response.mosaics;

					$scope.search_loading = false;
				});
			}
			else {
					
				$scope.search_loading = false;
			}
		}
		else {
				
			$scope.search_loading = false;
		}
	}
});

angular.module('FrontModule.controllers').controller('MapCtrl', function($scope, $rootScope, $cookies, $compile, API) {
	
	$('#page-loading').addClass('hidden');
	$('#page-content').removeClass('hidden');

	$rootScope.infowindow = new google.maps.InfoWindow({
		content: '',
		pixelOffset: new google.maps.Size(-1, 15)
	});

	$scope.initLocation = null;

	function createMap(startZoom, startLat, startLng, startBounds, geocoder) {
		
		var style = [{featureType:"all",elementType:"all",stylers:[{visibility:"on"},{hue:"#131c1c"},{saturation:"-50"},{invert_lightness:!0}]},{featureType:"water",elementType:"all",stylers:[{visibility:"on"},{hue:"#005eff"},{invert_lightness:!0}]},{featureType:"poi",stylers:[{visibility:"off"}]},{featureType:"transit",elementType:"all",stylers:[{visibility:"off"}]},{featureType:"road",elementType:"labels.icon",stylers:[{invert_lightness:!0}]}];
		
		var map = new google.maps.Map(document.getElementById('map'), {
			
			zoom: startZoom,
			styles : style,
			zoomControl: true,
			disableDefaultUI: true,
			center: {lat: startLat, lng: startLng},
		});
		
		if (startBounds) map.fitBounds(startBounds);
		
		function geolocate() {
		
		    if (navigator.geolocation) {
		
		        navigator.geolocation.getCurrentPosition(function (position) {
		
		            var pos = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
		            map.setCenter(pos);
		            map.setZoom(15);
		        });
		    }
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
		
		var geolocationDiv = document.createElement('div');
		var geolocationControl = new GeolocationControl(geolocationDiv, map);
		
		map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(geolocationDiv);
		
		var image = {
		    scaledSize: new google.maps.Size(25, 25),
			origin: new google.maps.Point(0, 0),
			anchor: new google.maps.Point(12, 13),
			url: 'https://commondatastorage.googleapis.com/ingress.com/img/map_icons/marker_images/enl_lev8.png',
		};
	
		var refArray = [];
		
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
			
			var data = {'sLat':South_Lat, 'sLng':South_Lng, 'nLat':North_Lat, 'nLng':North_Lng};
			API.sendRequest('/api/map/', 'POST', {}, data).then(function(response) {
				
				if (response) {
					
					var contentLoading =
						'<div class="ta-center">' +
						'	<i class="fa fa-spinner"></i>' +
						'	Loading data...' +
						'</div>'
					;
					
					for (var item of response) {
					
						var index = refArray.indexOf(item.ref)
						
						if (index == -1) {

							var latLng = new google.maps.LatLng(item.startLat, item.startLng);
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
									
									var data = {'ref':ref};
									API.sendRequest('/api/map/mosaic/', 'POST', {}, data).then(function(response) {
										
										if (response) {
											
											var details = response[0];
										
											var contentImage = '';
											for (var m of details.missions.reverse()) {
												
												contentImage +=	
												'<div style="flex:0 0 calc(100% / ' + details.cols + ');">' +
												'	<img src="/static/img/mask.png" style="width:100%; background-color:#000000; background-image:url(' + m.image + '=s100); background-size: 95% 95%; background-position: 50% 50%; float:left; background-repeat: no-repeat;" />' +
												'</div>'
												;
											}
											
											var contentClass = '';
											if (details.missions.length > 24) contentClass = 'scrollbar valign-start';
											if (details.missions.length <= 24) contentClass = 'valign-center';

											var contentDistance = '';
											if (details.type == 'sequence') contentDistance = details.distance.toFixed(2).toString() + ' km';
											if (details.type == 'serie') contentDistance = 'serie';
											if (details.type == 'sequence' && details.distance > 10.0 && details.distance < 30.0) contentDistance += '<span class="text-separator">&middot;</span><i class="fa fa-bicycle"></i>';
											if (details.type == 'sequence' && details.distance > 30.0) contentDistance += '<span class="text-separator">&middot;</span><i class="fa fa-car"></i>';
											
											var contentString =
												'<a class="btn-primary btn-block ta-left ttrans-normal" style="width:170px; font: 400 .75rem/1.5 \'Coda\',sans-serif;" href="/mosaic/' + details.ref + '">' +
													
												'	<div class="item ' + contentClass + '" style="margin-bottom:.25rem; display:flex; justify-content:center; background:#0b0c0d; height:105px; overflow-y:hidden; padding:.25rem;">' +
														
												'		<div class="row" style="align-items:center; justify-content:center; padding:0 calc((6 - ' + details.cols + ') / 2 * 16.666667%); width:100%;">' + contentImage + '</div>' +
														
												'	</div>' +
													
										        '    	<div class="ellipsis" style="margin-bottom:.25rem;">' + details.title + '</div>' +
											        '   <div class="c-lighter ellipsis">' +
											        '       <flag country="\'' + details.country + '\'"></flag>' +
											        details.location +
											        '   </div>' +
										        '    	<div class="c-lighter">' + details.missions.length + ' <i class="fa fa-th"></i> <span class="text-separator">&middot;</span>' + contentDistance + '</div>' +

												'</a>' +
											'';

											contentDiv = angular.element('<div/>');
											contentDiv.append(contentString);
											
											var compiledContent = $compile(contentDiv)($scope);
											
											infowindow.setContent(compiledContent[0]);
										}			
									});
								};
								
							})(marker, item.ref, $rootScope.infowindow));
							
							refArray.push(item.ref);
						}
					}
				}
			});
		});
		
		function geocodeAddress(geocoder, resultsMap) {
			
			var address = document.getElementById('address').value;
			geocoder.geocode({'address': address}, function(results, status) {
				
				if (status === 'OK') {
					
					resultsMap.setCenter(results[0].geometry.location);
					resultsMap.fitBounds(results[0].geometry.bounds);
					
				} else {
				}
			});
		}

    	document.getElementById('submit').addEventListener('click', function() {
        	geocodeAddress(geocoder, map);
        });
        
		return map;
	}

	$scope.initMap = function(location) {
		
		$scope.initLocation = location;
        
        var startLat = 0.0;
        var startLng = 0.0;
        
        var startBounds = null;
        
        var map = null;
	
		var geocoder = new google.maps.Geocoder();
        
        if (location) {
        	
        	document.getElementById('address').value = location;
			geocoder.geocode({'address': location}, function(results, status) {
				
				if (status === 'OK') {
					
					startLat = results[0].geometry.location.lat();
					startLng = results[0].geometry.location.lng();
					
					startBounds = results[0].geometry.bounds;
					
					map = createMap(15, startLat, startLng, startBounds, geocoder);
					
				} else {
				}
			});
        }
		else {
			
			startLat = parseFloat($cookies.get('startLat'));
			startLng = parseFloat($cookies.get('startLng'));
			
			var startZoom = parseInt($cookies.get('startZoom'));
			
			if (!startZoom) startZoom = 15;
			
			if (startLat == 0.0 && startLng == 0.0 && !location) {
				
				if (navigator.geolocation) {
					
					navigator.geolocation.getCurrentPosition(function(position) {
						
						startLat = position.coords.latitude;
						startLng = position.coords.longitude;
		
					}, function() {
					});
					
				} else {
				}
			}
		
			map = createMap(startZoom, startLat, startLng, null, geocoder);
		}
	}

	$scope.$on('user-loaded', function(event, args) {
		$scope.initMap($scope.initLocation);
	});
});

angular.module('FrontModule.controllers').controller('RegistrationCtrl', function($scope, $window, API, UtilsService) {
	
	$scope.mode_advanced = false;
	
	$scope.toggleAdvancedMode = function() {
		
		$scope.mode_advanced = !$scope.mode_advanced;
		
		if (!$scope.mode_advanced) $scope.refreshMissions();
		if ($scope.mode_advanced) $scope.refreshPotentials();
	}
	
	$scope.$on('user-loaded', function(event, args) {
		
		$('#page-loading').addClass('hidden');
		$('#page-content').removeClass('hidden');
		
		$scope.refreshMissions();
	});

	$scope.missions = [];
	$scope.filterText = '';

	var isMissionInArray = function(array, mission) {

		var index = -1;
		
		var temp = -1;
		for (var item of array) {

			temp += 1;
			
			if (item.ref == mission.ref) {
				
				index = temp;
				break;
			}
		}
		
		return index;
	}

	$scope.refreshingMissions = false;
	$scope.refreshMissions = function() {
	
		$scope.missions = [];
		$scope.filterText = '';
		$scope.refreshingMissions = true;
		
		API.sendRequest('/api/missions/', 'POST').then(function(response) {
			
			$scope.missions = response.missions;
			if (!$scope.missions) $scope.missions = [];
			else {
				
				for (var item of $scope.mosaicModel.missions) {
				
					var index = isMissionInArray($scope.missions, item);
					if (index != -1) $scope.missions.splice(index, 1);
				}
				
				$scope.missions.sort(compareCreatorTitleAsc);
			}
			
			$scope.refreshingMissions = false;
		});
	}

	$scope.filterMissions = function(text) {
		$scope.filterText = text;
	}

	$scope.mosaicModel = {
		
		'city': null,
		'type': 'sequence',
		'title': null,
		'region': null,
		'columns': '6',
		'country': null,
		
		'missions': [],
	}

	function compareOrderAsc(a, b) {
		
		if (parseInt(a.order) < parseInt(b.order))
			return -1;
			
		if (parseInt(a.order) > parseInt(b.order))
			return 1;
		
		if (a.title < b.title)
			return -1;
			
		if (a.title > b.title)
			return 1;
			
		return 0;
	}
	
	function compareCreatorTitleAsc(a, b) {
		
		if (a.creator < b.creator)
			return -1;
			
		if (a.creator > b.creator)
			return 1;
		
		if (a.title < b.title)
			return -1;
			
		if (a.title > b.title)
			return 1;
		
		return 0;
	}
	
	$scope.clearAll = function() {
		
		var missions = $scope.mosaicModel.missions.slice();
		for (var m of missions) {
			$scope.removeMission(m);
		}
		
		$window.scrollTo(0, 0);
	}
	
	$scope.removeMission = function(item) {
		
		$scope.missions.push(item);
		
		$scope.mosaicModel.missions.splice($scope.mosaicModel.missions.indexOf(item), 1);
		
		if ($scope.mosaicModel.missions.length < 1) {
			
			$scope.mosaicModel.city = null;
			$scope.mosaicModel.type = 'sequence';
			$scope.mosaicModel.title = null;
			$scope.mosaicModel.region = null;
			$scope.mosaicModel.columns = '6';
			$scope.mosaicModel.country = null;
		}
		else {
		
			$scope.mosaicModel.missions.sort(compareOrderAsc);
		}
		
		$scope.missions.sort(compareCreatorTitleAsc);
	}
	
	$scope.reorder = function() {
		
		$scope.mosaicModel.missions.sort(compareOrderAsc);
	}
	
	$scope.addAll = function() {
		
		var missions = $scope.missions.slice();
		for (var m of missions) {
			$scope.addMission(m);
		}
	}
	
	$scope.excludeAll = function() {
		
		var missions = $scope.searchModel.results.slice();
		for (var m of missions) {
			
			var data = { 'ref':m.ref }
			API.sendRequest('/api/mission/exclude/', 'POST', {}, data);
		}
	}
	
	$scope.addFake = function(fakeorder) {
		
		var item = {
			'ref': 'Unavailable',
			'order': fakeorder,
			'title': 'Fake mission',
		}
		
		$scope.addMission(item);
	}
	
	$scope.addMission = function(item) {
		
		$scope.mosaicModel.missions.push(item);
		
		$scope.missions.splice($scope.missions.indexOf(item), 1);
		
		if (!$scope.mosaicModel.title) {
			
			var mosaic_name = item.title;
			mosaic_name = mosaic_name.replace(/0|1|2|3|4|5|6|7|8|9|#/g, '');
			mosaic_name = mosaic_name.replace(/０|１|２|３|４|５|６|７|８|９/g, '');
			mosaic_name = mosaic_name.replace(/①|②|③|④|⑤|⑥/g, '');
			mosaic_name = mosaic_name.replace('.', '');
			mosaic_name = mosaic_name.replace('(', '');
			mosaic_name = mosaic_name.replace(')', '');
			mosaic_name = mosaic_name.replace('（', '');
			mosaic_name = mosaic_name.replace('）', '');
			mosaic_name = mosaic_name.replace('/', '');
			mosaic_name = mosaic_name.replace('[', '');
			mosaic_name = mosaic_name.replace(']', '');
			mosaic_name = mosaic_name.replace('【', '');
			mosaic_name = mosaic_name.replace('】', '');
			mosaic_name = mosaic_name.replace('-', '');
			mosaic_name = mosaic_name.replace('-', '');
			mosaic_name = mosaic_name.replace('－', '');
			mosaic_name = mosaic_name.replace('_', '');
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
			
			$scope.mosaicModel.title = mosaic_name;
		}
		
		if (!$scope.mosaicModel.country && !$scope.mosaicModel.region && !$scope.mosaicModel.city)  {
			
			var geocoder = new google.maps.Geocoder;
			
			var latlng = {
				lat: parseFloat($scope.mosaicModel.missions[0].startLat),
				lng: parseFloat($scope.mosaicModel.missions[0].startLng),
			};
			
			geocoder.geocode({'location': latlng}, function(results, status) {
				
				if (status === 'OK') {
					
					var components = null;
					if (results[0]) components = results[0].address_components;
					if (results[1]) components = results[1].address_components;
					
					if (components) {
						
						var admin2 = null;
						var admin3 = null;
						
						for (var item of components) {
							
							if (item.types[0] == 'country') $scope.mosaicModel.country = item.long_name;
							if (item.types[0] == 'locality') $scope.mosaicModel.city = item.long_name;
							if (item.types[0] == 'administrative_area_level_1') $scope.mosaicModel.region = item.long_name;
							if (item.types[0] == 'administrative_area_level_2') admin2 = item.long_name;
							if (item.types[0] == 'administrative_area_level_3') admin3 = item.long_name;
						}
						
						if (!$scope.mosaicModel.city && admin2) $scope.mosaicModel.city = item.admin2;
						if (!$scope.mosaicModel.city && admin3) $scope.mosaicModel.city = item.admin3;
						
						UtilsService.checkMosaicLocations($scope.mosaicModel);
						
						$scope.$applyAsync();
					}
				}
			});
		}
		
		var order = item.order;
		if (!item.order || item.order < 1) order = UtilsService.getOrderFromMissionName(item.title);
		item.order = order.toString();
		
		$scope.mosaicModel.missions.sort(compareOrderAsc);
	}
	
	$scope.creating = false;
	
	$scope.createMosaic = function() {

		$('#createButton').text('');
		$scope.creating = true;

		API.sendRequest('/api/mosaic/create/', 'POST', {}, $scope.mosaicModel).then(function(response) {

			var missions = $scope.mosaicModel.missions.slice();
			for (var m of missions) {
				$scope.mosaicModel.missions.splice($scope.mosaicModel.missions.indexOf(m), 1);
			}
			
			$scope.mosaicModel.city = null;
			$scope.mosaicModel.type = 'sequence';
			$scope.mosaicModel.title = null;
			$scope.mosaicModel.region = null;
			$scope.mosaicModel.columns = '6';
			$scope.mosaicModel.country = null;
		
			$window.open('https://www.myingressmosaics.com/mosaic/' + response);
			
			$('#createButton').text('Create');
			$scope.creating = false;
	
			$window.scrollTo(0, 0);
		});
	}
	
	$scope.deleteMission = function(item) {
		
		$scope.missions.splice($scope.missions.indexOf(item), 1);
		
		var data = {'ref':item.ref};
		API.sendRequest('/api/mission/exclude/', 'POST', {}, data);
	}
	
	/* Potentials management */
	
	$scope.potentials = [];
	$scope.refreshingPotentials = false;
	
	$scope.refreshPotentials = function() {
		
		$scope.potentials = [];
		$scope.refreshingPotentials = true;
		
		API.sendRequest('/api/potentials/', 'POST').then(function(response) {
			
			if (response) {
				for (var item of response) {
					
					var obj = {
						'city': null,
						'open': false,
						'type': 'sequence',
						'title': item.name,
						'count': item.count,
						'region': null,
						'columns': '6',
						'loading': false,
						'creating': false,
						'country': null,
						'missions': [],
					};
					
					$scope.potentials.push(obj);
				}
			}
			
			$scope.refreshingPotentials = false;
		});
	}
	
	$scope.togglePotential = function(potential) {
		
		potential.open = !potential.open;
		
		if (potential.open) {
			
			if (potential.missions.length < 1) $scope.refreshPotential(potential);
		}
	}
	
	$scope.refreshPotential = function(potential) {
		
		potential.missions = [];
		potential.loading = true;
		
		var data = {'name':potential.title};
		API.sendRequest('/api/potential/name/', 'POST', {}, data).then(function(response) {
			
			if (response) {
				
				potential.missions = response;
				
				var geocoder = new google.maps.Geocoder;
				
				var latlng = {
					lat: parseFloat(potential.missions[0].startLat),
					lng: parseFloat(potential.missions[0].startLng),
				};
				
				geocoder.geocode({'location': latlng}, function(results, status) {
					
					if (status === 'OK') {
						
						var components = null;
						if (results[0]) components = results[0].address_components;
						if (results[1]) components = results[1].address_components;
						
						if (components) {
							
							var admin2 = null;
							var admin3 = null;
							
							for (var item of components) {
								
								if (item.types[0] == 'country') potential.country = item.long_name;
								if (item.types[0] == 'locality') potential.city = item.long_name;
								if (item.types[0] == 'administrative_area_level_1') potential.region = item.long_name;
								if (item.types[0] == 'administrative_area_level_2') admin2 = item.long_name;
								if (item.types[0] == 'administrative_area_level_3') admin3 = item.long_name;
							}
							
							if (!potential.city && admin2) potential.city = item.admin2;
							if (!potential.city && admin3) potential.city = item.admin3;
							
							UtilsService.checkMosaicLocations(potential);
							
							$scope.$applyAsync();
						}
					}
				});
				
				for (var item of potential.missions) {
					
					var order = item.order;
					if (!item.order || item.order < 1) order = UtilsService.getOrderFromMissionName(item.title);
					item.order = order.toString();
				}
				
				potential.missions.sort(compareOrderAsc);
			}
			
			potential.loading = false;
		});
	}
	
	$scope.removeMissionFromPotential = function(potential, item) {
		
		potential.missions.splice(potential.missions.indexOf(item), 1);
		
		if (potential.missions.length < 1) {
			
			potential.city = null;
			potential.type = 'sequence';
			potential.title = null;
			potential.region = null;
			potential.columns = '6';
			potential.country = null;
		}
		else {
		
			potential.missions.sort(compareOrderAsc);
		}
	}
	
	$scope.reorderPotential = function(potential) {
		
		potential.missions.sort(compareOrderAsc);
	}
	
	$scope.addPotentialFake = function(potential, fakeorder) {
		
		var item = {
			'ref': 'Unavailable',
			'order': fakeorder,
			'title': 'Fake mission',
		}
		
		potential.missions.push(item);
		
		potential.missions.sort(compareOrderAsc);
	}
	
	$scope.createPotential = function(potential) {

		potential.creating = true;

		API.sendRequest('/api/mosaic/create/', 'POST', {}, potential).then(function(response) {

			$scope.potentials.splice($scope.potentials.indexOf(potential), 1);

			$window.open('https://www.myingressmosaics.com/mosaic/' + response);
		});
	}
});

angular.module('FrontModule.controllers').controller('LoginCtrl', function($scope, $auth, $cookies, $window, API) {
	
	$('#page-loading').addClass('hidden');
	$('#page-content').removeClass('hidden');
	
	$scope.unknown = false;
	$scope.signingin = false;
	
	$scope.socialLogin = function(provider) {
			
		$auth.authenticate(provider).then(function(response) {
			
			$auth.setToken(response.data.token);
			$cookies.token = response.data.token;
			
			$window.location.href = '/';
		});
	}
	
	$scope.localLogin = function(username, password) {
		
		$scope.unknown = false;
		$scope.signingin = true;
		
		var data = { 'username':username, 'password':password }
		API.sendRequest('/api/user/login/', 'POST', {}, data).then(function(response) {
			
			$auth.setToken(response.token);
			$cookies.token = response.token;
			
			$window.location.href = '/';
			
		}, function(response) {
			
			if (response == 'error_USER_UNKNOWN') $scope.unknown = true;
			
			$scope.signingin = false;
		});
	}
});

angular.module('FrontModule.controllers').controller('RegisterCtrl', function($scope, $auth, $cookies, $window, API) {
	
	$('#page-loading').addClass('hidden');
	$('#page-content').removeClass('hidden');
	
	$scope.already = false;
	$scope.passwords = false;
	$scope.registering = false;
	
	$scope.register = function(username, password1, password2, email) {
		
		$scope.already = false;
		$scope.passwords = false;
		$scope.registering = true;
		
		var data = { 'username':username, 'password1':password1, 'password2':password2, 'email':email }
		API.sendRequest('/api/user/register/', 'POST', {}, data).then(function(response) {
			
			$auth.setToken(response.token);
			$cookies.token = response.token;

			$window.location.href = '/';
			
		}, function(response) {
			
			if (response == 'error_USERNAME_ALREADY_EXISTS') $scope.already = true;
			if (response == 'error_PASSWORDS_NOT_EQUAL') $scope.passwords = true;
			
			$scope.registering = false;
		});
	}
});

angular.module('FrontModule.controllers').controller('ProfileCtrl', function($scope, $auth, $http, $cookies, $window, API) {
	
	API.sendRequest('/api/user/details/', 'POST').then(function(response) {
	
	    $scope.loved = response.loved;
	    $scope.completed = response.completed;
	});
	
	$scope.$on('user-loaded', function(event, args) {
		
		$('#page-loading').addClass('hidden');
		$('#page-content').removeClass('hidden');
	});

	$scope.editLoading = false;

	$scope.edit = function(newName, newFaction) {
		
		$scope.editLoading = true;
			
		var data = { 'name':newName, 'faction':newFaction };
		API.sendRequest('/api/user/edit/', 'POST', {}, data).then(function(response) {

			$scope.editLoading = false;
			
		}, function(response) {
			
			$scope.editLoading = false;
		});
	}
	
	$scope.logout = function() {
	    
		delete $http.defaults.headers.common.Authorization;
    	delete $cookies.token;
		
		$auth.removeToken();

		API.sendRequest('/api/user/logout/', 'POST').then(function(response) {
			
			$window.location.href = '/';
		});
	}
});

angular.module('FrontModule.controllers').controller('WorldCtrl', function($scope, API, GeoLabelService) {
	
	API.sendRequest('/api/world/', 'GET').then(function(response) {

		$scope.count = response.count;
		$scope.countries = response.countries;
		
		$scope.sortByMosaics();
		
		$('#page-loading').addClass('hidden');
		$('#page-content').removeClass('hidden');
	});
	
	$scope.sortByMosaics = function() {
		
		$scope.sort = 'mosaics';
		
		$scope.countries.sort(function(a, b) {
			return b.mosaics - a.mosaics;
		});
	}
	
	$scope.sortByName = function() {
		
		$scope.sort = 'name';
		
		$scope.countries.sort(function(a, b) {
			return a.name.localeCompare(b.name);
		});
	}
	
	$scope.getCountryLabel = GeoLabelService.getCountryLabel;
});

angular.module('FrontModule.controllers').controller('CountryCtrl', function($scope, API, GeoLabelService) {
	
	$scope.sort = 'mosaics';
	
	$scope.loadCountry = function(name) {
		
		$scope.country = name;
		
		API.sendRequest('/api/country/' + name + '/', 'GET').then(function(response) {
			
			$scope.count = response.count;
			$scope.regions = response.regions;
			
			$scope.sortByMosaics();
			
			for (var region of $scope.regions) {
				region.newname = region.name;
			}
			
			$('#page-loading').addClass('hidden');
			$('#page-content').removeClass('hidden');
		});
	}
	
	$scope.sortByMosaics = function() {
		
		$scope.sort = 'mosaics';
		
		$scope.regions.sort(function(a, b) {
			return b.mosaics - a.mosaics;
		});
	}
	
	$scope.sortByName = function() {
		
		$scope.sort = 'name';
		
		$scope.regions.sort(function(a, b) {
			return a.name.localeCompare(b.name);
		});
	}
	
	$scope.rename = function(region) {
		
		var data = {'country': $scope.country, 'region':region.name, 'new_region':region.newname};
		API.sendRequest('/api/adm/region/rename', 'POST', {}, data);
		
		region.name = region.newname
	}
	
	$scope.getCountryLabel = GeoLabelService.getCountryLabel;
	
	$scope.regionLocaleLabelMap = GeoLabelService.getRegionLocaleLabelMap($scope.country);

	$scope.getRegionLocaleLabel = function(enLabel) {
		
		var localeLabel = enLabel;
		
		var value = $scope.regionLocaleLabelMap.get(enLabel);
		if (value) localeLabel = value;
		
		return localeLabel;
	}
});

angular.module('FrontModule.controllers').controller('RegionCtrl', function($scope, API) {
	
	$scope.sort = 'mosaics';
	
	$scope.loadRegion = function(country, name) {
		
		$scope.country = country;
		$scope.region = name;
		
		API.sendRequest('/api/region/' + country + '/' + name + '/', 'GET').then(function(response) {

			$scope.count = response.count;
			$scope.cities = response.cities;
			
			$scope.sortByMosaics();
			
			for (var city of $scope.cities) {
				city.newname = city.name;
			}
			
			$('#page-loading').addClass('hidden');
			$('#page-content').removeClass('hidden');
		});
	}
	
	$scope.sortByMosaics = function() {
		
		$scope.sort = 'mosaics';
		
		$scope.cities.sort(function(a, b) {
			return b.mosaics - a.mosaics;
		});
	}
	
	$scope.sortByName = function() {
		
		$scope.sort = 'name';
		
		$scope.cities.sort(function(a, b) {
			return a.name.localeCompare(b.name);
		});
	}
	
	$scope.rename = function(city) {
		
		var data = {'country': $scope.country, 'region':$scope.region, 'city':city.name, 'new_city':city.newname};
		API.sendRequest('/api/adm/city/rename', 'POST', {}, data);
		
		city.name = city.newname
	}
});

angular.module('FrontModule.controllers').controller('CityCtrl', function($scope, API) {
	
	$scope.sort = 'missions';
	
	$scope.loadCity = function(country, region, name) {
		
		$scope.country = country;
		$scope.region = region;
		$scope.city = name;
		
		API.sendRequest('/api/city/' + country + '/' + region + '/' + name + '/', 'GET').then(function(response) {

			$scope.mosaics = response;
			
			$scope.sortByMissions();
			
			$('#page-loading').addClass('hidden');
			$('#page-content').removeClass('hidden');
		});
	}
	
	$scope.sortByMissions = function() {
		
		$scope.sort = 'missions';
		
		$scope.mosaics.sort(function(a, b) {
			return b.missions.length - a.missions.length;
		});
	}
	
	$scope.sortByName = function() {
		
		$scope.sort = 'name';
		
		$scope.mosaics.sort(function(a, b) {
			return a.title.localeCompare(b.title);
		});
	}
});

angular.module('FrontModule.controllers').controller('EventsCtrl', function($scope, API) {
	
	$('#page-loading').addClass('hidden');
	$('#page-content').removeClass('hidden');

	$scope.cities = [];
	$scope.selecting = false;
	$scope.selecttext = null;
	$scope.displayResults = false;

	$scope.init = function(text) {
		
		if (!text) return;
		$scope.select(text);
	}
	
	$scope.select = function(text) {
		
		$scope.cities = [];
		$scope.selecting = true;
		$scope.selecttext = text;
		$scope.displayResults = true;
		
		var data = {'event':text};
		API.sendRequest('/api/event/', 'POST', {}, data).then(function(response) {
			
			$scope.cities = response.cities;
			if (!$scope.cities) $scope.cities = [];

			$scope.cities.sort(function(a, b) {
				return b.mosaics.length - a.mosaics.length;
			});
			
			for (var city of $scope.cities) {
				city.mosaics.sort(function(a, b) {
					return b.missions.length - a.missions.length;
				});
			}

			$scope.selecting = false;
		});
	}
});

angular.module('FrontModule.controllers').controller('RecruitmentCtrl', function($scope, API) {
	
	$('#page-loading').addClass('hidden');
	$('#page-content').removeClass('hidden');
});