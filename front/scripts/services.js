angular.module('FrontModule.services', [])

angular.module('FrontModule.services').service('API', function($q, $http, $cookies) {
	
	var service = {
		
		sendRequest: function(url, method, params, data) {
			
			if ($cookies.token) { $http.defaults.headers.common.Authorization = 'Token ' + $cookies.token; }
			
			var deferred = $q.defer();
			
			$http({url: url, withCredentials: false, method: method, headers: {'X-CSRFToken': $cookies['csrftoken']}, params: params, data: data})
				.then(function successCallback(response) {
					
					deferred.resolve(response.data, response.status);
				}
				, function errorCallback(response) {

					if (response.status == 0) {
						
						if (response.data == '') response.data = 'error_TIMEOUT';
						if (response.data == null) response.data = 'error_NOCONNECTION';
					}

					deferred.reject(response.data, response.status, response.headers, response.config);
				});
			
			return deferred.promise;
		},
	};
	
	return service;
});

angular.module('FrontModule.services').service('UserService', function($auth, $http, $cookies, $window, API) {
	
	var service = {

		data: {

			name: null,
			team: null,
			level: null,
			superuser: null,
			
			authenticated: false,
			
			mosaics: null,
			missions: null,
		},

		init: function() {

			return API.sendRequest('/api/profile/', 'GET').then(function(response) {
				
				if (response) {
					service.data.authenticated = true;
					service.data.name = response.name;
					service.data.team = response.team;
					service.data.level = response.level;
					service.data.superuser = response.superuser;
				}
				else {
					service.data.authenticated = false;
				}
			});
		},

		logout: function() {
			
			delete $http.defaults.headers.common.Authorization;
	    	delete $cookies.token;
			
			$auth.removeToken();
			
			service.data.name = null;
			service.data.team = null;
			service.data.level = null;
			
			service.data.authenticated = false;
			
			return API.sendRequest('/api/logout/', 'POST').then(function(response) {
				
				$window.location.href = '/';
			});
		},
		
		socialLogin: function(provider) {
			
			return $auth.authenticate(provider).then(function(response) {
				
				$auth.setToken(response.data.token);
				$cookies.token = response.data.token;
				
				service.init();
				
				$window.location.href = '/';
			});
		},
		
		localLogin: function(username, password) {
			
			var data = { 'username':username, 'password':password }
			return API.sendRequest('/api/login/', 'POST', {}, data).then(function(response) {
				
				$auth.setToken(response.token);
				$cookies.token = response.token;
			
				service.init();
				
				$window.location.href = '/';
			});
		},
		
		register: function(username, password1, password2, email) {
			
			var data = { 'username':username, 'password1':password1, 'password2':password2, 'email':email }
			return API.sendRequest('/api/register/', 'POST', {}, data).then(function(response) {
				
				$auth.setToken(response.token);
				$cookies.token = response.token;
				
				service.init();
				
				$window.location.href = '/';
			});
		},
		
		updateName: function(newvalue) {
			
			var data = { 'name':newvalue };
			return API.sendRequest('/api/profile/name/', 'POST', {}, data).then(function(response) {
				
				service.data.name = newvalue;
			});
		},
		
		getMissions: function() {
			
			return API.sendRequest('/api/missions/', 'GET').then(function(response) {
				
				service.data.missions = response;
			});
		},
		
		deleteMission: function(item) {
			
			var data = { 'ref':item.ref };
			return API.sendRequest('/api/mission/delete/', 'POST', {}, data).then(function(response) {
				
				var index = service.data.missions.indexOf(item);
				if (index > -1) {
					service.data.missions.splice(index, 1);
				}
			});
		},

		sortMissionsByName: function(sort) {
			
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
			
			if (service.data.missions) {
				
				if (sort == 'asc') service.data.missions.sort(compareNameAsc);
				if (sort == 'desc') service.data.missions.sort(compareNameDesc);
			}
		},

		sortMissionsByCreator: function(sort) {
			
			function compareCreatorAsc(a, b) {
				
				var a_creator = a.creator.toLowerCase();
				var b_creator = b.creator.toLowerCase();
				
				if (a_creator < b_creator)
					return -1;
					
				if (a_creator > b_creator)
					return 1;

				var a_name = a.name.toLowerCase();
				var b_name = b.name.toLowerCase();
				
				if (a_name < b_name)
					return -1;
					
				if (a_name > b_name)
					return 1;
					
				return 0;
			}
			
			function compareCreatorDesc(a, b) {
				
				var a_creator = a.creator.toLowerCase();
				var b_creator = b.creator.toLowerCase();
				
				if (a_creator > b_creator)
					return -1;
					
				if (a_creator < b_creator)
					return 1;
				
				var a_name = a.name.toLowerCase();
				var b_name = b.name.toLowerCase();
				
				if (a_name > b_name)
					return -1;
					
				if (a_name < b_name)
					return 1;
					
				return 0;
			}
			
			if (service.data.missions) {
				
				if (sort == 'asc') service.data.missions.sort(compareCreatorAsc);
				if (sort == 'desc') service.data.missions.sort(compareCreatorDesc);
			}
		},
	};
	
	return service;
});

angular.module('FrontModule.services').service('DataService', function(API) {
	
	var service = {

		loadLatest: function() {
			
			return API.sendRequest('/api/latest/', 'GET');
		},
		
		loadCountriesFromWorld: function() {
			return API.sendRequest('/api/world/', 'GET');
		},
	};
	
	return service;
});

angular.module('FrontModule.services').service('CreateService', function($window, API) {
	
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
		
		add: function(item) {
			service.data.missions.push(item);
		},
		
		createWithMosaic: function(mosaic) {
			
			service.init();
			
			service.data.title = mosaic.title;
			service.data.missions = mosaic.missions;
			service.data.type = mosaic.type;
			service.data.cols = mosaic.columns;
			service.data.city = mosaic.city;
			service.data.region = mosaic.region;
			service.data.country = mosaic.country;

			API.sendRequest('/api/mosaic/create/', 'POST', {}, service.data).then(function(response) {

				$window.open('https://www.myingressmosaics.com/mosaic/' + response);
			});
		},
	};
	
	return service;
});

angular.module('FrontModule.services').service('MosaicService', function(API, DataService) {
	
	var service = {

		data: {
			
			mosaic: null,
			potentials: null,
		},
		
		getMosaic: function(ref) {
			
			var data = { 'ref':ref };
			return API.sendRequest('/api/mosaic/potential/', 'POST', {}, data).then(function(response) {
				
				if (response) {
					
					for (var m of response) {
						
						var order = 0;
						
						var found = m.name.match(/[0-9]+/);
						if (found) order = parseInt(found[0]);

						m.order = order;
					}
					
					service.data.potentials = response;
				}
			});
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
	};
	
	return service;
});

angular.module('FrontModule.services').service('MapService', function(API) {
	
	var service = {
		
		getMosaics: function(South_Lat, South_Lng, North_Lat, North_Lng) {
			
			var data = {'sLat':South_Lat, 'sLng':South_Lng, 'nLat':North_Lat, 'nLng':North_Lng};
			return API.sendRequest('/api/map/', 'POST', {}, data);
		},
		
		getMosaicDetails: function(ref) {
			
			var data = {'ref':ref};
			return API.sendRequest('/api/map/mosaic/', 'POST', {}, data);
		}
	};
	
	return service;
});

angular.module('FrontModule.services').service('SearchService', function(API) {
	
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
