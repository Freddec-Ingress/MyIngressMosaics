angular.module('FrontModule.controllers').controller('MosaicPageCtrl', function($scope, $window, $compile, API, UserService, $auth) {
	
	$scope.signin = UserService.signin;

	$scope.authenticated = $auth.isAuthenticated();
    
	$('.hidden').each(function() { $(this).removeClass('hidden'); })

	/* Link management */

	$scope.toggle_link = function(type) {

		if ($scope.authenticated) {
			
			switch (type) {
				
				case 'like':
					$scope.mosaic.is_like = !$scope.mosaic.is_like;
					if ($scope.mosaic.is_like) {
						
						$scope.mosaic.likers += 1;
						
						var data = { 'ref':$scope.mosaic.ref, 'type':type };
			    		API.sendRequest('/api/link/create/', 'POST', {}, data);
					}
					else {
						
						$scope.mosaic.likers -= 1;
						
						var data = { 'ref':$scope.mosaic.ref, 'type':type };
			    		API.sendRequest('/api/link/delete/', 'POST', {}, data);
					}
					break;
				
				case 'todo':
					$scope.mosaic.is_todo = !$scope.mosaic.is_todo;
					if ($scope.mosaic.is_todo) {
						
						$scope.mosaic.todoers += 1;
						
						var data = { 'ref':$scope.mosaic.ref, 'type':type };
			    		API.sendRequest('/api/link/create/', 'POST', {}, data);
					}
					else {
						
						$scope.mosaic.todoers -= 1;
						
						var data = { 'ref':$scope.mosaic.ref, 'type':type };
			    		API.sendRequest('/api/link/delete/', 'POST', {}, data);
					}
					break;
				
				case 'complete':
					$scope.mosaic.is_complete = !$scope.mosaic.is_complete;
					if ($scope.mosaic.is_complete) {
						
						$scope.mosaic.completers += 1;
						
						var data = { 'ref':$scope.mosaic.ref, 'type':type };
			    		API.sendRequest('/api/link/create/', 'POST', {}, data);
					}
					else {
						
						$scope.mosaic.completers -= 1;
						
						var data = { 'ref':$scope.mosaic.ref, 'type':type };
			    		API.sendRequest('/api/link/delete/', 'POST', {}, data);
					}
					break;
			}
		}
		else {
			
			$scope.link_need_signin = true;
		}
	}

	/* Comment edit displaying */
	
	$scope.comment_selected = null;
	
	$scope.displayCommentEdit = function(comment) {
		
		if ($scope.authenticated) {
			
			if (!comment) comment = { 'text':null }
			
			$scope.comment_selected = comment;
		}
		else {
			
			$scope.comment_need_signin = true;
		}
	}

	$scope.closeCommentEdit = function() {
		
		$scope.comment_selected = null;
	}
	
	$scope.saveComment = function(user, comment) {
		
		if (!comment.text) return;
		
		if (!comment.id) {
			
			var data = {'ref':$scope.mosaic.ref, 'text':comment.text}
			API.sendRequest('/api/comment/create/', 'POST', {}, data).then(function(response) {
			
				$scope.comments.unshift(response);
				$scope.closeCommentEdit();
			});
		}
		else {
			
			var data = {'id':comment.id, 'text':comment.text}
			API.sendRequest('/api/comment/update/', 'POST', {}, data).then(function(response) {
			
				$scope.closeCommentEdit();
			});
		}
	}
	
	$scope.deleteComment = function(user, index, comment) {
		
		var data = {'id':comment.id}
		API.sendRequest('/api/comment/delete/', 'POST', {}, data).then(function(response) {
			
			$scope.comments.splice(index, 1);
		});
	}

	/* Mosaic management */
	
	$scope.markAsObsolete = function() {
		
		var data = { 'ref':$scope.mosaic.ref }
		API.sendRequest('/api/mosaic/obsolete/', 'POST', {}, data).then(function(response) {
		
			$scope.mosaic.is_obsolete = true;
		});
	}
	
	/* Tab management */
	
	$scope.current_tab = 'details';
	
	/* Page loading */
	
	var mapInitiated = false;
	
	$scope.initMap = function() {
		
		if (mapInitiated) return;
		mapInitiated = true;
		
		var style = [{featureType:"all",elementType:"all",stylers:[{visibility:"on"},{hue:"#131c1c"},{saturation:"-50"},{invert_lightness:!0}]},{featureType:"water",elementType:"all",stylers:[{visibility:"on"},{hue:"#005eff"},{invert_lightness:!0}]},{featureType:"poi",stylers:[{visibility:"off"}]},{featureType:"transit",elementType:"all",stylers:[{visibility:"off"}]},{featureType:"road",elementType:"labels.icon",stylers:[{invert_lightness:!0}]}];
		var styledMapType = new google.maps.StyledMapType(style, {name: 'Ingress Intel'});
		
		var mapType = 'Ingress Intel';
				
		var center = new google.maps.LatLng($scope.mosaic.startLat, $scope.mosaic.startLng);
		console.log('center: ' + center);
		
		var map = new google.maps.Map(document.getElementById('map'), {
			
			zoom:8,
			gestureHandling: 'greedy', 
			zoomControl: true,
			disableDefaultUI: true,
			fullscreenControl: true,
			mapTypeId: mapType,
			mapTypeControl: true,
			mapTypeControlOptions: {
				style: google.maps.MapTypeControlStyle.DROPDOWN_MENU,
                mapTypeIds: [google.maps.MapTypeId.ROADMAP, google.maps.MapTypeId.SATELLITE, google.maps.MapTypeId.HYBRID, google.maps.MapTypeId.TERRAIN, 'Ingress Intel'],
			},
			center:center,
		});
		
        map.mapTypes.set('Ingress Intel', styledMapType);
        map.setMapTypeId('Ingress Intel');
		        
		var latlngbounds = new google.maps.LatLngBounds();
		
		var image = {
			scaledSize: new google.maps.Size(50, 50),
			origin: new google.maps.Point(0, 0),
			anchor: new google.maps.Point(25, 25),
			labelOrigin: new google.maps.Point(25, 27),
			url: 'https://www.myingressmosaics.com/static/img/neutral.png',
		};

		for (var m of $scope.missions) {
		
			var roadmapCoordinates= [];
		
			for (var p of m.portals) {
				
				if (p.lat != 0.0 && p.lng != 0.0) {
					
			        var platLng = new google.maps.LatLng(p.lat, p.lng);
			        roadmapCoordinates.push(platLng);
			        
			        new google.maps.Marker({
			        	
						map: map,
						icon: {
				            path: google.maps.SymbolPath.CIRCLE,
				            strokeColor: '#ebbc4a',
				            scale: 2
				    	},
						position: {lat: p.lat, lng: p.lng},
			        });
				}
			}
	        
			var roadmap = new google.maps.Polyline({
				path: roadmapCoordinates,
				geodesic: true,
				strokeColor: '#ebbc4a',
				strokeOpacity: 0.95,
				strokeWeight: 2,
			});
	        
	        roadmap.setMap(map);
		}
		
		var index = 1;
		for (var m of $scope.missions) {
	        
			var label = { text:String(index), color:'#FFFFFF', fontFamily:'Coda', fontSize:'.9rem', fontWeight:'400', }

	        var startMarker = new google.maps.Marker({
	        	
				map: map,
				icon: image,
				label: label,
				zIndex: 1000,
				position: {lat: m.startLat, lng: m.startLng},
	        });
	        
	        var mlatLng = new google.maps.LatLng(m.startLat, m.startLng);
	        latlngbounds.extend(mlatLng);
	        
	        index += 1;
		}
	        
		map.fitBounds(latlngbounds);
		
		var zoom = map.getZoom();
		console.log('zoom: ' + zoom)
		var center = map.getCenter();
		console.log('center: ' + center)
		if (zoom > 7) {
			
			var image = {
			    scaledSize: new google.maps.Size(25, 25),
				origin: new google.maps.Point(0, 0),
				anchor: new google.maps.Point(12, 23),
				url: 'https://www.myingressmosaics.com/static/img/circle_sgl.png',
			};
			
			var infowindow = new google.maps.InfoWindow({
				content: '',
				pixelOffset: new google.maps.Size(-1, 15)
			});
			
			var south = latlngbounds.getSouthWest().lat();
			var west = latlngbounds.getSouthWest().lng();
			var north = latlngbounds.getNorthEast().lat();
			var east = latlngbounds.getNorthEast().lng();
			
			var data = {'sLat':south, 'sLng':west, 'nLat':north, 'nLng':east};
			API.sendRequest('/api/map/', 'POST', {}, data).then(function(response) {
				if (response) {
					
					console.log('loaded mosaics in map: ' + response.length);
					for (var item of response) {
						if (item.ref != $scope.mosaic.ref) {
							
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
						}
					}
				}
			});
		}
	}
	
	$scope.init = function(mosaic, missions, comments) {

		$scope.mosaic = mosaic;
		$scope.missions = missions;
		$scope.comments = comments;
		
		$scope.mosaic.distance = Number(($scope.mosaic.distance).toFixed(2));
		
		var temp = 0;
		if ($scope.missions.length > $scope.mosaic.column_count) {
			temp = $scope.mosaic.column_count - $scope.missions.length % $scope.mosaic.column_count;
			if (temp < 0 || temp > ($scope.mosaic.column_count - 1)) temp = 0;
		}
		
		$scope.offset = new Array(temp);

		$scope.initMap();
		
		$scope.loaded = true;
	}
});