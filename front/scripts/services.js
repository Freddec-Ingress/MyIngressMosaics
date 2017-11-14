angular.module('FrontModule.services', [])

angular.module('FrontModule.services').service('API', function($q, $http, $cookies) {
	
	var service = {
		
		sendRequest: function(url, method, params, data) {
			
			if ($cookies.token) { $http.defaults.headers.common.Authorization = 'Token ' + $cookies.token; }
			
			var deferred = $q.defer();
			
			$http({url: url, withCredentials: false, method: method, headers: {'X-CSRFToken': $cookies['csrftoken']}, params: params, data: data})
				.then(function successCallback(response) {
					
					deferred.resolve(response.data, response.status);
				}
				, function errorCallback(response) {

					if (response.status == 0) {
						
						if (response.data == '') response.data = 'error_TIMEOUT';
						if (response.data == null) response.data = 'error_NOCONNECTION';
					}

					deferred.reject(response.data, response.status, response.headers, response.config);
				});
			
			return deferred.promise;
		},
	};
	
	return service;
});

angular.module('FrontModule.services').service('UtilsService', function() {
	
	var service = {
		
		getOrderFromMissionName: function(name) {
			
			var order = 0;
			
			var found = name.match(/[0-9]+/);
			if (found) { order = parseInt(found[0]); }
			else {
			
				found = name.match(/(０|１|２|３|４|５|６|７|８|９)+/);
				if (found) {
					
					var arrayCharracter = ['３９','３８','３７','３６','３５','３４','３３','３２','３１','３０',
										   '２９','２８','２７','２６','２５','２４','２３','２２','２１','２０',
										   '１９','１８','１７','１６','１５','１４','１３','１２','１１','１０',
											 '９',  '８',  '７',  '６',  '５',  '４',  '３',  '２',  '１',  '０']
											 
					var arrayInteger = [39,38,37,36,35,34,33,32,31,30,
										29,28,27,26,25,24,23,22,21,20,
										19,18,17,16,15,14,13,12,11,10,
					                     9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
					
					for (var i in arrayCharracter) {
						
						found = name.match(arrayCharracter[i]);
						if (found) {
							order = arrayInteger[i];
							break;
						}
					}
				}
				else {
					
					found = name.match(/(①|②|③|④|⑤|⑥|⑦|⑧|⑨|⑩|⑪|⑫|⑬|⑭|⑮|⑯|⑰|⑱|⑲|⑳|㉑|㉒|㉓|㉔)+/);
					if (found) {
						
						if (found[0] == '①') order = 1;
						if (found[0] == '②') order = 2;
						if (found[0] == '③') order = 3;
						if (found[0] == '④') order = 4;
 						if (found[0] == '⑤') order = 5;
						if (found[0] == '⑥') order = 6;
						if (found[0] == '⑦') order = 7;
						if (found[0] == '⑧') order = 8;
						if (found[0] == '⑨') order = 9;
						if (found[0] == '⑩') order = 10;
						if (found[0] == '⑪') order = 11;
						if (found[0] == '⑫') order = 12;
						if (found[0] == '⑬') order = 13;
						if (found[0] == '⑭') order = 14;
						if (found[0] == '⑮') order = 15;
						if (found[0] == '⑯') order = 16;
						if (found[0] == '⑰') order = 17;
						if (found[0] == '⑱') order = 18;
						if (found[0] == '⑲') order = 19;
						if (found[0] == '⑳') order = 20;
						if (found[0] == '㉑') order = 21;
						if (found[0] == '㉒') order = 22;
						if (found[0] == '㉓') order = 23;
						if (found[0] == '㉔') order = 24;
					}
					else {
						
						found = name.match(/(一|壱|二|弐|三|参|四|五|伍|六|七|八|九|十|拾|十一|拾壱|十二|拾弐)+/);
						if (found) {
							
							switch(found) {
								
								case '一': order = 1; break;
								case '壱': order = 1; break;
								case '二': order = 2; break;
								case '弐': order = 2; break;
								case '三': order = 3; break;
								case '参': order = 3; break;
								case '四': order = 4; break;
								case '五': order = 5; break;
		 						case '伍': order = 5; break;
								case '六': order = 6; break;
								case '七': order = 7; break;
								case '八': order = 8; break;
								case '九': order = 9; break;
								case '十': order = 10; break;
								case '拾': order = 10; break;
								case '十一': order = 11; break;
								case '拾壱': order = 11; break;
								case '十二': order = 12; break;
								case '拾弐': order = 12; break;
							}
						}
						else {
							
							found = name.match(/(い|ろ|は|に|ほ|へ|と|ち|り|ぬ|る|を)+/);
							if (found) {
								
								if (found[0] == 'い') order = 1;
								if (found[0] == 'ろ') order = 2;
								if (found[0] == 'は') order = 3;
								if (found[0] == 'に') order = 4;
		 						if (found[0] == 'ほ') order = 5;
								if (found[0] == 'へ') order = 6;
								if (found[0] == 'と') order = 7;
								if (found[0] == 'ち') order = 8;
								if (found[0] == 'り') order = 9;
								if (found[0] == 'ぬ') order = 10;
								if (found[0] == 'る') order = 11;
								if (found[0] == 'を') order = 12;
							}
							else {
								
								found = name.match(/( I| II | III| IV| V| VI| VII| VIII| IX| X| XI| XII| XIV| XV| XVI| XVII| XVIII| XIX| XX| XXI| XXII| XXIV| XXV| XXVI| XXVII| XXVIII| XXIX| XXX| XXXI| XXXII| XXXIV| XXXV| XXXVI| XXXVII| XXXVIII| XXXIX| XL| XLI| XLII| XLIV| XLV| XLVI| XLVII| XLVIII| XLIX)+/);
								if (found) {
									
									if (found[0] == ' I')		order =  1;
									if (found[0] == ' II')		order =  2;
									if (found[0] == ' III') 	order =  3;
									if (found[0] == ' IV')		order =  4;
			 						if (found[0] == ' V')		order =  5;
									if (found[0] == ' VI')		order =  6;
									if (found[0] == ' VII') 	order =  7;
									if (found[0] == ' VIII')	order =  8;
									if (found[0] == ' IX')		order =  9;
									if (found[0] == ' X')		order = 10;
									if (found[0] == ' XI')		order = 11;
									if (found[0] == ' XII')		order = 12;
									if (found[0] == ' XIII') 	order = 13;
									if (found[0] == ' XIV')		order = 14;
			 						if (found[0] == ' XV')		order = 15;
									if (found[0] == ' XVI')		order = 16;
									if (found[0] == ' XVII') 	order = 17;
									if (found[0] == ' XVIII')	order = 18;
									if (found[0] == ' XIX')		order = 19;
									if (found[0] == ' XX')		order = 20;
									if (found[0] == ' XXI')		order = 21;
									if (found[0] == ' XXII')	order = 22;
									if (found[0] == ' XXIII') 	order = 23;
									if (found[0] == ' XXIV')	order = 24;
			 						if (found[0] == ' XXV')		order = 25;
									if (found[0] == ' XXVI')	order = 26;
									if (found[0] == ' XXVII') 	order = 27;
									if (found[0] == ' XXVIII')	order = 28;
									if (found[0] == ' XXIX')	order = 29;
									if (found[0] == ' XXX')		order = 30;
									if (found[0] == ' XXXI')	order = 31;
									if (found[0] == ' XXXII')	order = 32;
									if (found[0] == ' XXXIII') 	order = 33;
									if (found[0] == ' XXXIV')	order = 34;
			 						if (found[0] == ' XXXV')	order = 35;
									if (found[0] == ' XXXVI')	order = 36;
									if (found[0] == ' XXXVII') 	order = 37;
									if (found[0] == ' XXXVIII')	order = 38;
									if (found[0] == ' XXXIX')	order = 39;
									if (found[0] == ' XL')		order = 40;
									if (found[0] == ' XLI')		order = 41;
									if (found[0] == ' XLII')	order = 42;
									if (found[0] == ' XLIII') 	order = 43;
									if (found[0] == ' XLIV')	order = 44;
			 						if (found[0] == ' XLV')		order = 45;
									if (found[0] == ' XLVI')	order = 46;
									if (found[0] == ' XLVII') 	order = 47;
									if (found[0] == ' XLVIII')	order = 48;
									if (found[0] == ' XLIX')	order = 49;
								}
							}
						}
					}
				}
			}
			
			return order;
		},
		
		checkMosaicLocations: function(mosaic) {
			
			if (mosaic.country == 'Japan') {
				
				if (mosaic.region) mosaic.region = mosaic.region.replace(/ō/g, 'o');
				if (mosaic.region) mosaic.region = mosaic.region.replace(/Ō/g, 'O');
				if (mosaic.region) mosaic.region = mosaic.region.replace(' Prefecture', '');
				if (mosaic.region && mosaic.region.substring(mosaic.region.length-3, mosaic.region.length) == '-to') mosaic.region = mosaic.region.substring(0, mosaic.region.length-3);
				if (mosaic.region && mosaic.region.substring(mosaic.region.length-3, mosaic.region.length) == '-fu') mosaic.region = mosaic.region.substring(0, mosaic.region.length-3);
				if (mosaic.region && mosaic.region.substring(mosaic.region.length-4, mosaic.region.length) == '-ken') mosaic.region = mosaic.region.substring(0, mosaic.region.length-4);
				
				if (mosaic.city) mosaic.city = mosaic.city.replace(/ō/g, 'o');
				if (mosaic.city) mosaic.city = mosaic.city.replace(/Ō/g, 'O');
				if (mosaic.city && mosaic.city.substring(mosaic.city.length-3, mosaic.city.length) == '-ku') mosaic.city = mosaic.city.substring(0, mosaic.city.length-3);
				if (mosaic.city && mosaic.city.substring(mosaic.city.length-4, mosaic.city.length) == '-son') mosaic.city = mosaic.city.substring(0, mosaic.city.length-4);
				if (mosaic.city && mosaic.city.substring(mosaic.city.length-4, mosaic.city.length) == '-shi') mosaic.city = mosaic.city.substring(0, mosaic.city.length-4);
				if (mosaic.city && mosaic.city.substring(mosaic.city.length-4, mosaic.city.length) == '-cho') mosaic.city = mosaic.city.substring(0, mosaic.city.length-4);
				if (mosaic.city && mosaic.city.substring(mosaic.city.length-5, mosaic.city.length) == '-mura') mosaic.city = mosaic.city.substring(0, mosaic.city.length-5);
				if (mosaic.city && mosaic.city.substring(mosaic.city.length-6, mosaic.city.length) == '-machi') mosaic.city = mosaic.city.substring(0, mosaic.city.length-6);
			}
		},
	}
	
	return service;
});
