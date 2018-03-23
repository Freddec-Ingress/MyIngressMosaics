angular.module('FrontModule.controllers').controller('MosaicPageCtrl', function($scope, $window, API, UserService, $auth) {
	
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
			    		API.sendRequest('/api/mosaic/link/', 'POST', {}, data);
					}
					else {
						
						$scope.mosaic.likers -= 1;
						
						var data = { 'ref':$scope.mosaic.ref, 'type':type };
			    		API.sendRequest('/api/mosaic/unlink/', 'POST', {}, data);
					}
					break;
				
				case 'todo':
					$scope.mosaic.is_todo = !$scope.mosaic.is_todo;
					if ($scope.mosaic.is_todo) {
						
						$scope.mosaic.todoers += 1;
						
						var data = { 'ref':$scope.mosaic.ref, 'type':type };
			    		API.sendRequest('/api/mosaic/link/', 'POST', {}, data);
					}
					else {
						
						$scope.mosaic.todoers -= 1;
						
						var data = { 'ref':$scope.mosaic.ref, 'type':type };
			    		API.sendRequest('/api/mosaic/unlink/', 'POST', {}, data);
					}
					break;
				
				case 'complete':
					$scope.mosaic.is_complete = !$scope.mosaic.is_complete;
					if ($scope.mosaic.is_complete) {
						
						$scope.mosaic.completers += 1;
						
						var data = { 'ref':$scope.mosaic.ref, 'type':type };
			    		API.sendRequest('/api/mosaic/link/', 'POST', {}, data);
					}
					else {
						
						$scope.mosaic.completers -= 1;
						
						var data = { 'ref':$scope.mosaic.ref, 'type':type };
			    		API.sendRequest('/api/mosaic/unlink/', 'POST', {}, data);
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
				API.sendRequest('/api/comment/add/', 'POST', {}, data).then(function(response) {
				
					$scope.mosaic.comments.unshift(response);
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
				
				$scope.mosaic.comments.splice(index, 1);
			});
	}
	
	/* Tab management */
	
	$scope.current_tab = 'roadmap';
	
	/* Page loading */
	
	var mapInitiated = false;
	
	$scope.initMap = function() {
		
		if (mapInitiated) return;
		mapInitiated = true;
		
		var style = [{featureType:"all",elementType:"all",stylers:[{visibility:"on"},{hue:"#131c1c"},{saturation:"-50"},{invert_lightness:!0}]},{featureType:"water",elementType:"all",stylers:[{visibility:"on"},{hue:"#005eff"},{invert_lightness:!0}]},{featureType:"poi",stylers:[{visibility:"off"}]},{featureType:"transit",elementType:"all",stylers:[{visibility:"off"}]},{featureType:"road",elementType:"labels.icon",stylers:[{invert_lightness:!0}]}];
		
		var map = new google.maps.Map(document.getElementById('map'), {
			
			zoom: 8,
			styles: style,
			zoomControl: true,
			disableDefaultUI: true,
			fullscreenControl: true,
			center: {lat:$scope.mosaic.startLat, lng:$scope.mosaic.startLng},
		});
		
		var latlngbounds = new google.maps.LatLngBounds();
		
		var image = {
			scaledSize: new google.maps.Size(35, 35),
			origin: new google.maps.Point(0, 0),
			anchor: new google.maps.Point(17, 18),
			labelOrigin: new google.maps.Point(17, 19),
			url: 'https://www.myingressmosaics.com/static/img/neutral.png',
		};

		var index = 1;
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
	        
			var label = { text:String(index), color:'#FFFFFF', fontFamily:'Coda', fontSize:'.5rem', fontWeight:'400', }

	        var startMarker = new google.maps.Marker({
	        	
				map: map,
				icon: image,
				label: label,
				position: {lat: m.startLat, lng: m.startLng},
	        });
	        
	        var mlatLng = new google.maps.LatLng(m.startLat, m.startLng);
	        latlngbounds.extend(mlatLng);
	        
	        index += 1;
		}
	        
		map.fitBounds(latlngbounds); 
	}
	
	$scope.init = function(mosaic, missions, comments) {

		$scope.mosaic = mosaic;
		$scope.missions = missions;
		$scope.comments = comments;
		
		var temp = 0;
		if ($scope.missions.length > $scope.mosaic.cols) {
			temp = $scope.mosaic.cols - $scope.missions.length % $scope.mosaic.cols;
			if (temp < 0 || temp > ($scope.mosaic.cols - 1)) temp = 0;
		}
		
		$scope.offset = new Array(temp);

		$scope.initMap();
		
		$scope.loaded = true;
	}
});