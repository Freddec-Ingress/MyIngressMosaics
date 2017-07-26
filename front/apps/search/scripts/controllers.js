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