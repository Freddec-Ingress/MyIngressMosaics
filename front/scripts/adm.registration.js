angular.module('FrontModule.controllers').controller('AdmRegistationCtrl', function($scope, API, UtilsService) {
	
	/* Mosaic management */
	
	$scope.mosaics = [];
	
	$scope.openMosaic = function(mosaic) {
		
		mosaic.open = true;
		
		var temp = 0;
		if ($scope.missions.length > $scope.columns) {
			temp = $scope.columns - $scope.missions.length % $scope.columns;
			if (temp < 0 || temp > ($scope.columns - 1)) temp = 0;
		}
		
		mosaic.offset = new Array(temp);
		
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
					
					console.log(components);
					
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
	
	/* Page loading */
	
	API.sendRequest('/api/missions/', 'POST').then(function(response) {
    
    	var names = [];
    
        var missions = response.missions;
        if (missions && missions.length > 0) {
        	
        	for (var mission of missions) {
        		
		    	var order = UtilsService.getOrderFromMissionName(mission.title);
				if (order < 1) order = 0;
				mission.order = order.toString();
				
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
        			}
        			
        			$scope.mosaics.push(mosaic);
        		}
        		else {
        			
        			mosaic = $scope.mosaics[index];
        		}
        		
        		mosaic.missions.push(mission);
        	}
        }
        
        for (var mosaic of $scope.mosaics) {
        	
        	var index = $scope.mosaics.indexOf(mosaic);
        	if (!$scope.mosaics.missions) $scope.mosaics.splice(index, 1);
        	else {
        		
        		var count = $scope.mosaics.missions.length;
        		if (count < 3) $scope.mosaics.splice(index, 1);
        	}
        }
        
        $scope.mosaics.sort(function(a, b) {
        	
        	if (a.missions.length > b.missions.length) return 1;
        	if (a.missions.length < b.missions.length) return -1;
        	
        	if (a.name > b.name) return 1;
        	if (a.name < b.name) return -1;
        	
        	return 0;
        });
        
    	$scope.loaded = true;
	});
});