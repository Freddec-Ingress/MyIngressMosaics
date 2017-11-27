angular.module('FrontModule.controllers').controller('NewRegistrationCtrl', function($scope, $window, toastr, API, UtilsService) {
	
	/* Tab management */
	
	$scope.current_step = 0;
	
	$scope.open_step = function(id) {
		
		$scope.current_step = id;
		
		if ($scope.current_step == 3) {
			
			if (!$scope.mosaic_name) $scope.computeMosaicName();
			if (!$scope.city_name || !$scope.region_name || !$scope.country_name) $scope.computeLocation();
		}
	}
	
	/* Step #1 management */
	
	$scope.missions = [];
	$scope.selected = [];
	
	$scope.refreshing = false;
	
	$scope.searchText = '';
	
	$scope.refreshMissions = function(text) {
		
		if (!text) return;
		
		if (text.length < 3) return;
		
		$scope.searchText = text;
		
		$scope.refreshing = true;
		
		$scope.missions = [];
		
		var data = { 'text':text };
		API.sendRequest('/api/new_missions/', 'POST', {}, data).then(function(response) {
			
			$scope.missions = response.missions;
			if (!$scope.missions) $scope.missions = [];

			$scope.missions.sort(UtilsService.sortMissionsByCreatorTitleAsc);
			
			for (var mission of $scope.missions) {
				for (var select of $scope.selected) {
					if (mission.ref == select.ref) {
						mission.selected = true;
						break;
					}
				}
			}

			$scope.refreshing = false;
		});
	}

	$scope.toggleSelectMission = function(mission) {
	
		mission.selected = !mission.selected;
		
		if (mission.selected) {
			
			$scope.selected.push(mission);
			
			var order = UtilsService.getOrderFromMissionName(mission.title);
			if (order < 1) order = $scope.selected.indexOf(mission) + 1;
			mission.order = order.toString();
			
			$scope.selected.sort(UtilsService.sortMissionsByOrderTitleAsc);
			
			$scope.computeOffset();
		}
		else {
			
			var index = $scope.selected.indexOf(mission);
			$scope.selected.splice(index, 1);
		}
	}
	
	$scope.selectAll = function() {
		
		for (var mission of $scope.missions) {
			if (!mission.selected) {
				$scope.toggleSelectMission(mission);
			}
		}
	}
	
	/* Step #2 management */
	
	$scope.columns = '6';
	
	$scope.offset = [];
	
	$scope.mission_selected = null;

	$scope.addFake = function(fakeorder) {
		
		var mission = {
			'ref': 'Unavailable',
			'order': fakeorder,
			'title': 'Fake mission',
		}
		
		$scope.selected.push(mission);
		
		$scope.selected.sort(UtilsService.sortMissionsByOrderTitleAsc);
		
		$scope.computeOffset();
	}
	
	$scope.computeOffset = function() {
		
		var temp = 0;
		if ($scope.selected.length > $scope.columns) {
			temp = $scope.columns - $scope.selected.length % $scope.columns;
			if (temp < 0 || temp > ($scope.columns - 1)) temp = 0;
		}
		
		$scope.offset = new Array(temp);
	}
	
	$scope.displayOrder = function(mission) {
		
		$scope.mission_selected = mission;
	}

	$scope.closeOrder = function() {
		
		$scope.mission_selected = null;
	}
	
	$scope.saveOrder = function(order) {
		
		if (!order) return;
		
		$scope.mission_selected.order = order;
		$scope.selected.sort(UtilsService.sortMissionsByOrderTitleAsc);
		
		$scope.closeOrder();
	}
	
	$scope.retireMission = function(mission) {
		
		var index = $scope.selected.indexOf(mission);
		$scope.selected.splice(index, 1);
		
		$scope.closeOrder();
	}
	
	$scope.reorderAsc = function() {
		
		var index = 0;
		for (var m of $scope.selected) {
			
			index += 1;
			m.order = index;
		}
		
		$scope.selected.sort(UtilsService.sortMissionsByOrderTitleAsc);
	}
	
	$scope.reorderDesc = function() {
		
		var index = $scope.selected.length + 1;
		for (var m of $scope.selected) {
			
			index -= 1;
			m.order = index;
		}
		
		$scope.selected.sort(UtilsService.sortMissionsByOrderTitleAsc);
	}
	
	/* Step #3 management */
	
	$scope.mosaic_name = '';
	$scope.mosaic_type = 'sequence';
	
	$scope.city_name = '';
	$scope.region_name = '';
	$scope.country_name = '';
	
	$scope.computeMosaicName = function() {
		
		$scope.mosaic_name = '';
		
		var mosaic_name = $scope.selected[0].title;
		mosaic_name = mosaic_name.replace(/0|1|2|3|4|5|6|7|8|9|#/g, '');
		mosaic_name = mosaic_name.replace(/０|１|２|３|４|５|６|７|８|９/g, '');
		mosaic_name = mosaic_name.replace(/①|②|③|④|⑤|⑥/g, '');
		mosaic_name = mosaic_name.replace('.', '');
		mosaic_name = mosaic_name.replace('(', '');
		mosaic_name = mosaic_name.replace(')', '');
		mosaic_name = mosaic_name.replace('（', '');
		mosaic_name = mosaic_name.replace('）', '');
		mosaic_name = mosaic_name.replace('/', '');
		mosaic_name = mosaic_name.replace('[', '');
		mosaic_name = mosaic_name.replace(']', '');
		mosaic_name = mosaic_name.replace('【', '');
		mosaic_name = mosaic_name.replace('】', '');
		mosaic_name = mosaic_name.replace('-', '');
		mosaic_name = mosaic_name.replace('-', '');
		mosaic_name = mosaic_name.replace('－', '');
		mosaic_name = mosaic_name.replace('_', '');
		mosaic_name = mosaic_name.replace(':', '');
		mosaic_name = mosaic_name.replace('of ', '');
		mosaic_name = mosaic_name.replace(' of', '');
		mosaic_name = mosaic_name.replace('part ', '');
		mosaic_name = mosaic_name.replace(' part', '');
		mosaic_name = mosaic_name.replace('Part ', '');
		mosaic_name = mosaic_name.replace(' Part', '');
		mosaic_name = mosaic_name.replace('  ', ' ');
		mosaic_name = mosaic_name.replace('  ', ' ');
		mosaic_name = mosaic_name.replace('　', ' ');
		mosaic_name = mosaic_name.trim();
		
		$scope.mosaic_name = mosaic_name;
	}
	
	$scope.computeLocation = function() {
		
		$scope.city_name = '';
		$scope.region_name = '';
		$scope.country_name = '';
		
		var geocoder = new google.maps.Geocoder;
		
		var latlng = {
			lat: parseFloat($scope.selected[0].startLat),
			lng: parseFloat($scope.selected[0].startLng),
		};

		geocoder.geocode({'location': latlng}, function(results, status) {
			
			if (status === 'OK') {
				
				var components = null;
				if (results[0]) components = results[0].address_components;
				if (results[1]) components = results[1].address_components;
				
				if (components) {
					
					console.log(components);
					
					var admin2 = null;
					var admin3 = null;
					
					for (var item of components) {
						
						if (item.types[0] == 'country') $scope.country_name = item.long_name;
						if (item.types[0] == 'locality') $scope.city_name = item.long_name;
						if (item.types[0] == 'administrative_area_level_1') $scope.region_name = item.long_name;
						if (item.types[0] == 'administrative_area_level_2') admin2 = item.long_name;
						if (item.types[0] == 'administrative_area_level_3') admin3 = item.long_name;
					}
					
					if (!$scope.city_name && admin2) $scope.city_name = admin2;
					if (!$scope.city_name && admin3) $scope.city_name = admin3;
					
					console.log($scope.city_name);
					
					/* Country */
					
					API.sendRequest('/api/country/list/', 'POST').then(function(response) {
						
						var countryList = response.countries;

						var cur_country = null;
						for (var country of countryList) {
							if (country.name == $scope.country_name || country.locale == $scope.country_name) {
								
								cur_country = country;
								
								$scope.country_name = country.name;
								break;
							}
						}
						
						/* Region */
						
						if (cur_country) {
							
							var data = {'country_id':cur_country.id};
							API.sendRequest('/api/region/list/', 'POST', {}, data).then(function(response) {
								
								var regionList = response.regions;
								
								var cur_region = null;
								for (var region of regionList) {
									if (region.name == $scope.region_name || region.locale == $scope.region_name) {
										
										cur_region = region;
										
										$scope.region_name = region.name;
										break;
									}
								}
								
								/* City */
								
								if (cur_region) {
									
									var data = {'country_id':cur_country.id, 'region_id':cur_region.id};
									API.sendRequest('/api/city/list/', 'POST', {}, data).then(function(response) {
										
										var cityList = response.cities;
										
										var cur_city = null;
										for (var city of cityList) {
											if (city.name == $scope.city_name || city.locale == $scope.city_name) {
												
												cur_city = city;
												
												$scope.city_name = city.name;
											}
										}
									});
								}
							});
						}
					});
					
					$scope.$applyAsync();
				}
			}
		});
	}
	
	/* Step #4 management */
	
	$scope.creating = false;
	
	$scope.createMosaic = function() {
		
		$scope.creating = true;
		
		var data = {
			'country': $scope.country_name,
			'region': $scope.region_name,
			'city': $scope.city_name,
			'columns': $scope.columns,
			'type': $scope.mosaic_type,
			'title': $scope.mosaic_name,
			'missions': $scope.selected,
		};
		API.sendRequest('/api/mosaic/create/', 'POST', {}, data).then(function(response) {

			$scope.missions = [];
			$scope.selected = [];
			
			$scope.searchText = '';
			
			$scope.columns = '6';
			
			$scope.offset = [];
			
			$scope.mission_selected = null;
			
			$scope.mosaic_name = '';
			$scope.mosaic_type = 'sequence';
			
			$scope.city_name = '';
			$scope.region_name = '';
			$scope.country_name = '';
		
			$window.open('https://www.myingressmosaics.com/mosaic/' + response);
			
			$scope.open_step(1);
			
			$scope.creating = false;
		});
	}
	
	/* Page loading */

	$scope.open_step(1);
	
	$scope.loaded = true;
});