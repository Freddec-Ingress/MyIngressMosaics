angular.module('FrontModule.directives', [])

angular.module('FrontModule.directives').directive('mosaicVignet', function() {
	
	return {
		
		replace: true,
		restrict: 'E',
		
		scope: { mosaic: '=' },
		
		template: '' +
			'<a class="btn btn-primary text-transform-normal f-col p-2" style="align-items:initial!important;" href="/mosaic/{{mosaic.ref}}">' +
				
			'	<div class="bg-black f-row f-justify-center" style="height:105px; overflow-y:auto; padding-top:4px; padding-bottom:4px; padding-left:4px;" ng-class="{\'f-align-start scrollbar scrollbar-mini\': mosaic.missions.length > 24, \'f-align-center pr-1\': mosaic.missions.length <= 24}">' +
					
			'		<div class="f-row f-wrap f-justify-center f-align-center" style="padding:0 calc((6 - {{mosaic.cols}}) / 2 * 16.666667%); width:100%;">' +
			'            <div ng-repeat="m in mosaic.missions | reverse" style="flex:0 0 calc(100% / {{mosaic.cols}});">' +
			'                <img src="/static/img/mask.png" style="width:100%; background-color:#000000; background-image:url({{m.image}}=s100); background-size: 95% 95%; background-position: 50% 50%; float:left; background-repeat: no-repeat;" />' +
			'           </div>' +
			'		</div>' +
					
			'	</div>' +
				
			'	<div class="f-col">' +
					
	        '    	<div class="text-white mt-2 mb-1" style="white-space:nowrap; text-overflow:ellipsis; overflow:hidden;">{{mosaic.title}}</div>' +
	        '   	<div class="text-normal mb-1" style="white-space:nowrap; text-overflow:ellipsis; overflow:hidden;">' +
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
		    '       		\'flag-icon-cn\': mosaic.country == \'China\',' +
		    '       		\'flag-icon-es\': mosaic.country == \'Spain\',' +
		    '       		\'flag-icon-ch\': mosaic.country == \'Switzerland\',' +
		    '       		\'flag-icon-ca\': mosaic.country == \'Canada\',' +
		    '       		\'flag-icon-at\': mosaic.country == \'Austria\',' +
		    '       		\'flag-icon-is\': mosaic.country == \'Iceland\',' +
		    '       		\'flag-icon-za\': mosaic.country == \'South Africa\',' +
		    '       		\'flag-icon-ad\': mosaic.country == \'Andorra\',' +
		    '       		\'flag-icon-it\': mosaic.country == \'Italy\',' +
		    '       		\'flag-icon-il\': mosaic.country == \'Israel\',' +
		    '       		\'flag-icon-pt\': mosaic.country == \'Portugal\',' +
		    '       		\'flag-icon-ie\': mosaic.country == \'Ireland\',' +
		    '       		\'flag-icon-gr\': mosaic.country == \'Greece\',' +
		    '       		\'flag-icon-tr\': mosaic.country == \'Turkey\',' +
		    '       		\'flag-icon-jp\': mosaic.country == \'Japan\',' +
		    '       		\'flag-icon-dk\': mosaic.country == \'Denmark\',' +
		    '       		\'flag-icon-se\': mosaic.country == \'Sweden\',' +
		    '       		\'flag-icon-no\': mosaic.country == \'Norway\',' +
		    '       		\'flag-icon-fi\': mosaic.country == \'Finland\',' +
		    '       		\'flag-icon-lv\': mosaic.country == \'Latvia\',' +
		    '       		\'flag-icon-ee\': mosaic.country == \'Estonia\',' +
		    '       		\'flag-icon-lt\': mosaic.country == \'Lithuania\',' +
		    '       		\'flag-icon-sk\': mosaic.country == \'Slovakia\',' +
		    '       		\'flag-icon-hr\': mosaic.country == \'Croatia\',' +
		    '       		\'flag-icon-ar\': mosaic.country == \'Argentina\',' +
		    '       		\'flag-icon-uy\': mosaic.country == \'Uruguay\',' +
		    '       		\'flag-icon-tw\': mosaic.country == \'Taiwan\',' +
		    '       		\'flag-icon-in\': mosaic.country == \'India\',' +
	        '        	}"></span>' +
	        '    		{{mosaic.location}}' +
	        '    	</div>' +
	        '    	<div class="text-normal">{{mosaic.missions.length}} <i class="fa fa-th mx-1"></i> <span class="mr-1">&middot;</span> <span ng-if="mosaic.type == \'sequence\'">{{mosaic.distance | number:2}} km</span><span ng-if="mosaic.type == \'serie\'">serie</span><span ng-show="mosaic.type != \'serie\' && mosaic.distance > 10.0" class="mx-1">&middot;</span><i ng-show="mosaic.type != \'serie\' && mosaic.distance > 10.0 && mosaic.distance < 30.0" class="fa fa-bicycle mx-1"></i><i ng-show="mosaic.type != \'serie\' && mosaic.distance > 30.0" class="fa fa-car mx-1"></i></div>' +
	            	
			'	</div>' +
				
			'</a>' +
		'',
	};
});