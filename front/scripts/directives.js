angular.module('FrontModule.directives', [])

angular.module('FrontModule.directives').directive('mosaicVignet', function() {
	
	return {
		
		replace: true,
		restrict: 'E',
		
		scope: { mosaic: '=' },
		
		template: '' +
			'<a class="btn-primary btn-block ta-center ttrans-normal" href="/mosaic/{{mosaic.ref}}">' +
				
			'	<div class="item" style="margin-bottom:.25rem; display:flex; justify-content:center; background:#0b0c0d; height:105px; overflow-y:hidden; padding:.25rem;" ng-class="{\'scrollbar valign-start\': mosaic.missions.length > 24, \'valign-center\': mosaic.missions.length <= 24}">' +
					
			'		<div class="row" style="align-items:center; justify-content:center; padding:0 calc((6 - {{mosaic.cols}}) / 2 * 16.666667%); width:100%;">' +
			'            <div ng-repeat="m in mosaic.missions | reverse" style="flex:0 0 calc(100% / {{mosaic.cols}});">' +
			'                <img src="/static/img/mask.png" style="width:100%; background-color:#000000; background-image:url({{m.image}}=s100); background-size: 95% 95%; background-position: 50% 50%; float:left; background-repeat: no-repeat;" />' +
			'           </div>' +
			'		</div>' +
					
			'	</div>' +
				
	        '   <div class="ellipsis" style="margin-bottom:.25rem;">' +
	        '		<i ng-if="mosaic.has_fake" class="fa fa-warning c-warning" style="padding-right:.5rem;"></i>{{mosaic.title}}' +
	        '	</div>' +
	        '   <div class="c-lighter ellipsis">' +
	        '       <flag country="mosaic.country.name"></flag>' +
	        '    	{{mosaic.location.name}}' +
	        '   </div>' +
	        '   <div class="c-lighter">{{mosaic.missions.length}} <i class="fa fa-th"></i> <span class="text-separator">&middot;</span> <span ng-if="mosaic.type == \'sequence\'">{{mosaic.distance | number:2}} km</span><span ng-if="mosaic.type == \'serie\'">serie</span><span ng-show="mosaic.type != \'serie\' && mosaic.distance > 10.0" class="text-separator">&middot;</span><i ng-show="mosaic.type != \'serie\' && mosaic.distance > 10.0 && mosaic.distance < 30.0" class="fa fa-bicycle"></i><i ng-show="mosaic.type != \'serie\' && mosaic.distance > 30.0" class="fa fa-car"></i></div>' +
				
			'</a>' +
		'',
	};
});

angular.module('FrontModule.directives').directive('flag', function() {
	
	return {
		
		replace: true,
		restrict: 'E',
		
		scope: { country: '=' },
		
		template: '' +
	        '       <span class="flag-icon" ng-class="{' +
	        '       		\'flag-icon-fr\': country == \'France\',' +
	        '       		\'flag-icon-gb\': country == \'United Kingdom\',' +
	        '       		\'flag-icon-my\': country == \'Malaysia\',' +
	        '       		\'flag-icon-sg\': country == \'Singapore\',' +
	        '       		\'flag-icon-us\': country == \'United States\',' +
	        '       		\'flag-icon-mx\': country == \'Mexico\',' +
	        '       		\'flag-icon-nz\': country == \'New Zealand\',' +
	        '       		\'flag-icon-mv\': country == \'Maldives\',' +
	        '       		\'flag-icon-do\': country == \'Dominican Republic\',' +
	        '       		\'flag-icon-au\': country == \'Australia\',' +
	        '       		\'flag-icon-hu\': country == \'Hungary\',' +
	        '       		\'flag-icon-lk\': country == \'Sri Lanka\',' +
	        '       		\'flag-icon-id\': country == \'Indonesia\',' +
	        '       		\'flag-icon-de\': country == \'Germany\',' +
	        '       		\'flag-icon-pl\': country == \'Poland\',' +
		    '       		\'flag-icon-ru\': country == \'Russia\',' +
		    '       		\'flag-icon-hk\': country == \'Hong Kong\',' +
		    '       		\'flag-icon-mu\': country == \'Mauritius\',' +
		    '       		\'flag-icon-th\': country == \'Thailand\',' +
		    '       		\'flag-icon-cz\': country == \'Czechia\',' +
		    '       		\'flag-icon-cn\': country == \'China\',' +
		    '       		\'flag-icon-es\': country == \'Spain\',' +
		    '       		\'flag-icon-ch\': country == \'Switzerland\',' +
		    '       		\'flag-icon-ca\': country == \'Canada\',' +
		    '       		\'flag-icon-at\': country == \'Austria\',' +
		    '       		\'flag-icon-is\': country == \'Iceland\',' +
		    '       		\'flag-icon-za\': country == \'South Africa\',' +
		    '       		\'flag-icon-ad\': country == \'Andorra\',' +
		    '       		\'flag-icon-it\': country == \'Italy\',' +
		    '       		\'flag-icon-il\': country == \'Israel\',' +
		    '       		\'flag-icon-pt\': country == \'Portugal\',' +
		    '       		\'flag-icon-ie\': country == \'Ireland\',' +
		    '       		\'flag-icon-gr\': country == \'Greece\',' +
		    '       		\'flag-icon-tr\': country == \'Turkey\',' +
		    '       		\'flag-icon-jp\': country == \'Japan\',' +
		    '       		\'flag-icon-dk\': country == \'Denmark\',' +
		    '       		\'flag-icon-se\': country == \'Sweden\',' +
		    '       		\'flag-icon-no\': country == \'Norway\',' +
		    '       		\'flag-icon-fi\': country == \'Finland\',' +
		    '       		\'flag-icon-lv\': country == \'Latvia\',' +
		    '       		\'flag-icon-ee\': country == \'Estonia\',' +
		    '       		\'flag-icon-lt\': country == \'Lithuania\',' +
		    '       		\'flag-icon-sk\': country == \'Slovakia\',' +
		    '       		\'flag-icon-hr\': country == \'Croatia\',' +
		    '       		\'flag-icon-ar\': country == \'Argentina\',' +
		    '       		\'flag-icon-uy\': country == \'Uruguay\',' +
		    '       		\'flag-icon-tw\': country == \'Taiwan\',' +
		    '       		\'flag-icon-in\': country == \'India\',' +
		    '       		\'flag-icon-nl\': country == \'Netherlands\',' +
		    '       		\'flag-icon-eg\': country == \'Egypt\',' +
		    '       		\'flag-icon-be\': country == \'Belgium\',' +
		    '       		\'flag-icon-ph\': country == \'Philippines\',' +
		    '       		\'flag-icon-pa\': country == \'Panama\',' +
	        '        	}"></span>' +
		'',
	};
});
