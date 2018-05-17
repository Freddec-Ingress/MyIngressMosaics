angular.module('FrontModule.controllers').controller('TagPageCtrl', function($scope, $window, API) {
	
	/* Tab management */
	
	$scope.current_tab = 'mosaics';
	
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
			
			zoom: 1,
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
			center: {lat:0, lng:0},
		});
		
        map.mapTypes.set('Ingress Intel', styledMapType);
        map.setMapTypeId('Ingress Intel');
        
		var image = {
		    scaledSize: new google.maps.Size(25, 25),
			origin: new google.maps.Point(0, 0),
			anchor: new google.maps.Point(12, 13),
			url: 'https://www.myingressmosaics.com/static/img/circle_sgl.png',
		};
		
        for (var mosaic of mosaics) {
        	
			var latLng = new google.maps.LatLng(mosaic.startLat, mosaic.startLng);
			var marker = new google.maps.Marker({
				position: latLng,
				map: map,
				icon: image,
			});
        }
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