angular.module('AngularApp.services', [])

angular.module('AngularApp.services').service('API', function($q, $http, $cookies, $filter, toastr) {
	
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
					
					toastr.error($filter('translate')(response.data.detail));

					deferred.reject(response.data, response.status, response.headers, response.config);
				});
			
			return deferred.promise;
		},
	};
	
	return service;
});

angular.module('AngularApp.services').service('UserService', function($auth, $http, $cookies, $state, API) {
	
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

			if (!$auth.isAuthenticated()) return;
			
			service.data.authenticated = true;
			
			return API.sendRequest('/api/profile/', 'GET').then(function(response) {
				
				service.data.name = response.name;
				service.data.team = response.team;
				service.data.level = response.level;
				service.data.superuser = response.superuser;
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
				
				$state.go('root.home', {location: 'replace'});
			});
		},
		
		socialLogin: function(provider) {
			
			return $auth.authenticate(provider).then(function(response) {
				
				$auth.setToken(response.data.token);
				$cookies.token = response.data.token;
				
				service.init();
				
				$state.go('root.home', {location: 'replace'});
			});
		},
		
		localLogin: function(username, password) {
			
			var data = { 'username':username, 'password':password }
			return API.sendRequest('/api/login/', 'POST', {}, data).then(function(response) {
				
				$auth.setToken(response.token);
				$cookies.token = response.token;
			
				service.init();
				
				$state.go('root.home', {location: 'replace'});
			});
		},
		
		register: function(username, password1, password2, email) {
			
			var data = { 'username':username, 'password1':password1, 'password2':password2, 'email':email }
			return API.sendRequest('/api/register/', 'POST', {}, data).then(function(response) {
				
				$auth.setToken(response.token);
				$cookies.token = response.token;
				
				service.init();
				
				$state.go('root.home', {location: 'replace'});
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
			
			if (service.data.authenticated) {
				return API.sendRequest('/api/missions/', 'GET').then(function(response) {
					
					service.data.missions = response;
				});
			}
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
				
				var a_name = a.name.toLowerCase();
				var b_name = b.name.toLowerCase();
				
				if (a_name < b_name)
					return -1;
					
				if (a_name > b_name)
					return 1;

				return 0;
			}
			
			function compareNameDesc(a, b) {
				
				var a_name = a.name.toLowerCase();
				var b_name = b.name.toLowerCase();
				
				if (a_name > b_name)
					return -1;
					
				if (a_name < b_name)
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

				return 0;
			}
			
			function compareCreatorDesc(a, b) {
				
				var a_creator = a.creator.toLowerCase();
				var b_creator = b.creator.toLowerCase();
				
				if (a_creator > b_creator)
					return -1;
					
				if (a_creator < b_creator)
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

angular.module('AngularApp.services').service('CreateService', function($state, API) {
	
	var service = {

		data: {
			
			desc: null,
			city: null,
			type: null,
			cols: null,
			count: null,
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
			service.data.count = null;
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
		
		add: function(item) {
			service.data.missions.push(item);
		},
		
		default: function() {

			if (service.data.missions[0]) {
				
				service.data.title = service.data.missions[0].name;
				service.data.desc = service.data.missions[0].desc;
			}
			
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
			
			service.data.type = 'sequence';
			service.data.count = service.data.missions.length;
			service.data.cols = 6;
			
			if (max_order > service.data.count) service.data.count = max_order;
			
			var temp = Math.ceil(service.data.count / 6);
			service.data.count = 6 * temp;
		},
		
		getImageByOrder: function(order) {
			
			var url = null;
			
			for (var item of service.data.missions) {
				if ((service.data.count - item.order + 1) == order) {
					url = item.image;
					break;
				}
			}
			
			return url;
		},
		
		create: function() {
			
			return API.sendRequest('/api/mosaic/create/', 'POST', {}, service.data).then(function(response) {
				
				$state.go('root.mosaic', {ref: response});
			});
		},
	};
	
	return service;
});

angular.module('AngularApp.services').service('MosaicService', function($state, API, DataService) {
	
	var service = {

		data: {
			
			mosaic: null,
			potentials: null,
		},
		
		getMosaic: function(ref) {
			
			var data = { 'ref':ref };
			API.sendRequest('/api/mosaic/potential/', 'POST', {}, data).then(function(response) {
				
				if (response) {
					service.data.potentials = response;
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
				service.data.mosaic.count = response.count;
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
		
		add: function(mission) {
			
			var data = { 'ref':service.data.mosaic.ref, 'mission':mission };
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

angular.module('AngularApp.services').service('DataService', function($cookies, API) {
	
	var service = {

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
		
		search: function(text) {
			
			var data = {'text':text};
			return API.sendRequest('/api/search/', 'POST', {}, data);
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
