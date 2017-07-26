angular.module('RegistrationApp.services', [])

angular.module('RegistrationApp.services').service('CreateService', function($state, $window, API) {
	
	var service = {

		data: {
			
			desc: null,
			city: null,
			type: null,
			cols: null,
			rows: null,
			title: null,
			region: null,
			country: null,
			
			missions: [],
		},
		
		init: function() {
			
			service.data.desc = null;
			service.data.city = null;
			service.data.type = null;
			service.data.cols = null;
			service.data.rows = null;
			service.data.title = null;
			service.data.region = null;
			service.data.country = null;
			
			service.data.missions = [];
		},
		
		getRefArray: function() {
			
			var refArray = [];
			for (var item of service.data.missions) {
				refArray.push(item.ref);
			}
			return refArray;
		},
		
		remove: function(item) {
			
			var index = service.data.missions.indexOf(item);
			if (index > -1) {
				service.data.missions.splice(index, 1);
			}
		},
		
		removeAll: function() {
			
			service.data.missions = [];
		},
		
		add: function(item) {
			service.data.missions.push(item);
		},
		
		default: function() {

			var max_order = 0;
			
			for (var m of service.data.missions) {
				
				var order = 0;
				
				var found = m.name.match(/[0-9]+/);
				if (found) order = parseInt(found[0]);
				
				if (order > max_order) max_order = order;
				
				m.order = order;
			}
			
			service.data.missions = service.data.missions.sort(function(a, b) {
				
				if (a.order < b.order) { 	return -1; }
				if (a.order > b.order) { 	return 1; }
				return 0;
			});
			
			if (service.data.missions[0]) {
				
				service.data.title = service.data.missions[0].name;
				service.data.desc = service.data.missions[0].desc;
				
				service.data.title = service.data.title.replace(/0|1|2|3|4|5|6|7|8|9|#/g, '');
				service.data.title = service.data.title.replace('.', '');
				service.data.title = service.data.title.replace('(', '');
				service.data.title = service.data.title.replace(')', '');
				service.data.title = service.data.title.replace('/', '');
				service.data.title = service.data.title.trim();
				service.data.title = service.data.title.replace('of  ', '');
				service.data.title = service.data.title.replace('  of', '');
			}
			
			service.data.type = 'sequence';
			service.data.cols = 6;
			service.data.rows = Math.ceil(service.data.missions.length / 6);
		},
		
		getImageByOrder: function(order) {
			
			var url = null;
			
			for (var item of service.data.missions) {
				if ((service.data.missions.length - item.order + 1) == order) {
					url = item.image;
					break;
				}
			}
			
			return url;
		},
		
		create: function() {
			
			return API.sendRequest('/api/mosaic/create/', 'POST', {}, service.data).then(function(response) {
				
				$window.location.href = '/mosaic/' + response;
			});
		},
		
		createWithMosaic: function(mosaic, callback) {
			
			service.init();
			
			service.data.title = mosaic.name;
			service.data.missions = mosaic.missions;
			
			service.data.desc = service.data.missions[0].desc;
			service.data.type = 'sequence';
			service.data.cols = 6;
			service.data.rows = Math.ceil(service.data.missions.length / 6);
			
			var geocoder = new google.maps.Geocoder;
			
			var latlng = {
				lat: parseFloat(service.data.missions[0].lat),
				lng: parseFloat(service.data.missions[0].lng),
			};
		
			geocoder.geocode({'location': latlng}, function(results, status) {
				
				if (status === 'OK') {
					if (results[1]) {
						
						var admin2 = null;
						var admin3 = null;
						
						for (var item of results[1].address_components) {
							
							if (item.types[0] == 'country') service.data.country = item.long_name;
							if (item.types[0] == 'locality') service.data.city = item.long_name;
							if (item.types[0] == 'administrative_area_level_1') service.data.region = item.long_name;
							if (item.types[0] == 'administrative_area_level_2') admin2 = item.long_name;
							if (item.types[0] == 'administrative_area_level_3') admin3 = item.long_name;
						}
						
						if (!service.data.city && admin2) service.data.city = item.admin2;
						if (!service.data.city && admin3) service.data.city = item.admin3;

						if (!service.data.city) service.data.city = service.data.region;

						API.sendRequest('/api/mosaic/create/', 'POST', {}, service.data).then(function(response) {
							
							callback(mosaic);
							
							$window.location.href = '/mosaic/' + response;
						});
					}
				}
			});
		},
	};
	
	return service;
});
