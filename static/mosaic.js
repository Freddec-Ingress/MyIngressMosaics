angular.module('MosaicApp.services', [])

angular.module('MosaicApp.services').service('MosaicService', function($state, API, DataService) {
	
	var service = {

		data: {
			
			mosaic: null,
			potentials: null,
		},
		
		sortMPotentialsByName: function(sort) {
			
			function compareNameAsc(a, b) {
				
				var a_name = a.name.toLowerCase().replace(/0|1|2|3|4|5|6|7|8|9/g, '');
				var b_name = b.name.toLowerCase().replace(/0|1|2|3|4|5|6|7|8|9/g, '');
				
				if (a_name < b_name)
					return -1;
					
				if (a_name > b_name)
					return 1;

				var a_name = a.name;
				var b_name = b.name;
				
				if (a_name < b_name)
					return -1;
					
				if (a_name > b_name)
					return 1;
					
				var a_creator = a.creator.toLowerCase();
				var b_creator = b.creator.toLowerCase();
				
				if (a_creator < b_creator)
					return -1;
					
				if (a_creator > b_creator)
					return 1;

				return 0;
			}
			
			function compareNameDesc(a, b) {
				
				var a_name = a.name.toLowerCase().replace(/0|1|2|3|4|5|6|7|8|9/g, '');
				var b_name = b.name.toLowerCase().replace(/0|1|2|3|4|5|6|7|8|9/g, '');
				
				if (a_name > b_name)
					return -1;
					
				if (a_name < b_name)
					return 1;

				var a_name = a.name;
				var b_name = b.name;
				
				if (a_name > b_name)
					return -1;
					
				if (a_name < b_name)
					return 1;
					
				var a_creator = a.creator.toLowerCase();
				var b_creator = b.creator.toLowerCase();
				
				if (a_creator > b_creator)
					return -1;
					
				if (a_creator < b_creator)
					return 1;
				
				return 0;
			}
			
			if (service.data.potentials) {
				
				if (sort == 'asc') service.data.potentials.sort(compareNameAsc);
				if (sort == 'desc') service.data.potentials.sort(compareNameDesc);
			}
		},

		getMosaic: function(ref) {
			
			var data = { 'ref':ref };
			API.sendRequest('/api/mosaic/potential/', 'POST', {}, data).then(function(response) {
				
				if (response) {
					
					for (var m of response) {
						
						var order = 0;
						
						var found = m.name.match(/[0-9]+/);
						if (found) order = parseInt(found[0]);

						m.order = order;
					}
					
					service.data.potentials = response;
					service.sortMPotentialsByName();
				}
			});
			
			return API.sendRequest('/api/mosaic/' + ref + '/', 'GET').then(function(response) {
				
				service.data.mosaic = response;
			});
		},
		
		getImageByOrder: function(order) {
			
			var url = null;
			
			if (service.data.mosaic) {
				for (var item of service.data.mosaic.missions) {
					if ((service.data.mosaic.count - item.order + 1) == order) {
						url = item.image;
						break;
					}
				}
			}
			
			return url;
		},
		
		getColsArray: function() {
			
			var temp = 1;
			if (service.data.mosaic.cols > 0) temp = service.data.mosaic.cols;
			if (!temp) temp = 1;
			
			var cols = [];
			for (var i = 0; i < temp; i++) {
				cols.push(i);
			}

			return cols;
		},
		
		getRowsArray: function() {
			
			var temp = 1;
			if (service.data.mosaic.count > 0 && service.data.mosaic.cols > 0) temp = Math.ceil(service.data.mosaic.count / service.data.mosaic.cols);
			if (!temp) temp = 1;
			
			var rows = [];
			for (var i = 0; i < temp; i++) {
				rows.push(i);
			}
			
			return rows;
		},
		
		edit: function(data) {
			
			return API.sendRequest('/api/mosaic/edit/', 'POST', {}, data).then(function(response) {
				
				service.data.mosaic.city = response.city;
				service.data.mosaic.desc = response.desc;
				service.data.mosaic.type = response.type;
				service.data.mosaic.cols = response.cols;
				service.data.mosaic.rows = response.rows;
				service.data.mosaic.title = response.title;
				service.data.mosaic.region = response.region;
				service.data.mosaic.country = response.country;
			});
		},

		reorder: function(data) {
			
			return API.sendRequest('/api/mosaic/reorder/', 'POST', {}, data).then(function(response) {
				
				service.data.mosaic._distance = response._distance;
				service.data.mosaic.missions = response.missions;
			});
		},
		
		delete: function(neworder) {
			
			var data = { 'ref':service.data.mosaic.ref, };
			return API.sendRequest('/api/mosaic/delete/', 'POST', {}, data).then(function(response) {
					
				DataService.current_city = service.data.mosaic.city;
				$state.go('root.city', {'country':service.data.mosaic.country, 'region':service.data.mosaic.region, 'city':service.data.mosaic.city});
				
				service.data.mosaic = null;
			});
		},
		
		remove: function(mission) {
			
			var data = { 'ref':service.data.mosaic.ref, 'mission':mission };
			return API.sendRequest('/api/mosaic/remove/', 'POST', {}, data).then(function(response) {
					
				service.data.mosaic.creators = response.creators;
				service.data.mosaic._distance = response._distance;
				service.data.mosaic.missions = response.missions;
			});
		},
		
		add: function(mission, order) {
			
			var data = { 'ref':service.data.mosaic.ref, 'mission':mission, 'order':order };
			return API.sendRequest('/api/mosaic/add/', 'POST', {}, data).then(function(response) {
					
				service.data.mosaic.creators = response.creators;
				service.data.mosaic._distance = response._distance;
				service.data.mosaic.missions = response.missions;
			});
		},
		
		repair: function() {
			
			var data = {'ref':service.data.mosaic.ref};
			return API.sendRequest('/api/mosaic/repair/', 'POST', {}, data);
		},
	};
	
	return service;
});

angular.module('MosaicApp.directives', [])
angular.module('MosaicApp.controllers', [])

angular.module('MosaicApp.controllers').controller('MosaicCtrl', function($scope, $state, $timeout, $window, $filter, toastr, MosaicService) {

	$scope.mosaic = MosaicService.data.mosaic;
	$scope.potentials = MosaicService.data.potentials;
	
	$scope.remove = MosaicService.remove;
	
	/* Edit */
	
	$scope.editMode = false;
	$scope.editLoading = false;
	
	$scope.editModel = {ref:null, city:null, region:null, desc:null, type:null, cols:null, rows:null, title:null, country:null};
	
	$scope.openEdit = function() {
		
		$scope.editModel.ref = $scope.mosaic.ref;
		$scope.editModel.city = $scope.mosaic.city;
		$scope.editModel.desc = $scope.mosaic.desc;
		$scope.editModel.type = $scope.mosaic.type;
		$scope.editModel.cols = $scope.mosaic.cols;
		$scope.editModel.rows = $scope.mosaic.rows;
		$scope.editModel.title = $scope.mosaic.title;
		$scope.editModel.region = $scope.mosaic.region;
		$scope.editModel.country = $scope.mosaic.country;
		
		$scope.editMode = true;
	}
	
	$scope.closeEdit = function() {
		
		$scope.editMode = false;
	}
	
	$scope.edit = function() {
		
		$scope.editLoading = true;
			
		MosaicService.edit($scope.editModel).then(function(response) {
			
			toastr.success($filter('translate')('success_EDIT'));

			$scope.editMode = false;
			$scope.editLoading = false;
			
		}, function(response) {
			
			$scope.editMode = false;
			$scope.editLoading = false;
		});
	}
	
	/* Reorder */
	
	$scope.reorderMode = false;
	$scope.reorderLoading = false;
	
	$scope.reorderModel = {ref:null, missions:null};
	
	$scope.openReorder = function() {
		
		$scope.reorderModel.ref = $scope.mosaic.ref;
		$scope.reorderModel.missions = $scope.mosaic.missions;

		$scope.reorderMode = true;
	}
	
	$scope.closeReorder = function() {
		
		$scope.reorderMode = false;
	}
	
	$scope.reorder = function() {
		
		$scope.reorderLoading = true;
			
		MosaicService.reorder($scope.reorderModel).then(function(response) {
			
			toastr.success($filter('translate')('success_REORDER'));

			$scope.reorderMode = false;
			$scope.reorderLoading = false;
			
		}, function(response) {
			
			$scope.reorderMode = false;
			$scope.reorderLoading = false;
		});
	}
	
	/* Add */
	
	$scope.addMode = false;
	
	$scope.openAdd = function() {
		
		$scope.addMode = true;
	}
	
	$scope.closeAdd = function() {
		
		$scope.addMode = false;
	}
	
	$scope.add = function(item, order) {
		
		var index = $scope.potentials.indexOf(item);
		if (index > -1) {
		    $scope.potentials.splice(index, 1);
		}
		
		item.order = order
		
		MosaicService.add(item.ref, order);
	}
	
	/* Delete */
	
	$scope.deleteModel = {name:null};
	
	$scope.delete = function() {
		
		if ($scope.deleteModel.name == $scope.mosaic.title) {
			
			MosaicService.delete();
		}
	}
	
	/* Repair */
	
	$scope.repair = function() {
		
		MosaicService.repair().then(function(response) {
			
			$state.reload();
		});
	}
	
	/* Map */

	$scope.initMap = function() {
		
		var style = [{featureType:"all",elementType:"all",stylers:[{visibility:"on"},{hue:"#131c1c"},{saturation:"-50"},{invert_lightness:!0}]},{featureType:"water",elementType:"all",stylers:[{visibility:"on"},{hue:"#005eff"},{invert_lightness:!0}]},{featureType:"poi",stylers:[{visibility:"off"}]},{featureType:"transit",elementType:"all",stylers:[{visibility:"off"}]},{featureType:"road",elementType:"labels.icon",stylers:[{invert_lightness:!0}]}];
		
		var map = new google.maps.Map(document.getElementById('map'), {
			
			zoom: 8,
			styles : style,
			zoomControl: true,
			disableDefaultUI: true,
			fullscreenControl: true,
			center: {lat: $scope.mosaic.missions[0].lat, lng: $scope.mosaic.missions[0].lng},
		});
		
		var latlngbounds = new google.maps.LatLngBounds();
		
		var image = {
			size: new google.maps.Size(50, 50),
			origin: new google.maps.Point(0, 0),
			anchor: new google.maps.Point(25, 25),
			labelOrigin: new google.maps.Point(25, 27),
			url: 'https://www.myingressmosaics.com/static/front/img/neutral.png',
		};
		
		var lineSymbol = {
			path: 'M 0,0 0,-5',
			strokeOpacity: 1,
			scale: 2
		};
		
		var arrowSymbol = {
			path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW
		};
		
		var nextlatLng = null;
		var previouslatLng = null;
		
		for (var m of $scope.mosaic.missions) {
		
			/* Mission marker */
			
	        var marker = new google.maps.Marker({
	        	
				map: map,
				icon: image,
				label: { text:String(m.order), color:'#FFFFFF', fontFamily:'Coda', fontSize:'.75rem', fontWeight:'400', },
				position: {lat: m.lat, lng: m.lng},
	        });
	        
	        var mlatLng = new google.maps.LatLng(m.lat, m.lng);
	        latlngbounds.extend(mlatLng);
	        
	        /* Mission transit */
	        
	        nextlatLng = mlatLng;
	        
	        if (nextlatLng && previouslatLng) {
	        	
				var transitRoadmapCoordinates= [];
				
		        transitRoadmapCoordinates.push(previouslatLng);
		        transitRoadmapCoordinates.push(nextlatLng);
		        
				var transitRoadmap = new google.maps.Polyline({
					path: transitRoadmapCoordinates,
					geodesic: true,
					strokeColor: '#ebbc4a',
					strokeOpacity: 0,
					strokeWeight: 2,
					icons: [{
						icon: lineSymbol,
						offset: '0',
						repeat: '20px'
					},],
		        });
		        
		        transitRoadmap.setMap(map);
	        }

			/* Mission roadmap */
			
			var roadmapCoordinates= [];
		
			for (var p of m.portals) {
				
				if (p.lat != 0.0 && p.lng != 0.0) {
					
			        var platLng = new google.maps.LatLng(p.lat, p.lng);
			        roadmapCoordinates.push(platLng);
			        
			        previouslatLng = platLng;
				}
			}
	        
			var roadmap = new google.maps.Polyline({
				path: roadmapCoordinates,
				geodesic: true,
				strokeColor: '#ebbc4a',
				strokeOpacity: 0.95,
				strokeWeight: 2,
				icons: [{
					icon: arrowSymbol,
					offset: '100%',
				},],
			});
	        
	        roadmap.setMap(map);
	        
		}
		
		map.setCenter(latlngbounds.getCenter());
		map.fitBounds(latlngbounds); 
	}
	
	/* Go to a creator page */
	
	$scope.goToCreator = function(creator) {
		
		$state.go('root.creator', {'creator':creator});
	}
	
	/* Go to a location page */
	
	$scope.goToCountry = function() {
		
		$state.go('root.country', {'country':$scope.mosaic.country});
	}
	
	$scope.goToRegion = function() {
		
		$state.go('root.region', {'country':$scope.mosaic.country, 'region':$scope.mosaic.region});
	}
	
	$scope.goToCity = function() {
		
		$state.go('root.city', {'country':$scope.mosaic.country, 'region':$scope.mosaic.region, 'city':$scope.mosaic.city});
	}
});
angular.module('MosaicApp', ['FrontModule',
						     'MosaicApp.services', 'MosaicApp.controllers', 'MosaicApp.directives',]);



/* Routing config */

angular.module('MosaicApp').config(function($urlRouterProvider, $stateProvider, $locationProvider) {
	
	$stateProvider
			.state('root.mosaic', { url: '/mosaic/:ref', controller:'MosaicCtrl', templateUrl: '/static/pages/mosaic.html', data:{ title: 'mosaicpage_TITLE', }, resolve: {loadMosaic: function($stateParams, MosaicService) { return MosaicService.getMosaic($stateParams.ref); }, }, })
});
