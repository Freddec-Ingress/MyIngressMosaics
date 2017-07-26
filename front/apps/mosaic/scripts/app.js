angular.module('MosaicApp', ['FrontModule',
						     'MosaicApp.services', 'MosaicApp.controllers', 'MosaicApp.directives',]);



/* Routing config */

angular.module('MosaicApp').config(function($urlRouterProvider, $stateProvider, $locationProvider) {
	
	$stateProvider
			.state('root.mosaic', { url: '/mosaic/:ref', controller:'MosaicCtrl', templateUrl: '/static/pages/mosaic.html', data:{ title: 'mosaicpage_TITLE', }, resolve: {loadMosaic: function($stateParams, MosaicService) { return MosaicService.getMosaic($stateParams.ref); }, }, })
});
