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