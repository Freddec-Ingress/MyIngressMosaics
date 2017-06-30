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
					
					toastr.error($filter('translate')(response.data));

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
			
			return;
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
			
			service.data.missions = service.data.missions.sort(function(a, b) {
				
				if (a.name < b.name) { 	return -1; }
				if (a.name > b.name) { 	return 1; }
				return 0;
			});

			if (service.data.missions[0]) {
				
				service.data.title = service.data.missions[0].name;
				service.data.desc = service.data.missions[0].desc;
			}
			
			service.data.type = 'sequence';
			service.data.count = service.data.missions.length;
			service.data.cols = 6;
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

angular.module('AngularApp.services').service('MosaicService', function(API) {
	
	var service = {

		data: {
			
			mosaic: null,
		},
		
		getMosaic: function(ref) {
			
			return API.sendRequest('/api/mosaic/' + ref + '/', 'GET').then(function(response) {
				
				service.data.mosaic = response;
			});
		},
		
		getImageByOrder: function(order) {
			
			var url = null;
			
			for (var item of service.data.mosaic.missions) {
				if ((service.data.mosaic.count - item.order + 1) == order) {
					url = item.image;
					break;
				}
			}
			
			return url;
		},
		
		updateName: function(newvalue) {
			
			var data = { 'ref':service.data.mosaic.ref, 'name':newvalue };
			return API.sendRequest('/api/mosaic/name/', 'POST', {}, data).then(function(response) {
				
				service.data.mosaic.title = newvalue;
			});
		},
	};
	
	return service;
});
