angular.module('RegistrationApp', ['FrontModule',
								   'RegistrationApp.services', 'RegistrationApp.controllers', 'RegistrationApp.directives',]);



/* Routing config */

angular.module('RegistrationApp').config(function($urlRouterProvider, $stateProvider, $locationProvider) {
	
	$stateProvider
			.state('root.missions', { url: '/registration', controller:'MissionsCtrl', templateUrl: '/static/pages/missions.html', data:{ title: 'missions_TITLE', }, resolve: {loadMissions: function(UserService) { return UserService.getMissions(); }, }, })
			.state('root.create', { url: '/registration/create', controller:'CreateCtrl', templateUrl: '/static/pages/create.html', data:{ title: 'create_TITLE', }, })
			.state('root.plugin', { url: '/registration/plugin', controller:'PluginCtrl', templateUrl: '/static/pages/plugin.html', data:{ title: 'plugin_TITLE', }, })
});
