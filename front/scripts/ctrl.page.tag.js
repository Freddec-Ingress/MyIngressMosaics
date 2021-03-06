angular.module('FrontModule.controllers').controller('TagPageCtrl', function($scope, $window, $compile, API) {
	
	/* Tab management */
	
	$scope.current_tab = 'map';
	
	/* Index management */
	
	$scope.indexes_by_country = []
	$scope.mosaics_by_country = null;
	$scope.current_by_country_index = null;
	
	$scope.setByCountryIndex = function(index) {
		
		$scope.mosaics_by_country = index.mosaics;
		$scope.current_by_country_index = index;
	}
	
	/*----------*/
	
	$scope.indexes_by_mission = []
	$scope.mosaics_by_mission = null;
	$scope.current_by_mission_index = null;
	
	$scope.setByMissionIndex = function(index) {
		
		$scope.mosaics_by_mission = index.mosaics;
		$scope.current_by_mission_index = index;
	}
	
	/* Page loading */
	
	var mapInitiated = false;
	
	$scope.initMap = function(mosaics) {
		
		if (mapInitiated) return;
		mapInitiated = true;
		
		var style = [{featureType:"all",elementType:"all",stylers:[{visibility:"on"},{hue:"#131c1c"},{saturation:"-50"},{invert_lightness:!0}]},{featureType:"water",elementType:"all",stylers:[{visibility:"on"},{hue:"#005eff"},{invert_lightness:!0}]},{featureType:"poi",stylers:[{visibility:"off"}]},{featureType:"transit",elementType:"all",stylers:[{visibility:"off"}]},{featureType:"road",elementType:"labels.icon",stylers:[{invert_lightness:!0}]}];
		var styledMapType = new google.maps.StyledMapType(style, {name: 'Ingress Intel'});
		
		var mapType = 'Ingress Intel';
				
		var map = new google.maps.Map(document.getElementById('map'), {
			
			zoom: 20,
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
			center: {lat:mosaics[0].startLat, lng:mosaics[0].startLng},
		});
		
        map.mapTypes.set('Ingress Intel', styledMapType);
        map.setMapTypeId('Ingress Intel');
        
		var image = {
		    scaledSize: new google.maps.Size(25, 25),
			origin: new google.maps.Point(0, 0),
			anchor: new google.maps.Point(12, 13),
			url: 'https://www.myingressmosaics.com/static/img/circle_sgl.png',
		};
		
		var infowindow = new google.maps.InfoWindow({
			content: '',
			pixelOffset: new google.maps.Size(-1, 15)
		});
		
		var latlngbounds = new google.maps.LatLngBounds();
		
        for (var mosaic of mosaics) {
        	
			var latLng = new google.maps.LatLng(mosaic.startLat, mosaic.startLng);
			var marker = new google.maps.Marker({
				position: latLng,
				map: map,
				icon: image,
			});
			
	        var mlatLng = new google.maps.LatLng(mosaic.startLat, mosaic.startLng);
	        latlngbounds.extend(mlatLng);
	        
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
				
			})(marker, mosaic, infowindow));
        }
        
        map.fitBounds(latlngbounds);
	}
	
	$scope.init = function(mosaics) {
	
		$scope.indexes_by_country = []
		var country_code_array = [];
		
		$scope.indexes_by_mission = []
		var mission_count_array = [];
		
		for (var mosaic of mosaics) {
			
			var index_by_country = null;
			
			var country_code = mosaic.country_code;
			var index = country_code_array.indexOf(country_code);
			if (index == -1) {
				
				index_by_country = {
					
					'code':mosaic.country_code,
					'name':mosaic.country_code.toUpperCase(),
					
					'mosaics':[],
				}
				
				country_code_array.push(country_code);
				$scope.indexes_by_country.push(index_by_country);
			}
			else {
				
				index_by_country = $scope.indexes_by_country[index]
			}
			
			index_by_country.mosaics.push(mosaic);
			
			/*----------*/
			
			var index_by_mission = null;
			
			var mission_count = mosaic.mission_count;
			var index = mission_count_array.indexOf(mission_count);
			if (index == -1) {
				
				index_by_mission = {
					
					'count':mosaic.mission_count,

					'mosaics':[],
				}
				
				mission_count_array.push(mission_count);
				$scope.indexes_by_mission.push(index_by_mission);
			}
			else {
				
				index_by_mission = $scope.indexes_by_mission[index]
			}
			
			index_by_mission.mosaics.push(mosaic);
		}
		
		$scope.indexes_by_country.sort(function(a, b) {

			if (a.name > b.name) return 1;
			if (a.name < b.name) return -1;
			
			return 0;
		});

		for (var index of $scope.indexes_by_country) {
			
			index.mosaics.sort(function(a, b) {
	
				if (a.city_name > b.city_name) return 1;
				if (a.city_name < b.city_name) return -1;
					
				if (a.name > b.name) return 1;
				if (a.name < b.name) return -1;
				
				return 0;
			});
		}

		$scope.current_by_country_index = $scope.indexes_by_country[0];
		$scope.mosaics_by_country = $scope.current_by_country_index.mosaics;
		
		/*----------*/
		
		$scope.indexes_by_mission.sort(function(a, b) {

			if (a.count > b.count) return 1;
			if (a.count < b.count) return -1;
			
			return 0;
		});

		for (var index of $scope.indexes_by_mission) {
			
			index.mosaics.sort(function(a, b) {
	
				if (a.name > b.name) return 1;
				if (a.name < b.name) return -1;
				
				return 0;
			});
		}

		$scope.current_by_mission_index = $scope.indexes_by_mission[0];
		$scope.mosaics_by_mission = $scope.current_by_mission_index.mosaics;
		
		$scope.mosaics_sorting = 'by_country';
		
		$scope.initMap(mosaics);
		
		$scope.loaded = true;
	}
});