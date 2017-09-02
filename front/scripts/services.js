angular.module('FrontModule.services', [])

angular.module('FrontModule.services').service('API', function($q, $http, $cookies, $filter, toastr) {
	
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

angular.module('FrontModule.services').service('UserService', function($auth, $http, $cookies, $state, $window, API) {
	
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
		
		updateTeam: function(newvalue) {
			
			var data = { 'team':newvalue };
			return API.sendRequest('/api/profile/team/', 'POST', {}, data).then(function(response) {
				
				service.data.team = newvalue;
			});
		},
		
		updateLevel: function(newvalue) {
			
			var data = { 'level':newvalue };
			return API.sendRequest('/api/profile/level/', 'POST', {}, data).then(function(response) {
				
				service.data.level = newvalue;
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
		
		getMosaics: function() {
			
			if (service.data.authenticated) {
				return API.sendRequest('/api/mosaics/', 'GET').then(function(response) {
					
					service.data.mosaics = response;
				});
			}
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

angular.module('FrontModule.services').service('DataService', function($cookies, API) {
	
	var service = {

		loadLatest: function() {
			
			return API.sendRequest('/api/mosaic/latest/', 'GET');
		},
		
		loadCountriesFromWorld: function() {
			return API.sendRequest('/api/world/', 'POST');
		},
		
		loadRegionsFromCountry: function(country) {
			
			var data = {'country':country};
			return API.sendRequest('/api/country/', 'POST', {}, data);
		},
		
		loadCitiesFromRegion: function(country, region) {
			
			var data = {'country':country, 'region':region};
			return API.sendRequest('/api/region/', 'POST', {}, data);
		},
		
		loadMosaicsFromCity: function(country, region, city) {
			
			var data = {'country':country, 'region':region, 'city':city};
			return API.sendRequest('/api/city/', 'POST', {}, data);
		},
		
		loadMosaicsFromCreator: function(creator) {
			
			var data = {'creator':creator};
			return API.sendRequest('/api/creator/', 'POST', {}, data);
		},

		sortByMosaics: function(sort, list) {
			
			function compareMosaicsAsc(a, b) {
				
				if (a.mosaics < b.mosaics) return -1;
				if (a.mosaics > b.mosaics) return 1;

				return 0;
			}
			
			function compareMosaicsDesc(a, b) {
				
				if (a.mosaics > b.mosaics) return -1;
				if (a.mosaics < b.mosaics) return 1;

				return 0;
			}
			
			if (list) {
				
				if (sort == 'asc') list.sort(compareMosaicsAsc);
				if (sort == 'desc') list.sort(compareMosaicsDesc);
			}
		},

		sortByName: function(sort, list) {
			
			function compareNameAsc(a, b) {
				
				var a_name = a.name.toLowerCase();
				var b_name = b.name.toLowerCase();
				
				if (a_name < b_name) return -1;
				if (a_name > b_name) return 1;

				return 0;
			}
			
			function compareNameDesc(a, b) {
				
				var a_name = a.name.toLowerCase();
				var b_name = b.name.toLowerCase();
				
				if (a_name > b_name) return -1;
				if (a_name < b_name) return 1;

				return 0;
			}
				
			if (list) {
				
				if (sort == 'asc') list.sort(compareNameAsc);
				if (sort == 'desc') list.sort(compareNameDesc);
			}
		},

		sortByMissions: function(sort, list) {
			
			function compareMissionsAsc(a, b) {
				
				if (a.count < b.count) return -1;
				if (a.count > b.count) return 1;

				return 0;
			}
			
			function compareMissionsDesc(a, b) {
				
				if (a.count > b.count) return -1;
				if (a.count < b.count) return 1;

				return 0;
			}
				
			if (list) {
				
				if (sort == 'asc') list.sort(compareMissionsAsc);
				if (sort == 'desc') list.sort(compareMissionsDesc);
			}
		},
		
		renameCountry: function(oldValue, newValue) {
			
			var data = {'oldValue':oldValue, 'newValue':newValue};
			return API.sendRequest('/api/country/rename/', 'POST', {}, data);
		},
		
		setRegion: function(city, region) {
			
			var data = {'city':city, 'region':region};
			return API.sendRequest('/api/city/setRegion/', 'POST', {}, data);
		},
		
		renameCity: function(oldValue, newValue) {
			
			var data = {'oldValue':oldValue, 'newValue':newValue};
			return API.sendRequest('/api/city/rename/', 'POST', {}, data);
		},
	};
	
	return service;
});

angular.module('FrontModule.services').service('CreateService', function($state, $window, API) {
	
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

angular.module('FrontModule.services').service('MosaicService', function($state, API, DataService) {
	
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
			return API.sendRequest('/api/mosaic/potential/', 'POST', {}, data).then(function(response) {
				
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

angular.module('FrontModule.services').service('MapService', function(API) {
	
	var service = {
		
		getMosaics: function(South_Lat, South_Lng, North_Lat, North_Lng) {
			
			var data = {'sLat':South_Lat, 'sLng':South_Lng, 'nLat':North_Lat, 'nLng':North_Lng};
			return API.sendRequest('/api/map/', 'POST', {}, data);
		},
		
		getMosaicDetails: function(ref) {
			
			var data = {'ref':ref};
			return API.sendRequest('/api/map/details/', 'POST', {}, data);
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
