angular.module('FrontModule', ['satellizer', 'ngCookies',
							   'FrontModule.services', 'FrontModule.controllers', 'FrontModule.directives', ]);



/* Satellizer config */

angular.module('FrontModule').config(function($authProvider, $locale) {
	
	$authProvider.facebook({
		
		url: '/login/social/token_user/facebook',
		clientId: '237811833398918'
	});

	$authProvider.google({
		
		url: '/login/social/token_user/google-oauth2',
		clientId: '949801101013-ss1st02gn04q6oisp1chpp35l8m4itbm.apps.googleusercontent.com'
	});

	$authProvider.authToken = 'Token';
	$authProvider.tokenType = 'Token';
	
	$locale.NUMBER_FORMATS.GROUP_SEP = ' ';
});




/* Filter */

angular.module('FrontModule').filter('reverse', function() {
	
	return function(items) {
		if (!items) return;
		return items.slice().reverse();
	};
});