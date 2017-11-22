angular.module('FrontModule.controllers').controller('NewMosaicCtrl', function($scope, $window, toastr, API) {

	/* Lovers management */

	$scope.toggle_love = function(user) {
		
		if (!user.authenticated) {
			toastr.error('To perform this action you must be signed in! <a class="ml-small" href="/login" target="blank">Sign in</a>', {allowHtml: true});
		}
		else {
			
			$scope.mosaic.is_loved = !$scope.mosaic.is_loved;
			
			if ($scope.mosaic.is_loved) {
				
				$scope.mosaic.lovers += 1;
				
				var data = { 'ref':$scope.mosaic.ref };
	    		API.sendRequest('/api/mosaic/love/', 'POST', {}, data).then(function(response) {
	    			toastr.success('Mosaic added to your favorite list!');
	    		});
			}
			else {
				
				$scope.mosaic.lovers -= 1;
				
				var data = { 'ref':$scope.mosaic.ref };
	    		API.sendRequest('/api/mosaic/unlove/', 'POST', {}, data).then(function(response) {
	    			toastr.success('Mosaic removed from your favorite list!');
	    		});
			}
		}
	}

	/* Completers management */

	$scope.toggle_complete = function(user) {
		
		if (!user.authenticated) {
			toastr.error('To perform this action you must be signed in! <a class="ml-small" href="/login" target="blank">Sign in</a>', {allowHtml: true});
		}
		else {
			
			$scope.mosaic.is_completed = !$scope.mosaic.is_completed;
			
			if ($scope.mosaic.is_completed) {
				
				$scope.mosaic.completers += 1;
				
				var data = { 'ref':$scope.mosaic.ref };
	    		API.sendRequest('/api/mosaic/complete/', 'POST', {}, data);
			}
			else {
				
				$scope.mosaic.completers -= 1;
				
				var data = { 'ref':$scope.mosaic.ref };
	    		API.sendRequest('/api/mosaic/uncomplete/', 'POST', {}, data);
			}
		}
	}
	
	/* Mission details displaying */

	$scope.mission_selected = null;

	$scope.displayMissionDetails = function(mission) {
		
		$scope.mission_selected = mission;
	}

	$scope.closeMissionDetails = function() {
		
		$scope.mission_selected = null;
	}
	
	/* Comment edit displaying */
	
	$scope.comment_selected = null;
	
	$scope.displayCommentEdit = function(comment) {
		
		if (!comment) comment = { 'text':null }
		
		$scope.comment_selected = comment;
	}

	$scope.closeCommentEdit = function() {
		
		$scope.comment_selected = null;
	}
	
	$scope.saveComment = function(user, comment) {
		
		if (!user.authenticated) {
			toastr.error('To perform this action you must be signed in! <a class="ml-small" href="/login" target="blank">Sign in</a>', {allowHtml: true});
		}
		else {
			
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
	}
	
	$scope.deleteComment = function(user, index, comment) {
		
		if (!user.authenticated) {
			toastr.error('To perform this action you must be signed in! <a class="ml-small" href="/login" target="blank">Sign in</a>', {allowHtml: true});
		}
		else {
		
			var data = {'id':comment.id}
			API.sendRequest('/api/comment/delete/', 'POST', {}, data).then(function(response) {
				
				$scope.mosaic.comments.splice(index, 1);
			});
		}
	}
	
	/* Map management */
	
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
		for (var m of $scope.mosaic.missions) {
		
			if (m.ref.indexOf('Unavailable') !== -1) continue;
		
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

	        new google.maps.Marker({
	        	
				map: map,
				icon: image,
				label: label,
				position: {lat: m.startLat, lng: m.startLng},
	        });
	        
	        var mlatLng = new google.maps.LatLng(m.startLat, m.startLng);
	        latlngbounds.extend(mlatLng);
	        
	        index += 1;
		}
	        
		map.setCenter(latlngbounds.getCenter());
		map.fitBounds(latlngbounds); 
	}
	
	/* Tab management */
	
	$scope.current_tab = 0;
	
	$scope.open_tab = function(id) {
		
		$scope.current_tab = id;
	}
	
	/* Page loading */
	
	$scope.load_mosaic = function(ref) {
		
		API.sendRequest('/api/mosaic/' + ref + '/', 'GET').then(function(response) {
		
			$scope.mosaic = response;
			
			var temp = 0;
			if ($scope.mosaic.missions.length > $scope.mosaic.cols) {
				temp = $scope.mosaic.cols - $scope.mosaic.missions.length % $scope.mosaic.cols;
				if (temp < 0 || temp > ($scope.mosaic.cols - 1)) temp = 0;
			}
			
			$scope.offset = new Array(temp);
			
			$scope.open_tab(1);
			
			$scope.loaded = true;
		});
	}
});