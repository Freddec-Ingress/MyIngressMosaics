angular.module('AngularApp.directives', [])

angular.module('AngularApp.directives').directive('pageTitle', function($rootScope, $filter, $timeout) {
	
	return {
		
		link: function(scope, element) {
		
			var listener = function(event, toState) {
			
				var title = 'MyIngressMosaics';
				if (toState.data && toState.data.title) title = 'MyIngressMosaics - ' + $filter('translate')(toState.data.title);
				
				$timeout(function() { element.text(title); }, 0, false);
			};
			
			$rootScope.$on('$stateChangeSuccess', listener);
		}
	};
});

angular.module('AngularApp.directives').directive('convertToNumber', function() {
	
	return {
		
		require: 'ngModel',
		
		link: function(scope, element, attrs, ngModel) {
			
			ngModel.$parsers.push(function(val) {
				return val != null ? parseInt(val, 10) : null;
			});
			
			ngModel.$formatters.push(function(val) {
				return val != null ? '' + val : null;
			});
		}
	};
});