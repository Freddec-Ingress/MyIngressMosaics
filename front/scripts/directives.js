angular.module('FrontModule.directives', [])

angular.module('FrontModule.directives').directive('pageTitle', function($rootScope, $filter, $timeout) {
	
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

angular.module('FrontModule.directives').directive('convertToNumber', function() {
	
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

angular.module('FrontModule.directives').directive('mosaicVignet', function() {
	
	return {
		
		replace: true,
		restrict: 'E',
		
		scope: { mosaic: '=' },
		
		template: '' +
			'<a class="f-col m-2" href="/mosaic/{{mosaic.ref}}">' +
				
			'	<div class="card-block-bordered f-row f-justify-center scrollbar" style="height:100px; overflow-y:auto;" ng-class="{\'f-align-start scrollbar scrollbar-mini\': mosaic.missions.length > 24, \'f-align-center\': mosaic.missions.length <= 24}">' +
					
			'		<div class="f-row f-wrap f-justify-center f-align-center" style="padding:0 calc((6 - {{mosaic.cols}}) / 2 * 16.666667%); width:100%;">' +
			'            <div ng-repeat="m in mosaic.missions | reverse" style="flex:0 0 calc(100% / {{mosaic.cols}});">' +
			'                <img src="/static/img/mask.png" style="width:100%; background-color:#000000; background-image:url({{m.image}}=s100); background-size: 85% 85%; background-position: 50% 50%; float:left; background-repeat: no-repeat;" />' +
			'           </div>' +
			'		</div>' +
					
			'	</div>' +
				
			'	<div class="card-block text-center f-col">' +
					
	        '    	<div class="text-white mb-1" style="white-space:nowrap; text-overflow:ellipsis; overflow:hidden;">{{mosaic.title}}</div>' +
	        '   	<div class="text-normal">' +
	        '        	<span class="flag-icon mr-1 text-highlight" style="position:relative; top:-2px;" ng-class="{' +
	        '       		\'flag-icon-fr\': mosaic.country == \'France\',' +
	        '       		\'flag-icon-gb\': mosaic.country == \'United Kingdom\',' +
	        '       		\'flag-icon-my\': mosaic.country == \'Malaysia\',' +
	        '       		\'flag-icon-sg\': mosaic.country == \'Singapore\',' +
	        '       		\'flag-icon-us\': mosaic.country == \'United States\',' +
	        '       		\'flag-icon-mx\': mosaic.country == \'Mexico\',' +
	        '       		\'flag-icon-nz\': mosaic.country == \'New Zealand\',' +
	        '       		\'flag-icon-mv\': mosaic.country == \'Maldives\',' +
	        '       		\'flag-icon-do\': mosaic.country == \'Dominican Republic\',' +
	        '       		\'flag-icon-au\': mosaic.country == \'Australia\',' +
	        '       		\'flag-icon-hu\': mosaic.country == \'Hungary\',' +
	        '       		\'flag-icon-lk\': mosaic.country == \'Sri Lanka\',' +
	        '       		\'flag-icon-id\': mosaic.country == \'Indonesia\',' +
	        '       		\'flag-icon-de\': mosaic.country == \'Germany\',' +
	        '       		\'flag-icon-pl\': mosaic.country == \'Poland\',' +
		    '       		\'flag-icon-ru\': mosaic.country == \'Russia\',' +
		    '       		\'flag-icon-hk\': mosaic.country == \'Hong Kong\',' +
		    '       		\'flag-icon-mu\': mosaic.country == \'Mauritius\',' +
		    '       		\'flag-icon-th\': mosaic.country == \'Thailand\',' +
		    '       		\'flag-icon-cz\': mosaic.country == \'Czechia\',' +
	        '        	}"></span>' +
	        '    		{{mosaic.city}}' +
	        '    	</div>' +
	        '    	<div class="text-normal">{{mosaic.missions.length}} missions &middot; {{mosaic._distance | number:2}} km</div>' +
	            	
			'	</div>' +
				
			'</a>' +
		'',
	};
});