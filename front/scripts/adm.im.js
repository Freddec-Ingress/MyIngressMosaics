angular.module('FrontModule.controllers').controller('AdmImCtrl', function($scope, API) {

	$scope.clipboardCopy = function(country) {
		
		var index = $scope.countries.indexOf(country);
		var input_country = $('#country_input_' + index);
		
		input_country.select();
		document.execCommand('Copy');
	}
	
	/* Page loading */
	
	$scope.loaded = true;
});