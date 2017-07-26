angular.module('MapApp.controllers', [])

angular.module('MapApp.controllers').controller('MapCtrl', function($scope, $rootScope, $cookies, toastr, $filter, $compile, MapService) {
	
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
			url: 'https://www.myingressmosaics.com/static/img/marker.png',
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
									    '<img src="/static/img/mask.png" style="width:100%; background-color:#000000; background-image:url(' + m.image + '=s10); background-size: 85% 85%; background-position: 50% 50%; float:left; background-repeat: no-repeat;" />' +
									'</div>'
								;
							}
							
							var contentString =
								'<a class="infoBlock" href="/mosaic/' + item.ref + '})">' +
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