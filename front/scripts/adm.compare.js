angular.module('FrontModule.controllers').controller('AdmCompareCtrl', function($scope, API, UtilsService) {
	
	/* Potential management */
    
	$scope.refresh_missions = function(potential, index) {
		
		potential.open = true;
		potential.refreshing = true;
		
		potential.missions = [];
		
		var data = { 'text':potential.name };
		API.sendRequest('/api/potential/refresh/', 'POST', {}, data).then(function(response) {
			
			potential.missions = response.missions;
			
			for (var mission of potential.missions) {
				
				var order = UtilsService.getOrderFromMissionName(mission.title);
				if (order < 1) order = potential.missions.indexOf(mission) + 1;
				mission.order = order;
			}
			
			potential.missions.sort(UtilsService.sortMissionsByOrderTitleAsc);
			
			potential.refreshing = false;
			
			var geocoder = new google.maps.Geocoder();
			
			var latlng = {
				lat: parseFloat(potential.missions[0].startLat),
				lng: parseFloat(potential.missions[0].startLng),
			};
			
			geocoder.geocode({'location': latlng}, function(results, status) {
				
				if (status == 'OK') {

					var components = null;
					if (results[0]) components = results[0].address_components;
					if (results[1]) components = results[1].address_components;
					
					if (components) {
						
						var city = '';
						var country = '';
						var admin1 = '';
						var admin2 = '';
						var admin3 = '';
						
						for (var item of components) {
							
							if (item.types[0] == 'country') country = item.long_name;
							if (item.types[0] == 'locality') city = item.long_name;
							if (item.types[0] == 'administrative_area_level_1') admin1 = item.long_name;
							if (item.types[0] == 'administrative_area_level_2') admin2 = item.long_name;
							if (item.types[0] == 'administrative_area_level_3') admin3 = item.long_name;
						}
						
						potential.default = '';
						if (city) potential.default += city;
						if (admin3) potential.default += ', ' + admin3;
						if (admin2) potential.default += ', ' + admin2;
						if (admin1) potential.default += ', ' + admin1;
						if (country) potential.default += ', ' + country;
	
						$scope.$apply();
					}
				}
			});
		});
		
		var inputCity = document.getElementById('city_input_' + index);
	    var options = {
			types: ['(cities)'],
		};
		
		if (!potential.autocomplete) {
			
		    potential.autocomplete = new google.maps.places.Autocomplete(inputCity, options);
		        
		    potential.autocomplete.addListener('place_changed', function() {
		    	
				potential.city = '';
				potential.region = '';
				potential.country = '';
		    	
		    	var place = potential.autocomplete.getPlace();
		    	for (var i = 0; i < place.address_components.length; i++) {
		    		
		    		var addressType = place.address_components[i].types[0];
		    		if (addressType == 'country') potential.country = place.address_components[i]['long_name'];
		    		if (addressType == 'locality') potential.city = place.address_components[i]['long_name'];
		    		if (addressType == 'administrative_area_level_1') potential.region = place.address_components[i]['long_name'];
		    		if (addressType == 'administrative_area_level_2' && !potential.region) potential.region = place.address_components[i]['long_name'];
		     		if (addressType == 'administrative_area_level_3' && !potential.city) potential.city = place.address_components[i]['long_name'];
		   		}
		
				if (potential.region == '' || !potential.region) {
					
					potential.region = potential.city;
				}

				$scope.$apply();
			});
		}
	}
	
	/* Mosaic management */
    
    $scope.die = function(mosaic) {
    	
    	var data = { 'id':mosaic.id, }
    	API.sendRequest('/api/im/mosaic/die/', 'POST', {}, data);
    	
    	mosaic.dead = true;
    }
     
    $scope.exclude = function(mosaic) {
    	
    	var data = { 'id':mosaic.id, }
    	API.sendRequest('/api/im/mosaic/exclude/', 'POST', {}, data);
    	
    	mosaic.excluded = true;
    }
    
    $scope.register = function(mosaic) {
    	
    	var data = { 'id':mosaic.id, }
    	API.sendRequest('/api/im/mosaic/register/', 'POST', {}, data);
    	
    	mosaic.registered = true;
    }
     
    $scope.delete = function(mosaic) {
    	
    	var data = { 'id':mosaic.id, }
    	API.sendRequest('/api/im/mosaic/delete/', 'POST', {}, data);
    	
    	mosaic.deleted = true;
    }
  
	/* Page loading */
	
    $scope.loaded = true;
});