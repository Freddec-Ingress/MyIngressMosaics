angular.module('FrontModule.controllers').controller('NewMapCtrl', function($scope, $window, $cookies, API) {
	
	/* Map management */
	
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
			url: 'https://commondatastorage.googleapis.com/ingress.com/img/map_icons/marker_images/enl_lev8.png',
		};
	
		var refArray = [];
		
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

				var geolocationControl = new GeolocationControl(geolocationDiv, map);
				map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(geolocationDiv);
		
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
		
		    	document.getElementById('submit').addEventListener('click', function() {
		        	geocodeAddress(geocoder, map);
		        });
			});
		}
	}
	
	/* Page loading */
	
	$scope.loaded = true;
});