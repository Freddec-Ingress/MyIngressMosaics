angular.module('FrontModule', ['satellizer', 'ngCookies',
							   'FrontModule.services', 'FrontModule.controllers', 'FrontModule.directives', ]);



/* Config */

angular.module('FrontModule').config(function($authProvider) {
	
	$authProvider.facebook({
		
		url: '/login/social/token_user/facebook',
		clientId: '237811833398918'
	});

	$authProvider.google({
		
		url: '/accounts.google.com/o/oauth2/v2/auth',
		clientId: '404579985700-eig13jlsdvbe6bhmtsis46tsn7nij4ju.apps.googleusercontent.com'
	});

	$authProvider.authToken = 'Token';
	$authProvider.tokenType = 'Token';
});



/* Running */

angular.module('FrontModule').run(['$locale', function($locale) {
	
	$locale.NUMBER_FORMATS.GROUP_SEP = ' ';
	$locale.NUMBER_FORMATS.DECIMAL_SEP = '.';
}]);



/* Filter */

angular.module('FrontModule').filter('reverse', function() {
	
	return function(items) {
		if (!items) return;
		return items.slice().reverse();
	};
});