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
					
					toastr.error($filter('translate')(response.data.detail));

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
