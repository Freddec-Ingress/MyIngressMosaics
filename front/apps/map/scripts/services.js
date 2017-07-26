angular.module('MapApp.services', [])

angular.module('MapApp.services').service('MapService', function(API) {
	
	var service = {
		
		getMosaics: function(South_Lat, South_Lng, North_Lat, North_Lng) {
			
			var data = {'sLat':South_Lat, 'sLng':South_Lng, 'nLat':North_Lat, 'nLng':North_Lng};
			return API.sendRequest('/api/map/', 'POST', {}, data);
		},
	};
	
	return service;
});
