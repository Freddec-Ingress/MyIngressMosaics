angular.module('MosaicApp.services', [])

angular.module('MosaicApp.services').service('MosaicService', function($state, API, DataService) {
	
	var service = {

		data: {
			
			mosaic: null,
			potentials: null,
		},
		
		sortMPotentialsByName: function(sort) {
			
			function compareNameAsc(a, b) {
				
				var a_name = a.name.toLowerCase().replace(/0|1|2|3|4|5|6|7|8|9/g, '');
				var b_name = b.name.toLowerCase().replace(/0|1|2|3|4|5|6|7|8|9/g, '');
				
				if (a_name < b_name)
					return -1;
					
				if (a_name > b_name)
					return 1;

				var a_name = a.name;
				var b_name = b.name;
				
				if (a_name < b_name)
					return -1;
					
				if (a_name > b_name)
					return 1;
					
				var a_creator = a.creator.toLowerCase();
				var b_creator = b.creator.toLowerCase();
				
				if (a_creator < b_creator)
					return -1;
					
				if (a_creator > b_creator)
					return 1;

				return 0;
			}
			
			function compareNameDesc(a, b) {
				
				var a_name = a.name.toLowerCase().replace(/0|1|2|3|4|5|6|7|8|9/g, '');
				var b_name = b.name.toLowerCase().replace(/0|1|2|3|4|5|6|7|8|9/g, '');
				
				if (a_name > b_name)
					return -1;
					
				if (a_name < b_name)
					return 1;

				var a_name = a.name;
				var b_name = b.name;
				
				if (a_name > b_name)
					return -1;
					
				if (a_name < b_name)
					return 1;
					
				var a_creator = a.creator.toLowerCase();
				var b_creator = b.creator.toLowerCase();
				
				if (a_creator > b_creator)
					return -1;
					
				if (a_creator < b_creator)
					return 1;
				
				return 0;
			}
			
			if (service.data.potentials) {
				
				if (sort == 'asc') service.data.potentials.sort(compareNameAsc);
				if (sort == 'desc') service.data.potentials.sort(compareNameDesc);
			}
		},

		getMosaic: function(ref) {
			
			var data = { 'ref':ref };
			API.sendRequest('/api/mosaic/potential/', 'POST', {}, data).then(function(response) {
				
				if (response) {
					
					for (var m of response) {
						
						var order = 0;
						
						var found = m.name.match(/[0-9]+/);
						if (found) order = parseInt(found[0]);

						m.order = order;
					}
					
					service.data.potentials = response;
					service.sortMPotentialsByName();
				}
			});
			
			return API.sendRequest('/api/mosaic/' + ref + '/', 'GET').then(function(response) {
				
				service.data.mosaic = response;
			});
		},
		
		getImageByOrder: function(order) {
			
			var url = null;
			
			if (service.data.mosaic) {
				for (var item of service.data.mosaic.missions) {
					if ((service.data.mosaic.count - item.order + 1) == order) {
						url = item.image;
						break;
					}
				}
			}
			
			return url;
		},
		
		getColsArray: function() {
			
			var temp = 1;
			if (service.data.mosaic.cols > 0) temp = service.data.mosaic.cols;
			if (!temp) temp = 1;
			
			var cols = [];
			for (var i = 0; i < temp; i++) {
				cols.push(i);
			}

			return cols;
		},
		
		getRowsArray: function() {
			
			var temp = 1;
			if (service.data.mosaic.count > 0 && service.data.mosaic.cols > 0) temp = Math.ceil(service.data.mosaic.count / service.data.mosaic.cols);
			if (!temp) temp = 1;
			
			var rows = [];
			for (var i = 0; i < temp; i++) {
				rows.push(i);
			}
			
			return rows;
		},
		
		edit: function(data) {
			
			return API.sendRequest('/api/mosaic/edit/', 'POST', {}, data).then(function(response) {
				
				service.data.mosaic.city = response.city;
				service.data.mosaic.desc = response.desc;
				service.data.mosaic.type = response.type;
				service.data.mosaic.cols = response.cols;
				service.data.mosaic.rows = response.rows;
				service.data.mosaic.title = response.title;
				service.data.mosaic.region = response.region;
				service.data.mosaic.country = response.country;
			});
		},

		reorder: function(data) {
			
			return API.sendRequest('/api/mosaic/reorder/', 'POST', {}, data).then(function(response) {
				
				service.data.mosaic._distance = response._distance;
				service.data.mosaic.missions = response.missions;
			});
		},
		
		delete: function(neworder) {
			
			var data = { 'ref':service.data.mosaic.ref, };
			return API.sendRequest('/api/mosaic/delete/', 'POST', {}, data).then(function(response) {
					
				DataService.current_city = service.data.mosaic.city;
				$state.go('root.city', {'country':service.data.mosaic.country, 'region':service.data.mosaic.region, 'city':service.data.mosaic.city});
				
				service.data.mosaic = null;
			});
		},
		
		remove: function(mission) {
			
			var data = { 'ref':service.data.mosaic.ref, 'mission':mission };
			return API.sendRequest('/api/mosaic/remove/', 'POST', {}, data).then(function(response) {
					
				service.data.mosaic.creators = response.creators;
				service.data.mosaic._distance = response._distance;
				service.data.mosaic.missions = response.missions;
			});
		},
		
		add: function(mission, order) {
			
			var data = { 'ref':service.data.mosaic.ref, 'mission':mission, 'order':order };
			return API.sendRequest('/api/mosaic/add/', 'POST', {}, data).then(function(response) {
					
				service.data.mosaic.creators = response.creators;
				service.data.mosaic._distance = response._distance;
				service.data.mosaic.missions = response.missions;
			});
		},
		
		repair: function() {
			
			var data = {'ref':service.data.mosaic.ref};
			return API.sendRequest('/api/mosaic/repair/', 'POST', {}, data);
		},
	};
	
	return service;
});
