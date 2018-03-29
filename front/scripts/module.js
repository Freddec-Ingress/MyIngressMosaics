angular.module('FrontModule', ['satellizer',
							   'FrontModule.services', 'FrontModule.controllers', 'FrontModule.directives', ]);



/* Config */

angular.module('FrontModule').config(function($interpolateProvider, $authProvider) {

    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
    
	$authProvider.google({
		
		url: '/api/user/google/',
		clientId: '404579985700-eig13jlsdvbe6bhmtsis46tsn7nij4ju.apps.googleusercontent.com',
		redirectUri: window.location.origin + '/api/user/redirect/',
	});

	$authProvider.authToken = 'Token';
	$authProvider.tokenType = 'Token';
});



/* Filter */

angular.module('FrontModule').filter('reverse', function() {
	
	return function(items) {
		if (!items) return;
		return items.slice().reverse();
	};
});