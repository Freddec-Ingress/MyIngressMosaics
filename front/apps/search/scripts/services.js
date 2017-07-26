angular.module('SearchApp.services', [])

angular.module('SearchApp.services').service('SearchService', function(API) {
	
	var service = {
		
		data: {
			
			search_text: null,
			
			no_result: false,
	
			cities: null,
			regions: null,
			mosaics: null,
			creators: null,
			countries: null,
		},
		
		reset: function() {
			
			service.data.no_result = false;
			
			service.data.cities = null;
			service.data.regions = null;
			service.data.mosaics = null;
			service.data.creators = null;
			service.data.countries = null;
		},
		
		search: function(text) {
			
			service.data.search_text = text;
			
			var data = {'text':text};
			return API.sendRequest('/api/search/', 'POST', {}, data).then(function(response) {
				
				service.data.cities = response.cities;
				service.data.regions = response.regions;
				service.data.mosaics = response.mosaics;
				service.data.creators = response.creators;
				service.data.countries = response.countries;
				
				if (!service.data.cities && !service.data.regions && !service.data.mosaics && !service.data.creators && !service.data.countries) service.data.no_result = true;
			});
		},
	};
	
	return service;
});
