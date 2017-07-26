angular.module('SearchApp.services', [])

angular.module('SearchApp.services').service('SearchService', function(API) {
	
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

angular.module('SearchApp.directives', [])
angular.module('SearchApp.controllers', [])

angular.module('SearchApp.controllers').controller('SearchCtrl', function($scope, $state, toastr, $filter, $window, SearchService) {
	
	/* Search */
	
	$scope.search_loading = false;
	
	$scope.searchModel = {text:SearchService.data.search_text};

	$scope.no_result = SearchService.data.no_result;
	
	$scope.mosaics = SearchService.data.mosaics;

	$scope.search = function() {
		
		$scope.search_loading = true;
		
		$scope.no_result = false;
		
		$scope.cities = null;
		$scope.regions = null;
		$scope.mosaics = null;
		$scope.creators = null;
		$scope.countries = null;
	
		SearchService.reset();
		
		if ($scope.searchModel.text) {
			
			if ($scope.searchModel.text.length > 2) {
		
				SearchService.search($scope.searchModel.text).then(function(response) {
					
					$scope.no_result = SearchService.data.no_result;
					
					$scope.cities = SearchService.data.cities;
					$scope.regions = SearchService.data.regions;
					$scope.mosaics = SearchService.data.mosaics;
					$scope.creators = SearchService.data.creators;
					$scope.countries = SearchService.data.countries;
	
					$scope.search_loading = false;
				});
			}
			else {
					
				$scope.search_loading = false;
				
				toastr.error($filter('translate')('error_ATLEAST3CHAR'));
			}
		}
		else {
				
			$scope.search_loading = false;
			
			toastr.error($filter('translate')('error_ATLEAST3CHAR'));
		}
	}
	
	/* Go to ... */
	
	$scope.goToCreator = function(creator) {
		
		$state.go('root.creator', {'creator':creator.name});
	}

	$scope.goToCountry = function(country) {
		
		$state.go('root.country', {'country':country.name});
	}
	
	$scope.goToRegion = function(region) {
		
		$state.go('root.region', {'country':region.country, 'region':region.name});
	}
	
	$scope.goToCity = function(city) {
		
		$state.go('root.city', {'country':city.country, 'region':city.region, 'city':city.name});
	}
	
	$scope.goToMosaic = function(mosaic) {
		
		$window.location.href = '/mosaic/' + mosaic.ref;
	}
});
angular.module('SearchApp', ['FrontModule',
						     'SearchApp.services', 'SearchApp.controllers', 'SearchApp.directives',]);



/* Routing config */

angular.module('SearchApp').config(function($urlRouterProvider, $stateProvider, $locationProvider) {
	
	$stateProvider
			.state('root.search', { url: '/search', templateUrl: '/static/pages/search.html', data:{ title: 'search_TITLE', }, })
});
