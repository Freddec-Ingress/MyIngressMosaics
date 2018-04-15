angular.module('FrontModule.controllers').controller('AdmImCtrl', function($scope, API) {

	$scope.clipboardCopy = function(index) {
		
		var input_country = $('#country_input_' + index);
		
		input_country.select();
		document.execCommand('Copy');
	}
	
	/* Page loading */
	
	$scope.init = function(countries) {
		
		$scope.countries = countries;
		
		$scope.loaded = true;
	}
});