angular.module('FrontModule.directives', [])

angular.module('FrontModule.directives').directive('mosaic', function() {
	
	return {
		
		replace: true,
		restrict: 'E',
		
		scope: { mosaic: '=' },
		
		template: '' +
			'<div class="item width-12 width-xl-4 flex-col">' +
				'<div class="item link-block" style="height:100%">' +
					
					'<a class="item" href="/mosaic/[[mosaic.ref]]" target="_blank" style="display:block;">' +
						'<div class="flex align-center">' +
							'<i class="mr-normal text-small fa fa-exclamation-triangle color-danger" title="Some portals are unavailable!" ng-show="mosaic.has_unavailable_portals"></i>' +
							'<span class="mr-normal grow text-medium color-light ellipsis" title="[[mosaic.title]]">[[mosaic.title]]</span>' +
							'<i class="fa fa-angle-right"></i>' +
						'</div>' +
						'<span class="text-small color-dark"><span class="color-normal">[[mosaic.images.length]]</span> missions &middot; <span class="color-normal">[[mosaic.unique_count]]</span> uniques</span>' +
					'</a>' +
					
					'<div class="item pt-none">' +
						'<a class="flex" href="/world/[[mosaic.country_name]]/[[mosaic.region_name]]/[[mosaic.city_name]]">' +
							'<span class="mr-small flag-icon flag-icon-[[mosaic.country_code]]"></span>' +
							'<span>[[mosaic.city_name]]</span>' +
						'</a>' +
					'</div>' +

					'<a class="item" href="/mosaic/[[mosaic.ref]]" target="_blank" style="display:block;">' +
						'<div class="flex wrap shrink" style="max-width:150px; padding-right:calc((6 - [[mosaic.cols]]) * 25px);">' +
							
							'<div ng-repeat="m in mosaic.offset track by $index" style="flex:0 0 calc(100% / [[mosaic.cols]]);">' +
							'</div>' +
							
							'<div ng-repeat="m in mosaic.images track by $index" class="mission-vignet" style="max-width:25px; flex:0 0 calc(100% / [[mosaic.cols]]);">' +
								'<img src="/static/img/mask.png" style="width:25px; background-image:url([[m]]=s25);" />' +
							'</div>' +
							
						'</div>' +
					'</a>' +
					
				'</div>' +
			'</div>' +
		'',
	};
});

angular.module('FrontModule.directives').directive('potential', function() {
	
	return {
		
		replace: true,
		restrict: 'E',
		
		scope: { potential: '=' },
		
		template: '' +
			'<div class="item width-12 width-xl-4">' +
				'<div class="item link-block">' +
					
					'<a class="item" href="/registration/[[potential.title]]" target="_blank" style="display:block;">' +
						'<div class="flex align-center">' +
							'<span class="mr-normal grow text-medium color-light ellipsis" title="[[potential.title]]">[[potential.title]]</span>' +
							'<i class="fa fa-angle-right"></i>' +
						'</div>' +
						'<span class="text-small color-dark">[[potential.mission_count]] missions</span>' +
					'</a>' +
					
					'<div class="item pt-none">' +
						'<a class="flex" href="/world/[[potential.country_name]]/[[potential.region_name]]/[[potential.city_name]]">' +
							'<span class="mr-small flag-icon flag-icon-[[potential.country_code]]"></span>' +
							'<span>[[potential.city_name]]</span>' +
						'</a>' +
					'</div>' +
					
				'</div>' +
			'</div>' +
		'',
	};
});

angular.module('FrontModule.directives').directive('mission', function() {
	
	return {
		
		replace: true,
		restrict: 'E',
		
		scope: { mission: '=' },
		
		template: '' +
			'<div class="width-12 width-xl-6 item">' +
				'<div class="item bg-block flex align-center">' +
				
					'<div class="item">' +
						'<img src="/static/img/mask.png" style="width:26px; background-color:#000000; background-image:url([[mission.image]]=s25); background-size: 95% 95%; background-position: 50% 50%; float:left; background-repeat: no-repeat;" />' +
					'</div>' +
					
					'<div class="item grow ellipsis">' +
						
						'<div class="ellipsis">' +
							'<span class="text-medium color-light" title="[[mission.title]]">[[mission.title]]</span>' +
						'</div>' +
						
						'<div class="text-small">' +
							'<a href="/search/[[mission.creator]]" ng-class="{\'color-enlightened\': mission.faction == \'E\', \'color-resistant\': mission.faction == \'R\'}">[[mission.creator]]</a>' +
						'</div>' +
						
					'</div>' +

					'<div class="item">' +
						'<a href="https://www.ingress.com/intel?ll=[[mission.startLat]],[[mission.startLng]]&z=19&pll=[[mission.startLat]],[[mission.startLng]]" target="_blank">' +
							'<i class="fa fa-external-link"></i>' +
						'</a>' +
					'</div>' +
							
				'</div>' +
			'</div>' +
		'',
	};
});