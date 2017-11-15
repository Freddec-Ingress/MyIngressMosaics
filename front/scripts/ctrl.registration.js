angular.module('FrontModule.controllers').controller('RegistrationCtrl', function($scope, $window, API, UtilsService) {
	
	/* Page loaded */
	
	$scope.$on('user-loaded', function(event, args) {
		
		$('#page-loading').addClass('hidden');
		$('#page-content').removeClass('hidden');
		
		$scope.refreshMissions();
	});
	
	/* Advanced mode */
	
	$scope.mode_advanced = false;
	
	$scope.toggleAdvancedMode = function() {
		
		$scope.mode_advanced = !$scope.mode_advanced;
		
		if (!$scope.mode_advanced) $scope.refreshMissions();
		if ($scope.mode_advanced) $scope.refreshPotentials();
	}

	/* Missions management */

	$scope.missions = [];
	$scope.filteredMissions = [];
	
	$scope.filterText = '';
		
	$scope.refreshingMissions = false;
	
	$scope.refreshMissions = function() {
	
		$scope.missions = [];
		$scope.filteredMissions = [];
		
		$scope.filterText = '';
		
		$scope.refreshingMissions = true;
		
		API.sendRequest('/api/missions/', 'POST').then(function(response) {
			
			$scope.missions = response.missions;
			if (!$scope.missions) $scope.missions = [];
			else {
				
				for (var mitem of $scope.mosaicModel.missions) {
				
					var index = -1;
					
					var temp = -1;
					for (var item of $scope.missions) {
			
						temp += 1;
						
						if (item.ref == mitem.ref) {
							
							index = temp;
							break;
						}
					}
					
					if (index != -1) $scope.missions.splice(index, 1);
				}
				
				$scope.missions.sort(UtilsService.sortMissionsByCreatorTitleAsc);
			}
			
			$scope.filterMissions('');

			$scope.refreshingMissions = false;
		});
	}

	$scope.filterMissions = function(text) {
		
		$scope.filteredMissions = [];
		
		$scope.filterText = text;
		
		if (!$scope.filterText) $scope.filteredMissions = $scope.missions.slice();
		else  {
			
			for (var item of $scope.missions) {
				
				if (item.title.indexOf(text) != -1 || item.creator.indexOf(text) != -1) {
					$scope.filteredMissions.push(item);
				}
			}
		}
	}
	
	$scope.addAllMissions = function() {
		
		var missions = $scope.filteredMissions.slice();
		for (var item of missions) {
			$scope.addMissionToModel(item);
		}
	}
	
	$scope.addMissionToModel = function(item) {
		
		$scope.mosaicModel.missions.push(item);
		computeOffset();
		
		$scope.filteredMissions.splice($scope.filteredMissions.indexOf(item), 1);
		
		if (!$scope.mosaicModel.title) {
			
			var mosaic_name = item.title;
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
			
			$scope.mosaicModel.title = mosaic_name;
		}
		
		if (!$scope.mosaicModel.country && !$scope.mosaicModel.region && !$scope.mosaicModel.city)  {
			
			var geocoder = new google.maps.Geocoder;
			
			var latlng = {
				lat: parseFloat($scope.mosaicModel.missions[0].startLat),
				lng: parseFloat($scope.mosaicModel.missions[0].startLng),
			};
			
			$scope.countries = [];
			$scope.regions = [];
			$scope.cities = [];

			geocoder.geocode({'location': latlng}, function(results, status) {
				
				if (status === 'OK') {
					
					var components = null;
					if (results[0]) components = results[0].address_components;
					if (results[1]) components = results[1].address_components;
					
					if (components) {
						
						var admin2 = null;
						var admin3 = null;
						
						for (var item of components) {
							
							if (item.types[0] == 'country') $scope.mosaicModel.country = item.long_name;
							if (item.types[0] == 'locality') $scope.mosaicModel.city = item.long_name;
							if (item.types[0] == 'administrative_area_level_1') $scope.mosaicModel.region = item.long_name;
							if (item.types[0] == 'administrative_area_level_2') admin2 = item.long_name;
							if (item.types[0] == 'administrative_area_level_3') admin3 = item.long_name;
						}
						
						if (!$scope.mosaicModel.city && admin2) $scope.mosaicModel.city = item.admin2;
						if (!$scope.mosaicModel.city && admin3) $scope.mosaicModel.city = item.admin3;
						
						UtilsService.checkMosaicLocations($scope.mosaicModel);
						
						/* Country */
						
						API.sendRequest('/api/country/list/', 'POST').then(function(response) {
							
							var countryList = response.countries;

							var cur_country = null;
							for (var country of countryList) {
								if (country.name == $scope.mosaicModel.country || country.locale == $scope.mosaicModel.country) {
									
									cur_country = country;
									
									$scope.mosaicModel.country = country.name;
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
										if (region.name == $scope.mosaicModel.region || region.locale == $scope.mosaicModel.region) {
											
											cur_region = region;
											
											$scope.mosaicModel.region = region.name;
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
												if (city.name == $scope.mosaicModel.city || city.locale == $scope.mosaicModel.city) {
													
													cur_city = city;
													
													$scope.mosaicModel.city = city.name;
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
		
		var order = item.order;
		if (!item.order || item.order < 1) order = UtilsService.getOrderFromMissionName(item.title);
		item.order = order.toString();
		
		$scope.mosaicModel.missions.sort(UtilsService.sortMissionsByOrderTitleAsc);
	}
	
	$scope.deleteAllMissions = function() {
		
		var missions = $scope.filteredMissions.slice();
		for (var item of missions) {
			$scope.deleteMission(item);
		}
	}
	
	$scope.deleteMission = function(item) {
		
		$scope.filteredMissions.splice($scope.filteredMissions.indexOf(item), 1);
		
		var data = {'ref':item.ref};
		API.sendRequest('/api/mission/exclude/', 'POST', {}, data);
	}

	/* Mosaic model management */

	$scope.mosaicModel = {
		
		'city': null,
		'type': 'sequence',
		'title': null,
		'region': null,
		'columns': '6',
		'country': null,
		'missions': [],
		'creating': false,
		'offset': 0,
	}

	function computeOffset() {
		
		$scope.mosaicModel.offset = $scope.mosaicModel.missions.length % 6;
		console.log($scope.mosaicModel.offset);
		if ($scope.mosaicModel.offset < 0 || $scope.mosaicModel.offset > 5) $scope.mosaicModel.offset = 0;
	}

	$scope.clearAll = function() {
		
		var missions = $scope.mosaicModel.missions.slice();
		for (var m of missions) {
			$scope.removeMission(m);
		}
		
		$window.scrollTo(0, 0);
	}
	
	$scope.removeMission = function(item) {
		
		$scope.mosaicModel.missions.splice($scope.mosaicModel.missions.indexOf(item), 1);
		computeOffset();

		if ($scope.mosaicModel.missions.length < 1) {
			
			$scope.mosaicModel.city = null;
			$scope.mosaicModel.type = 'sequence';
			$scope.mosaicModel.title = null;
			$scope.mosaicModel.region = null;
			$scope.mosaicModel.columns = '6';
			$scope.mosaicModel.country = null;
		}
		else {
		
			$scope.mosaicModel.missions.sort(UtilsService.sortMissionsByOrderTitleAsc);
		}
		
		if (!$scope.filterText || item.title.indexOf($scope.filterText) != -1 || item.creator.indexOf($scope.filterText) != -1) {
			
			$scope.filteredMissions.push(item);
			$scope.filteredMissions.sort(UtilsService.sortMissionsByCreatorTitleAsc);
		}
	}
	
	$scope.reorder = function() {
		
		$scope.mosaicModel.missions.sort(UtilsService.sortMissionsByOrderTitleAsc);
	}

	$scope.addFake = function(fakeorder) {
		
		var item = {
			'ref': 'Unavailable',
			'order': fakeorder,
			'title': 'Fake mission',
		}
		
		$scope.addMissionToModel(item);
	}
	
	$scope.createMosaic = function() {

		$('#createButton').text('');
		$scope.creating = true;

		API.sendRequest('/api/mosaic/create/', 'POST', {}, $scope.mosaicModel).then(function(response) {

			var missions = $scope.mosaicModel.missions.slice();
			for (var m of missions) {
				$scope.mosaicModel.missions.splice($scope.mosaicModel.missions.indexOf(m), 1);
			}
			
			$scope.mosaicModel.city = null;
			$scope.mosaicModel.type = 'sequence';
			$scope.mosaicModel.title = null;
			$scope.mosaicModel.region = null;
			$scope.mosaicModel.columns = '6';
			$scope.mosaicModel.country = null;
		
			$window.open('https://www.myingressmosaics.com/mosaic/' + response);
			
			$('#createButton').text('Create');
			$scope.creating = false;
	
			$window.scrollTo(0, 0);
		});
	}
	
	/* Potentials management */
	
	$scope.potentials = [];
	
	$scope.refreshingPotentials = false;
	
	$scope.refreshPotentials = function() {
		
		$scope.potentials = [];
		
		$scope.refreshingPotentials = true;
		
		API.sendRequest('/api/potentials/', 'POST').then(function(response) {
			
			if (response) {
				for (var item of response) {
					
					var obj = {
						'city': null,
						'open': false,
						'type': 'sequence',
						'title': item.name,
						'count': item.count,
						'region': null,
						'columns': '6',
						'loading': false,
						'creating': false,
						'country': null,
						'missions': [],
					};
					
					$scope.potentials.push(obj);
				}
			}
			
			$scope.refreshingPotentials = false;
		});
	}
	
	$scope.togglePotential = function(potential) {
		
		potential.open = !potential.open;
		
		if (potential.open) {
			
			if (potential.missions.length < 1) $scope.refreshPotential(potential);
		}
	}
	
	$scope.refreshPotential = function(potential) {
		
		potential.missions = [];
		potential.loading = true;
		
		var data = {'name':potential.title};
		API.sendRequest('/api/potential/name/', 'POST', {}, data).then(function(response) {
			
			if (response) {
				
				potential.missions = response;
				
				var geocoder = new google.maps.Geocoder;
				
				var latlng = {
					lat: parseFloat(potential.missions[0].startLat),
					lng: parseFloat(potential.missions[0].startLng),
				};
				
				geocoder.geocode({'location': latlng}, function(results, status) {
					
					if (status === 'OK') {
						
						var components = null;
						if (results[0]) components = results[0].address_components;
						if (results[1]) components = results[1].address_components;
						
						if (components) {
							
							var admin2 = null;
							var admin3 = null;
							
							for (var item of components) {
								
								if (item.types[0] == 'country') potential.country = item.long_name;
								if (item.types[0] == 'locality') potential.city = item.long_name;
								if (item.types[0] == 'administrative_area_level_1') potential.region = item.long_name;
								if (item.types[0] == 'administrative_area_level_2') admin2 = item.long_name;
								if (item.types[0] == 'administrative_area_level_3') admin3 = item.long_name;
							}
							
							if (!potential.city && admin2) potential.city = item.admin2;
							if (!potential.city && admin3) potential.city = item.admin3;
							
							UtilsService.checkMosaicLocations(potential);
						
							/* Country */
							
							API.sendRequest('/api/country/list/', 'POST').then(function(response) {
								
								var countryList = response.countries;
							
								var cur_country = null;
								for (var country of countryList) {
									if (country.name == potential.country || country.locale == potential.country) {
										
										cur_country = country;
										
										potential.country = country.name;
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
											if (region.name == potential.region || region.locale == potential.region) {
												
												cur_region = region;
												
												potential.region = region.name;
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
													if (city.name == potential.city || city.locale == potential.city) {
														
														cur_city = city;
														
														potential.city = city.name;
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
				
				for (var item of potential.missions) {
					
					var order = item.order;
					if (!item.order || item.order < 1) order = UtilsService.getOrderFromMissionName(item.title);
					item.order = order.toString();
				}
				
				potential.missions.sort(UtilsService.sortMissionsByOrderTitleAsc);
			}
			
			potential.loading = false;
		});
	}
	
	$scope.removeMissionFromPotential = function(potential, item) {
		
		potential.missions.splice(potential.missions.indexOf(item), 1);
		
		if (potential.missions.length < 1) {
			
			potential.city = null;
			potential.type = 'sequence';
			potential.title = null;
			potential.region = null;
			potential.columns = '6';
			potential.country = null;
		}
		else {
		
			potential.missions.sort(compareOrderAsc);
		}
	}
	
	$scope.reorderPotential = function(potential) {
		
		potential.missions.sort(compareOrderAsc);
	}
	
	$scope.addPotentialFake = function(potential, fakeorder) {
		
		var item = {
			'ref': 'Unavailable',
			'order': fakeorder,
			'title': 'Fake mission',
		}
		
		potential.missions.push(item);
		
		potential.missions.sort(compareOrderAsc);
	}
	
	$scope.createPotential = function(potential) {

		potential.creating = true;

		API.sendRequest('/api/mosaic/create/', 'POST', {}, potential).then(function(response) {

			$scope.potentials.splice($scope.potentials.indexOf(potential), 1);

			$window.open('https://www.myingressmosaics.com/mosaic/' + response);
		});
	}
	
	$scope.isCountValid = function(count) {
		
		var remainder = (count/6) % 1;
		if (remainder > 0) return true;
		return false;
	}
});
