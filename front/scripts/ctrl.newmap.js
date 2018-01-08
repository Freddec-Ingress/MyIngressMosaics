angular.module('FrontModule.controllers').controller('NewMapCtrl', function($scope, $window, $compile, API) {
	
	/* Map management */

	$scope.mosaics = [];

	$scope.flag_loading = true;
	$scope.flag_no_mosaic = false;

	$scope.initMap = function() {
		
		var map = null;
		
		var startZoom = 15;
		
		var style = [{featureType:"all",elementType:"all",stylers:[{visibility:"on"},{hue:"#131c1c"},{saturation:"-50"},{invert_lightness:!0}]},{featureType:"water",elementType:"all",stylers:[{visibility:"on"},{hue:"#005eff"},{invert_lightness:!0}]},{featureType:"poi",stylers:[{visibility:"off"}]},{featureType:"transit",elementType:"all",stylers:[{visibility:"off"}]},{featureType:"road",elementType:"labels.icon",stylers:[{invert_lightness:!0}]}];
		
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
				
				map = new google.maps.Map(document.getElementById('map'), {
					
					styles : style,
					zoomControl: true,
					disableDefaultUI: true,
					center: {lat: startLat, lng: startLng},
					zoom: startZoom
		        });
		        
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

				map.addListener('idle', function(e) {
					
					$scope.mosaics = [];
					
					$scope.flag_loading = true;
					$scope.flag_no_mosaic = false;
					
					var bds = map.getBounds();
					
					var South_Lat = bds.getSouthWest().lat();
					var South_Lng = bds.getSouthWest().lng();
					var North_Lat = bds.getNorthEast().lat();
					var North_Lng = bds.getNorthEast().lng();
					
					var data = {'sLat':South_Lat, 'sLng':South_Lng, 'nLat':North_Lat, 'nLng':North_Lng};
					API.sendRequest('/api/map/', 'POST', {}, data).then(function(response) {
						
						if (response) {
							
							$scope.mosaics = response;
							
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
											if (mosaic.missions.length > mosaic.cols) {
												temp = mosaic.cols - mosaic.missions.length % mosaic.cols;
												if (temp < 0 || temp > (mosaic.cols - 1)) temp = 0;
											}
											
											for (var i = 0; i < temp; i++) {
												offset_string += '<div style="flex:0 0 calc(100% / ' + mosaic.cols + ');"></div>';
											}
											
											var missions_string = '';
											
											for (var mission of mosaic.missions) {
												
												missions_string +=
										            '<div class="mission-vignet" style="flex:0 0 calc(100% / ' + mosaic.cols + ');">' +
										                '<img src="/static/img/mask.png" style="width:100%; background-color:#000000; background-image:url(' + mission.image + '=s100); background-size: 95% 95%; background-position: 50% 50%; float:left; background-repeat: no-repeat;" />' +
										            '</div>';
											}
											
											var contentString = '' +
												'<a class="flex" target="_blank" href="/mosaic/' + mosaic.ref + '" >' +
													'<div class="item" style="width:125px; max-width:125px; max-height:102px; overflow-y:auto;">' +
														'<div class="flex wrap shrink justify-center" style="padding:0 calc((6 - ' + mosaic.cols + ') / 2 * 16.666667%);">' +
															offset_string +
															missions_string + 
														'</div>' +
													'</div>' + 
													'<div class="item flex-col">' + 
														'<span class="color-black mb-small text-bold">' + mosaic.title + '</span>' + 
														'<span class="color-grey mb-normal">' + mosaic.missions.length + ' missions</span>' + 
														'<span class="color-link">Open mosaic page</span>' + 
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
							
							var markerCluster = new MarkerClusterer(map, markerArray, { imagePath: 'https://www.myingressmosaics.com/static/img/m' });
							markerCluster.setMaxZoom(10);
							
							$scope.flag_loading = false;
						}
						else {
							
							$scope.mosaics = [];
							
							$scope.flag_no_mosaic = true;
							$scope.flag_loading = false;
						}
					});
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