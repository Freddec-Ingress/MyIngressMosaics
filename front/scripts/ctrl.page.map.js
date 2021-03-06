angular.module('FrontModule.controllers').controller('MapPageCtrl', function($scope, $window, $compile, API) {
	
	/* Mosaic list management */
	
	$scope.mosaic_list = false;
	
	$scope.openMosaicList = function() { $scope.mosaic_list = true; }
	$scope.closeMosaicList = function() { $scope.mosaic_list = false; }
	
	/* Map management */

	$scope.mosaics = [];

	$scope.flag_loading = true;
	$scope.flag_no_mosaic = false;
	$scope.flag_zoom_in = false;

	$scope.curTileCount = 0;
    $scope.curTileProcessed = 0;
				    
	$scope.initMap = function() {
		
		var map = null;
		
		var startZoom = 15;
		
		var style = [{featureType:"all",elementType:"all",stylers:[{visibility:"on"},{hue:"#131c1c"},{saturation:"-50"},{invert_lightness:!0}]},{featureType:"water",elementType:"all",stylers:[{visibility:"on"},{hue:"#005eff"},{invert_lightness:!0}]},{featureType:"poi",stylers:[{visibility:"off"}]},{featureType:"transit",elementType:"all",stylers:[{visibility:"off"}]},{featureType:"road",elementType:"labels.icon",stylers:[{invert_lightness:!0}]}];
		var styledMapType = new google.maps.StyledMapType(style, {name: 'Ingress Intel'});
		
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
		
		var image = {
		    scaledSize: new google.maps.Size(25, 25),
			origin: new google.maps.Point(0, 0),
			anchor: new google.maps.Point(12, 13),
			url: 'https://www.myingressmosaics.com/static/img/circle_sgl.png',
		};
	
		var refArray = [];
		var markerArray = [];
		
		var infowindow = new google.maps.InfoWindow({
			content: '',
			pixelOffset: new google.maps.Size(-1, 15)
		});

		var geocoder = new google.maps.Geocoder();
		
		function geocodeAddress(geocoder, resultsMap) {
			
			var address = document.getElementById('address').value;
			geocoder.geocode({'address': address}, function(results, status) {
				
				if (status === 'OK') {
					
					resultsMap.setCenter(results[0].geometry.location);
					resultsMap.fitBounds(results[0].geometry.bounds);
				}
			});
		}
		
		if (navigator.geolocation) {
			
			navigator.geolocation.getCurrentPosition(function(position) {
				
				var startLat = position.coords.latitude;
				var startLng = position.coords.longitude;
				
				var mapType = 'Ingress Intel';
				
				map = new google.maps.Map(document.getElementById('map'), {
					
					gestureHandling: 'greedy', 
					zoomControl: true,
					streetViewControl: true,
					disableDefaultUI: true,
					fullscreenControl: true,
					mapTypeId: mapType,
					mapTypeControl: true,
					mapTypeControlOptions: {
						style: google.maps.MapTypeControlStyle.DROPDOWN_MENU,
	                    mapTypeIds: [google.maps.MapTypeId.ROADMAP, google.maps.MapTypeId.SATELLITE, google.maps.MapTypeId.HYBRID, google.maps.MapTypeId.TERRAIN, 'Ingress Intel'],
					},
					center: {lat: startLat, lng: startLng},
					zoom: startZoom
		        });
		        
		        map.mapTypes.set('Ingress Intel', styledMapType);
		        map.setMapTypeId('Ingress Intel');
		        
				var imageMe = {
				    scaledSize: new google.maps.Size(25, 25),
					origin: new google.maps.Point(0, 0),
					anchor: new google.maps.Point(12, 13),
					url: 'https://www.myingressmosaics.com/static/img/marker_me.png',
				};
		
				var latLng = new google.maps.LatLng(startLat, startLng);
				var marker = new google.maps.Marker({
					position: latLng,
					map: map,
					icon: imageMe,
				});
		        
				var geolocationControl = new GeolocationControl(geolocationDiv, map);
				map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(geolocationDiv);

				function tileToLat(y, tilesPerEdge) {
				
				    var n = Math.PI - 2 * Math.PI * y / tilesPerEdge;
				    return 180 / Math.PI * Math.atan(0.5 * (Math.exp(n) - Math.exp(-n)));
				}
				
				function tileToLng(x, tilesPerEdge) {
				
				    return x / tilesPerEdge * 360 - 180;
				}
				
				var tilesProcessed = [];
				var tilesToBeProcessed = [];
				
				var tilesPerEdgeArray = [80,320,1000,2000,2000,4000,8000,16000,16000,32000];
				
				var loadedMosaics = [];
				
				map.addListener('idle', function(e) {
					
					$scope.curTileCount = 0;
				    $scope.curTileProcessed = 0;
				        
					$scope.flag_loading = true;
					$scope.flag_no_mosaic = false;
					$scope.flag_zoom_in = false;
					
					var bds = map.getBounds();
					
					var South_Lat = bds.getSouthWest().lat();
					var South_Lng = bds.getSouthWest().lng();
					var North_Lat = bds.getNorthEast().lat();
					var North_Lng = bds.getNorthEast().lng();
					
					console.log('bounds: (' + North_Lat + ',' + North_Lng + ')(' + South_Lat + ',' + South_Lng + ')')
					
					var zoom = map.getZoom();
					console.log('zoom: ' + zoom)
					if (zoom > 10) {
						
						var tilesPerEdge = tilesPerEdgeArray[zoom-10];
				
				        var xStart = Math.floor((South_Lng + 180) / 360 * tilesPerEdge);
				        var xEnd = Math.floor((North_Lng + 180) / 360 * tilesPerEdge);
				
				        var yStart = Math.floor((1 - Math.log(Math.tan(North_Lat * Math.PI / 180) + 1 / Math.cos(North_Lat * Math.PI / 180)) / Math.PI) / 2 * tilesPerEdge);
				        var yEnd = Math.floor((1 - Math.log(Math.tan(South_Lat * Math.PI / 180) + 1 / Math.cos(South_Lat * Math.PI / 180)) / Math.PI) / 2 * tilesPerEdge);
				        
				        $scope.curTileCount = (xEnd - xStart) * (yEnd - yStart);
				        
				        for (var x = xStart; x <= xEnd; x++) {
				            for (var y = yStart; y <= yEnd; y++) {
								
								$scope.curTileProcessed += 1;
								$scope.$apply();
								
								var tile_id = x + '_' + y;
				                if (tilesProcessed.indexOf(tile_id) == -1 && tilesToBeProcessed.indexOf(tile_id) == -1) {
									
									tilesToBeProcessed.push(tile_id);
								
				                    var south = tileToLat(y + 1, tilesPerEdge);
				                    var north = tileToLat(y, tilesPerEdge);
				                    var west = tileToLng(x, tilesPerEdge);
				                    var east = tileToLng(x + 1, tilesPerEdge);
				                    
									var data = {'sLat':south, 'sLng':west, 'nLat':north, 'nLng':east};
									API.sendRequest('/api/map/', 'POST', {}, data).then(function(response) {
										
										tilesProcessed.push(tile_id);
										tilesToBeProcessed.splice(tilesToBeProcessed.indexOf(tile_id), 1);
										
										if (response) {
											
											for (var mosaic of response) {
												if (loadedMosaics.findIndex(function(element, index, array) { return element.ref == mosaic.ref; }) == -1) {
													loadedMosaics.push(mosaic);
												}
											}
											console.log('loaded mosaics count: ' + loadedMosaics.length);
											
											for (var item of response) {
											
												var index = refArray.indexOf(item.ref)
												
												if (index == -1) {
						
													var latLng = new google.maps.LatLng(item.startLat, item.startLng);
													var marker = new google.maps.Marker({
														position: latLng,
														map: map,
														icon: image,
													});
													
													google.maps.event.addListener(marker, 'click', (function (marker, mosaic, infowindow) {
														
														return function () {
															
															var offset_string = '';
															
															var temp = 0;
															if (mosaic.images.length > mosaic.column_count) {
																temp = mosaic.column_count - mosaic.images.length % mosaic.column_count;
																if (temp < 0 || temp > (mosaic.column_count - 1)) temp = 0;
															}
															
															for (var i = 0; i < temp; i++) {
																offset_string += '<div style="flex:0 0 calc(100% / ' + mosaic.column_count + ');"></div>';
															}
															
															var missions_string = '';
															
															var missions_array = mosaic.images.slice();
															for (var mission of missions_array) {
																
																missions_string +=
														            '<div class="mission-vignet" style="flex:0 0 calc(100% / ' + mosaic.column_count + ');">' +
														                '<img src="/static/img/mask.png" style="z-index:auto; background-image:url(' + mission + '=s25);" />' +
														            '</div>';
															}
															
															var contentString = '' +
																'<a class="flex-col" target="_blank" style="width:200px; min-width:200px; max-width:200px;" href="/mosaic/' + mosaic.ref + '" >' +
																	'<div class="flex-col" style="flex-shrink:1;">' + 
																		'<span class="color-black text-medium text-bold ellipsis" style="word-break: break-all;" title="' + mosaic.title + '">' + mosaic.title + '</span>' + 
																		'<span class="color-grey text-small">' + mosaic.images.length + ' missions &middot; ' + mosaic.unique_count + ' uniques</span>' + 
																		'<span class="color-link text-small mb-small">See details</span>' + 
																	'</div>' + 
																	'<div style="max-height:400px; overflow-y:auto;">' +
																		'<div class="flex wrap shrink" style="padding:0 calc((6 - ' + mosaic.column_count + ') / 2 * 16.666667%);">' +
																			offset_string +
																			missions_string + 
																		'</div>' +
																	'</div>' + 
																'</a>';
																'';
															
															var contentDiv = angular.element('<div/>');
															contentDiv.append(contentString);													
															
															var compiledContent = $compile(contentDiv)($scope);
															
															infowindow.setContent(compiledContent[0]);
															infowindow.open($scope.map, marker);
														};
														
													})(marker, item, infowindow));
													
													refArray.push(item.ref);
													markerArray.push(marker);
												}
											}
										}
										
										if (tilesToBeProcessed.length < 1) {
					
											$scope.mosaics = [];
											for (var mosaic of loadedMosaics) {
												console.log('mosaic start point: (' + mosaic.startLat + ',' + mosaic.startLng + ')');
												if (mosaic.startLat >= South_Lat && mosaic.startLat <= North_Lat && mosaic.startLng >= South_Lng && mosaic.startLng <= North_Lng) {
												 	$scope.mosaics.push(mosaic);
													console.log('mosaic displayed');
												}
											}

											$scope.flag_loading = false;
										}
									});
				                }
				                else {
				                	
				                	if (x == xEnd && y == yEnd) {
				                		$scope.flag_loading = false;
				                	}
				                }
				            }
				        }
					}
					else {
						$scope.flag_loading = false;
						$scope.flag_zoom_in = true;
					}
					
					$scope.$apply();
					console.log('flag zoom in:' + $scope.flag_zoom_in);
				});
		
		    	document.getElementById('submit').addEventListener('click', function() {
		        	geocodeAddress(geocoder, map);
		        });
		        
		        var input = document.getElementById('address');
		        
		        var autocomplete = new google.maps.places.Autocomplete(input);
		        autocomplete.bindTo('bounds', map);
		        
		        autocomplete.addListener('place_changed', function() {
		        	geocodeAddress(geocoder, map);
		        });
			});
		}
	}
	
	/* Page loading */
	
	$scope.loaded = true;
});