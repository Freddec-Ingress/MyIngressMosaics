angular.module('FrontModule.controllers').controller('AdmRegistationCtrl', function($scope, $window, API, UtilsService) {
	
	/* Mosaic management */
	
	$scope.mosaics = [];
	
	$scope.isMissionCountValid = function(mosaic) {
		
		var count = mosaic.missions.length;
		var rest = count % 6;
		
		if (rest == 0) return true;
		return false;
	}
	
	$scope.openMosaic = function(mosaic) {
		
		mosaic.open = true;
		
		$scope.computeOffsetMosaic(mosaic);
		
		mosaic.columns = '6';

		var geocoder = new google.maps.Geocoder;
		
		var latlng = {
			lat: parseFloat(mosaic.missions[0].startLat),
			lng: parseFloat(mosaic.missions[0].startLng),
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
						
						if (item.types[0] == 'country') mosaic.country = item.long_name;
						if (item.types[0] == 'locality') mosaic.city = item.long_name;
						if (item.types[0] == 'administrative_area_level_1') mosaic.region = item.long_name;
						if (item.types[0] == 'administrative_area_level_2') admin2 = item.long_name;
						if (item.types[0] == 'administrative_area_level_3') admin3 = item.long_name;
					}
					
					if (!mosaic.city && admin2) mosaic.city = admin2;
					if (!mosaic.city && admin3) mosaic.city = admin3;
					
					/* Country */
					
					API.sendRequest('/api/country/list/', 'POST').then(function(response) {
						
						var countryList = response.countries;

						var cur_country = null;
						for (var country of countryList) {
							if (country.name == mosaic.country || country.locale == mosaic.country) {
								
								cur_country = country;
								
								mosaic.country = country.name;
								break;
							}
						}
						
						/* Region */
						
						if (cur_country) {
							
							var data = {'country_id':cur_country.id};
							API.sendRequest('/api/region/list/', 'POST', {}, data).then(function(response) {
								
								var regionList = response.regions;
								
								var cur_region = null;
								for (var region of regionList) {
									if (region.name == mosaic.region || region.locale == mosaic.region) {
										
										cur_region = region;
										
										mosaic.region = region.name;
										break;
									}
								}
								
								/* City */
								
								if (cur_region) {
									
									var data = {'country_id':cur_country.id, 'region_id':cur_region.id};
									API.sendRequest('/api/city/list/', 'POST', {}, data).then(function(response) {
										
										var cityList = response.cities;
										
										var cur_city = null;
										for (var city of cityList) {
											if (city.name == mosaic.city || city.locale == mosaic.city) {
												
												cur_city = city;
												
												mosaic.city = city.name;
											}
										}
									});
								}
							});
						}
					});
					
					$scope.$applyAsync();
				}
			}
		});
	}
	
	$scope.computeOffsetMosaic = function(mosaic) {
		
		var temp = 0;
		if (mosaic.missions.length > mosaic.columns) {
			temp = mosaic.columns - mosaic.missions.length % mosaic.columns;
			if (temp < 0 || temp > (mosaic.columns - 1)) temp = 0;
		}
		
		mosaic.offset = new Array(temp);
	}
	
	$scope.createMosaic = function(mosaic) {
		
		$scope.reorderAscMosaic(mosaic);
		
		var data = {
			'country': mosaic.country,
			'region': mosaic.region,
			'city': mosaic.city,
			'columns': mosaic.columns,
			'type': mosaic.type,
			'title': mosaic.name,
			'missions': mosaic.missions,
		};
		
		API.sendRequest('/api/mosaic/create/', 'POST', {}, data).then(function(response) {
			
			var index = $scope.mosaics.indexOf(mosaic);
			$scope.mosaics.splice(index, 1);
			
			$scope.openMosaic($scope.mosaics[index]);
		});
	}
	
	$scope.excludeMosaic = function(mosaic) {
		
		for (var mission of mosaic.missions) $scope.excludeMission(mosaic, mission);
		
		var index = $scope.mosaics.indexOf(mosaic);
		$scope.mosaics.splice(index, 1);
	}
	
	$scope.reorderMosaic = function(mosaic) {
		
		mosaic.missions.sort(UtilsService.sortMissionsByOrderTitleAsc);
	}
	
	$scope.reorderAscMosaic = function(mosaic) {
		
		var index = 0;
		for (var m of mosaic.missions) {
			
			index += 1;
			m.order = index;
		}
		
		mosaic.missions.sort(UtilsService.sortMissionsByOrderTitleAsc);
	}
	
	$scope.reorderDescMosaic = function(mosaic) {
		
		var index = mosaic.missions.length + 1;
		for (var m of mosaic.missions) {
			
			index -= 1;
			m.order = index;
		}
		
		mosaic.missions.sort(UtilsService.sortMissionsByOrderTitleAsc);
	}
	
	$scope.reorderAlphaMosaic = function(mosaic) {
		
		mosaic.missions.sort(function(a, b) {
			return a.title - b.title;
		});
		
		var index = 0;
		for (var m of mosaic.missions) {
			
			index += 1;
			m.order = index;
		}
		
		mosaic.missions.sort(UtilsService.sortMissionsByOrderTitleAsc);
	}
	
	/* Mission management */
	
	$scope.excludeMission = function(mosaic, mission) {
		
		var data = { 'ref':mission.ref };
		API.sendRequest('/api/mission/exclude/', 'POST', {}, data).then(function(response) {
			
			var index = mosaic.missions.indexOf(mission);
			mosaic.missions.splice(index, 1);
		});
	}
	
	/* Page loading */
	
	API.sendRequest('/api/missions/', 'POST').then(function(response) {
    
    	var names = [];
    
        var missions = response.missions;
        if (missions && missions.length > 0) {
        	
        	for (var mission of missions) {
				
        		var mosaic = null;
        		
        		var name = mission.name;
        		var index = names.indexOf(name);
        		
        		if (index == -1) {
        			
        			names.push(name);
        			
        			mosaic = {
        				'name': name,
        				'type': 'sequence',
        				'open': false,
        				'columns': 6,
        				'offset': null,
        				'city': null,
        				'region': null,
        				'country': null,
        				'missions': [],
        				'creator': mission.creator,
        			}
        			
        			$scope.mosaics.push(mosaic);
        		}
        		else {
        			
        			mosaic = $scope.mosaics[index];
        		}
        		
        		mosaic.missions.push(mission);
        		
		    	var order = UtilsService.getOrderFromMissionName(mission.title);
				if (order < 1) order = mosaic.missions.indexOf(mission) + 1;
				mission.order = order.toString();
        	}
        }
        
        var temp = $scope.mosaics.slice();
        for (var mosaic of temp) {
        	
        	var index = $scope.mosaics.indexOf(mosaic);

    		var count = mosaic.missions.length;
    		if (count < 3) {
    			
    			$scope.excludeMosaic(mosaic);
    		}
    		else {
    			$scope.reorderMosaic(mosaic);
    		}
        }
        
        $scope.mosaics.sort(function(a, b) {
        	
        	if (a.missions.length > b.missions.length) return -1;
        	if (a.missions.length < b.missions.length) return 1;
        	
        	if (a.name > b.name) return 1;
        	if (a.name < b.name) return -1;
        	
        	return 0;
        });
        
    	$scope.loaded = true;
	});
});