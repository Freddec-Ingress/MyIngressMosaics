angular.module('FrontModule.controllers').controller('AdmRegistationCtrl', function($scope, $window, API, UtilsService) {
	
	/* Mosaic management */
	
	$scope.mosaics = [];
	
	$scope.isMissionCountValid = function(mosaic) {
		
		var count = mosaic.missions.length;
		var rest = count % 6;
		
		if (rest == 0) return true;
		return false;
	}
	
	$scope.openMosaic = function(mosaic, index) {
		
		mosaic.open = true;
		
		$scope.computeOffsetMosaic(mosaic);
		
		mosaic.columns = '6';
		
		var geocoder = new google.maps.Geocoder();
		
		var latlng = {
			lat: parseFloat(mosaic.missions[0].startLat),
			lng: parseFloat(mosaic.missions[0].startLng),
		};
		
		geocoder.geocode({'location': latlng}, function(results, status) {
			
			if (status == 'OK') {
				
				var components = null;
				if (results[0]) components = results[0].address_components;
				if (results[1]) components = results[1].address_components;
				
				if (components) {
					
					var city = '';
					var country = '';
					
					for (var item of components) {
						
						if (item.types[0] == 'country') country = item.long_name;
						if (item.types[0] == 'locality') city = item.long_name;
					}
					
					mosaic.default = country + ', ' + city;
					
					console.log(mosaic.default);
					
					$scope.$apply();
				}
			}
		});

	    var inputCity = document.getElementById('city_input_' + index.toString());
	    var options = {
			types: ['(cities)'],
		};
		
	    var autocomplete = new google.maps.places.Autocomplete(inputCity, options);
	        
	    autocomplete.addListener('place_changed', function() {
	    	
			mosaic.city = '';
			mosaic.region = '';
			mosaic.country = '';
	    	
	    	var place = autocomplete.getPlace();
	    	for (var i = 0; i < place.address_components.length; i++) {
	    		
	    		var addressType = place.address_components[i].types[0];
	    		if (addressType == 'country') mosaic.country = place.address_components[i]['long_name'];
	    		if (addressType == 'administrative_area_level_1') mosaic.region = place.address_components[i]['long_name'];
	    		if (addressType == 'administrative_area_level_2' && !mosaic.region) mosaic.region = place.address_components[i]['long_name'];
	    		if (addressType == 'administrative_area_level_3' && !mosaic.city) mosaic.city = place.address_components[i]['long_name'];
	    		if (addressType == 'locality') mosaic.city = place.address_components[i]['long_name'];
	    	}
	    	
	    	console.log(place.address_components);
	    	
	     	console.log(mosaic.country);
	    	console.log(mosaic.region);
	    	console.log(mosaic.city);

			$scope.$apply();
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
	
	$scope.go = function(url) {
		$window.open(url);
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
        				'columns': '6',
        				'offset': null,
        				'city': null,
        				'region': null,
        				'country': null,
        				'default': null,
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