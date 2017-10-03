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

angular.module('FrontModule.controllers').controller('HomeCtrl', function($scope, API) {
	
	$scope.latest_loading = true;
	$scope.countries_loading = true;
	
	$('#page-loading').addClass('hidden');
	$('#page-content').removeClass('hidden');
	
	API.sendRequest('/api/world/', 'GET').then(function(response) {

		response.sort(function(a, b) {
			return b.mosaics - a.mosaics;
		});
		
		$scope.firstCountries = response.slice(0,4);
		$scope.lastCountries = response.slice(4);
		
		$scope.countries_loading = false;
	});
	
	API.sendRequest('/api/latest/', 'GET').then(function(response) {
		
		$scope.mosaics = response;
		
		$scope.latest_loading = false;
	});
});

angular.module('FrontModule.controllers').controller('MosaicCtrl', function($scope, $window, API) {

	$scope.loadMosaic = function(ref) {
		
		API.sendRequest('/api/mosaic/' + ref + '/', 'GET').then(function(response) {
		
			$scope.mosaic = response;

			$scope.initMap();
			
			$('#page-loading').addClass('hidden');
			$('#page-content').removeClass('hidden');
		});
	}

	$scope.toggleMission = function(item) {
		
		if (!item.expanded) item.expanded = true;
		else item.expanded = false;
	}

	$scope.remove = function(mission_ref, index) {

		var data = { 'ref':$scope.mosaic.ref, 'mission':$scope.mosaic.missions[index] };
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

	$scope.initMap = function() {
		
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

	$scope.addComment = false;
	$scope.createComment = function(text) {
		
		$scope.addingComment = true;
		
		var data = { 'ref':$scope.mosaic.ref, 'text':text };
		API.sendRequest('/api/comment/add/', 'POST', {}, data).then(function(response) {
			
			$scope.mosaic.comments.unshift(response);
			
			$scope.addComment = false;
			$scope.addingComment = false;
		});
	}
	
	$scope.editComment = function(comment) {
		
		comment.editing = true;
		
		var data = { 'id':comment.id, 'text':comment.text };
		API.sendRequest('/api/comment/update/', 'POST', {}, data).then(function(response) {
			
			comment.edit = false;
			comment.editing = false;
		});
	}
	
	$scope.deleteComment = function(id, index) {
		
		var data = { 'id':id };
		API.sendRequest('/api/comment/delete/', 'POST', {}, data);
		
		$scope.mosaic.comments.splice(index, 1);
	}
});

angular.module('FrontModule.controllers').controller('SearchCtrl', function($scope, API) {
	
	$scope.mosaics = null;
	$scope.search_loading = false;
	
	$('#page-loading').addClass('hidden');
	$('#page-content').removeClass('hidden');

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
	
	var refArray = [];

	$rootScope.infowindow = new google.maps.InfoWindow({
		content: '',
		pixelOffset: new google.maps.Size(0, 0)
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
			
			var data = {'sLat':South_Lat, 'sLng':South_Lng, 'nLat':North_Lat, 'nLng':North_Lng};
			API.sendRequest('/api/map/', 'POST', {}, data).then(function(response) {
				
				if (response) {
					
					var contentLoading =
						'<div class="loading-line px-2 py-1">' +
						'	<img src="/static/img/loading.png" />' +
						'	Loading data...' +
						'</div>'
					;
					
					for (var item of response) {
					
						if (refArray.indexOf(item.ref) == -1) {
							
							refArray.push(item.ref);

							var latLng = new google.maps.LatLng(item.startLat, item.startLng);
							var marker = new google.maps.Marker({
								position: latLng,
								map: map,
								icon: image,
							});
							
							console.log(marker);
							
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
											if (details.missions.length > 24) contentClass = 'scrollbar';
											if (details.missions.length <= 24) contentClass = '';

											var contentDistance = '';
											if (details.type == 'sequence') contentDistance = details.distance.toFixed(2).toString() + ' km';
											if (details.type == 'serie') contentDistance = 'serie';
											if (details.type == 'sequence' && details.distance > 10.0 && details.distance < 30.0) contentDistance += '<span class="mx-1">&middot;</span><i class="fa fa-bicycle mx-1"></i>';
											if (details.type == 'sequence' && details.distance > 30.0) contentDistance += '<span class="mx-1">&middot;</span><i class="fa fa-car mx-1"></i>';

											var contentString =
												'<a class="btn-primary btn-block ta-left ttrans-normal" href="/mosaic/' + details.ref + '">' +
													
												'	<div class="item' + contentClass + '" style="margin-bottom:.25rem; display:flex; align-items:center; justify-content:center; background:#0b0c0d; height:105px; overflow-y:hidden; padding:.25rem;">' +
														
												'		<div class="row" style="align-items:center; justify-content:center; padding:0 calc((6 - ' + details.cols + ') / 2 * 16.666667%); width:100%;">' + contentImage + '</div>' +
														
												'	</div>' +
													
												'	<div class="f-col">' +
														
										        '    	<div class="text-white mt-2 mb-1" style="white-space:nowrap; text-overflow:ellipsis; overflow:hidden;">' + details.title + '</div>' +
										        '    	<div class="text-normal">' + details.missions.length + ' <i class="fa fa-th"></i> <span class="text-separator">&middot;</span>' + contentDistance + '</div>' +
										            	
												'	</div>' +
													
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
				});
				
			} else {
			}
		}
		
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
	}

	$scope.$on('user-loaded', function(event, args) {
		$scope.initMap($scope.initLocation);
	});
});

angular.module('FrontModule.controllers').controller('RegistrationCtrl', function($scope, $window, API) {
	
	$scope.$on('user-loaded', function(event, args) {
		
		$('#page-loading').addClass('hidden');
		$('#page-content').removeClass('hidden');
	});

	$scope.searchModel = {
		
		'text': null,
		'results': [],
	}
	
	$scope.searching = false;
	
	$scope.search = function() {
		
		$scope.searchModel.results = [];
		
		$('#searchButton').val('');
		$scope.searching = true;
		
		if (!$scope.searchModel.text) {
			$('#searchButton').val('Search');
			$scope.searching = false;
			return;
		}
		
		var data = {'text': $scope.searchModel.text}
		API.sendRequest('/api/missions/', 'POST', {}, data).then(function(response) {
			
			$scope.searchModel.results = response.missions;
			$('#searchButton').val('Search');
			$scope.searching = false;
		});
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
	}
			
	$scope.removeMission = function(item) {
		
		$scope.searchModel.results.push(item);
		
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
		
		$scope.searchModel.results.sort(compareCreatorTitleAsc);
	}
	
	$scope.reorder = function() {
		
		$scope.mosaicModel.missions.sort(compareOrderAsc);
	}
	
	$scope.addAll = function() {
		
		var missions = $scope.searchModel.results.slice();
		for (var m of missions) {
			$scope.addMission(m);
		}
	}
	
	$scope.addMission = function(item) {
		
		$scope.mosaicModel.missions.push(item);
		
		$scope.searchModel.results.splice($scope.searchModel.results.indexOf(item), 1);
		
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
						
						$scope.mosaicModel.city = $scope.mosaicModel.city.replace(/ō/g, 'o');
						
						if ($scope.mosaicModel.country == 'Japan') {
							
							$scope.mosaicModel.region = $scope.mosaicModel.region.replace(' Prefecture', '');
						
							if ($scope.mosaicModel.region.substring($scope.mosaicModel.region.length-4, $scope.mosaicModel.region.length) == '-ken') $scope.mosaicModel.region = $scope.mosaicModel.region.substring(0, $scope.mosaicModel.region.length-4);
							if ($scope.mosaicModel.city.substring($scope.mosaicModel.city.length-4, $scope.mosaicModel.city.length) == '-shi') $scope.mosaicModel.city = $scope.mosaicModel.city.substring(0, $scope.mosaicModel.city.length-4);
							if ($scope.mosaicModel.city.substring($scope.mosaicModel.city.length-4, $scope.mosaicModel.city.length) == '-cho') $scope.mosaicModel.city = $scope.mosaicModel.city.substring(0, $scope.mosaicModel.city.length-4);
						}
						
						$scope.$applyAsync();
					}
				}
			});
		}
		
		var order = 0;
		
		var found = item.title.match(/[0-9]+/);
		if (found) { order = parseInt(found[0]); }
		else {
		
			found = item.title.match(/(０|１|２|３|４|５|６|７|８|９)+/);
			if (found) {
				
				var arrayCharracter = ['３９','３８','３７','３６','３５','３４','３３','３２','３１','３０',
									   '２９','２８','２７','２６','２５','２４','２３','２２','２１','２０',
									   '１９','１８','１７','１６','１５','１４','１３','１２','１１','１０',
										 '９',  '８',  '７',  '６',  '５',  '４',  '３',  '２',  '１',  '０']
										 
				var arrayInteger = [39,38,37,36,35,34,33,32,31,30,
									29,28,27,26,25,24,23,22,21,20,
									19,18,17,16,15,14,13,12,11,10,
				                     9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
				
				for (var i in arrayCharracter) {
					
					found = item.title.match(arrayCharracter[i]);
					if (found) {
						order = arrayInteger[i];
						break;
					}
				}
			}
			
		}
		
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
		
		}, function(response) {
			
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

angular.module('FrontModule.controllers').controller('AdmRegionCtrl', function($scope, API) {
	
	$scope.loading_page = true;
	
	$scope.countries = [];

	API.sendRequest('/api/adm/countries', 'POST').then(function(response) {
		
		$scope.countries = response.countries;
		
		$scope.loading_page = false;
	
	$('#page-loading').addClass('hidden');
	$('#page-content').removeClass('hidden');
	});
	
	$scope.loading_regions = false;
	
	$scope.regions = null;

	$scope.refresh = function(countryName) {
		
		$scope.loading_regions = true;
		
		$scope.regions = null;
		
		if (!countryName) {
			
			$scope.loading_regions = false;
			return;
		}
		
		var data = {'country': countryName};
		API.sendRequest('/api/adm/regions', 'POST', {}, data).then(function(response) {
			
			$scope.regions = [];
			
			for (var item of response.regions) {
			
				var obj = {
					'name': item.name,
					'newname': item.name,
				};
				
				$scope.regions.push(obj);
			}
			
			$scope.loading_regions = false;
		});
	}
	
	$scope.rename = function(region) {
		
		var data = {'country': $scope.selected_country, 'region':region.name, 'new_region':region.newname};
		API.sendRequest('/api/adm/region/rename', 'POST', {}, data);
		
		region.name = region.newname
	}
});

angular.module('FrontModule.controllers').controller('AdmRegistrationCtrl', function($scope, API) {

	$scope.loading_page = true;
	
	$scope.mosaics = [];
	
	API.sendRequest('/api/adm/registration/mosaics/', 'POST').then(function(response) {
		
		$scope.mosaics = [];
		
		for (var item of response) {
			
			var obj = {
				
				'name': item.name,
				'count': item.count,
				
				'loading': false,
				'creating': false,
				
				'type': 'sequence',
				'title': item.name,
				'columns': '6',
				
				'city': null,
				'region': null,
				'country': null,
				
				'missions': [],
			}
			
			$scope.mosaics.push(obj);
		}

		$scope.loading_page = false;
	
	$('#page-loading').addClass('hidden');
	$('#page-content').removeClass('hidden');
	});
	
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
	
	$scope.refrech = function(mosaic) {
		
		mosaic.missions = [];
		
		mosaic.loading = true;

		var data = {'text': mosaic.name}
		API.sendRequest('/api/missions/', 'POST', {}, data).then(function(response) {
			
			if (!response.missions || response.missions.length < 1) {
				
				mosaic.loading = false;
				return;
			}
			
			mosaic.title = mosaic.name;
			
			mosaic.missions = response.missions;
			
			for (var item of mosaic.missions) {
				
				var order = 0;
				
				var found = item.title.match(/[0-9]+/);
				if (found) { order = parseInt(found[0]); }
				else {
				
					found = item.title.match(/(０|１|２|３|４|５|６|７|８|９)+/);
					if (found) {
						
						var arrayCharracter = ['３９','３８','３７','３６','３５','３４','３３','３２','３１','３０',
											   '２９','２８','２７','２６','２５','２４','２３','２２','２１','２０',
											   '１９','１８','１７','１６','１５','１４','１３','１２','１１','１０',
												 '９',  '８',  '７',  '６',  '５',  '４',  '３',  '２',  '１',  '０']
												 
						var arrayInteger = [39,38,37,36,35,34,33,32,31,30,
											29,28,27,26,25,24,23,22,21,20,
											19,18,17,16,15,14,13,12,11,10,
						                     9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
						
						for (var i in arrayCharracter) {
							
							found = item.title.match(arrayCharracter[i]);
							if (found) {
								order = arrayInteger[i];
								break;
							}
						}
					}
					else {
						
						found = item.title.match(/(①|②|③|④|⑤|⑥|⑦|⑧|⑨|⑩|⑪|⑫|⑬|⑭|⑮|⑯|⑰|⑱|⑲|⑳|㉑|㉒|㉓|㉔)+/);
						if (found) {
							
							if (found[0] == '①') order = 1;
							if (found[0] == '②') order = 2;
							if (found[0] == '③') order = 3;
							if (found[0] == '④') order = 4;
 							if (found[0] == '⑤') order = 5;
							if (found[0] == '⑥') order = 6;
							if (found[0] == '⑦') order = 7;
							if (found[0] == '⑧') order = 8;
							if (found[0] == '⑨') order = 9;
							if (found[0] == '⑩') order = 10;
							if (found[0] == '⑪') order = 11;
							if (found[0] == '⑫') order = 12;
							if (found[0] == '⑬') order = 13;
							if (found[0] == '⑭') order = 14;
							if (found[0] == '⑮') order = 15;
							if (found[0] == '⑯') order = 16;
							if (found[0] == '⑰') order = 17;
							if (found[0] == '⑱') order = 18;
							if (found[0] == '⑲') order = 19;
							if (found[0] == '⑳') order = 20;
							if (found[0] == '㉑') order = 21;
							if (found[0] == '㉒') order = 22;
							if (found[0] == '㉓') order = 23;
							if (found[0] == '㉔') order = 24;
						}
					}
				}
				
				item.order = order.toString();
			}
			
			mosaic.missions.sort(compareOrderAsc);
			
			var geocoder = new google.maps.Geocoder;
			
			var latlng = {
				lat: parseFloat(mosaic.missions[0].startLat),
				lng: parseFloat(mosaic.missions[0].startLng),
			};
			
			geocoder.geocode({'location': latlng, 'language': 'en'}, function(results, status) {
				
				if (status === 'OK') {
					
					var components = null;
					if (results[0]) components = results[0].address_components;
					if (results[1]) components = results[1].address_components;
					
					if (components) {
						
						var admin2 = null;
						var admin3 = null;
						
						for (var item of components) {
							
							if (item.types[0] == 'country') mosaic.country = item.long_name;
							if (item.types[0] == 'locality') mosaic.city = item.long_name;
							if (item.types[0] == 'administrative_area_level_1') mosaic.region = item.long_name;
							if (item.types[0] == 'administrative_area_level_2') admin2 = item.long_name;
							if (item.types[0] == 'administrative_area_level_3') admin3 = item.long_name;
						}
						
						if (!mosaic.city && admin2) mosaic.city = item.admin2;
						if (!mosaic.city && admin3) mosaic.city = item.admin3;
						
						
						if (mosaic.country == 'Japan') {
							
							if (mosaic.region) mosaic.region = mosaic.region.replace(/ō/g, 'o');
							if (mosaic.region) mosaic.region = mosaic.region.replace(/Ō/g, 'O');
							if (mosaic.region) mosaic.region = mosaic.region.replace(' Prefecture', '');
							if (mosaic.region && mosaic.region.substring(mosaic.region.length-3, mosaic.region.length) == '-to') mosaic.region = mosaic.region.substring(0, mosaic.region.length-3);
							if (mosaic.region && mosaic.region.substring(mosaic.region.length-3, mosaic.region.length) == '-fu') mosaic.region = mosaic.region.substring(0, mosaic.region.length-3);
							if (mosaic.region && mosaic.region.substring(mosaic.region.length-4, mosaic.region.length) == '-ken') mosaic.region = mosaic.region.substring(0, mosaic.region.length-4);
							
							if (mosaic.city) mosaic.city = mosaic.city.replace(/ō/g, 'o');
							if (mosaic.city) mosaic.city = mosaic.city.replace(/Ō/g, 'O');
							if (mosaic.city && mosaic.city.substring(mosaic.city.length-3, mosaic.city.length) == '-ku') mosaic.city = mosaic.city.substring(0, mosaic.city.length-3);
							if (mosaic.city && mosaic.city.substring(mosaic.city.length-4, mosaic.city.length) == '-son') mosaic.city = mosaic.city.substring(0, mosaic.city.length-4);
							if (mosaic.city && mosaic.city.substring(mosaic.city.length-4, mosaic.city.length) == '-shi') mosaic.city = mosaic.city.substring(0, mosaic.city.length-4);
							if (mosaic.city && mosaic.city.substring(mosaic.city.length-4, mosaic.city.length) == '-cho') mosaic.city = mosaic.city.substring(0, mosaic.city.length-4);
							if (mosaic.city && mosaic.city.substring(mosaic.city.length-5, mosaic.city.length) == '-mura') mosaic.city = mosaic.city.substring(0, mosaic.city.length-5);
							if (mosaic.city && mosaic.city.substring(mosaic.city.length-6, mosaic.city.length) == '-machi') mosaic.city = mosaic.city.substring(0, mosaic.city.length-6);
						}
						
						$scope.$applyAsync();
					}
				}
				
				mosaic.loading = false;
			});
		});
	}

	$scope.reorderMosaic = function(mosaic) {
		
		mosaic.missions.sort(compareOrderAsc);
	}
	
	$scope.removeMosaic = function(mosaic) {
		
		$scope.mosaics.splice($scope.mosaics.indexOf(mosaic), 1);
	}
	
	$scope.createMosaic = function(mosaic) {

		mosaic.creating = true;

		API.sendRequest('/api/mosaic/create/', 'POST', {}, mosaic).then(function(response) {

			$scope.mosaics.splice($scope.mosaics.indexOf(mosaic), 1);

			mosaic.creating = false;
		});
	}

	$scope.deleteMosaic = function(mosaic) {
		
		for (var m of mosaic.missions) {
			
			var data = { 'ref': m.ref };
			API.sendRequest('/api/mission/delete/', 'POST', {}, data);
		}
		
		$scope.mosaics.splice($scope.mosaics.indexOf(mosaic), 1);
	}
});