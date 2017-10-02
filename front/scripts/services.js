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
