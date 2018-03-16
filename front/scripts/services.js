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
		
		sortMissionsByTitleAsc: function(a, b) {
			
			if (a.title < b.title)
				return -1;
				
			if (a.title > b.title)
				return 1;
			
			return 0;
		},

		sortMissionsByCreatorTitleAsc: function(a, b) {
			
			if (a.creator < b.creator)
				return -1;
				
			if (a.creator > b.creator)
				return 1;
			
			if (a.title < b.title)
				return -1;
				
			if (a.title > b.title)
				return 1;
			
			return 0;
		},

		sortMissionsByOrderTitleAsc: function(a, b) {
			
			if (parseInt(a.order) < parseInt(b.order))
				return -1;
				
			if (parseInt(a.order) > parseInt(b.order))
				return 1;
			
			if (a.title < b.title)
				return -1;
				
			if (a.title > b.title)
				return 1;
				
			return 0;
		},
	
		getOrderFromMissionName: function(name) {
			
			var order = 0;
			
			if (!name) return order;
			
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
								
								found = name.substr(name.lastIndexOf(' ') + 1);
								if (found) {
									
									if (found == 'I')		order =  1;
									if (found == 'II')		order =  2;
									if (found == 'III') 	order =  3;
									if (found == 'IV')		order =  4;
			 						if (found == 'V')		order =  5;
									if (found == 'VI')		order =  6;
									if (found == 'VII') 	order =  7;
									if (found == 'VIII')	order =  8;
									if (found == 'IX')		order =  9;
									if (found == 'X')		order = 10;
									if (found == 'XI')		order = 11;
									if (found == 'XII')	order = 12;
									if (found == 'XIII') 	order = 13;
									if (found == 'XIV')	order = 14;
			 						if (found == 'XV')		order = 15;
									if (found == 'XVI')	order = 16;
									if (found == 'XVII') 	order = 17;
									if (found == 'XVIII')	order = 18;
									if (found == 'XIX')	order = 19;
									if (found == 'XX')		order = 20;
									if (found == 'XXI')	order = 21;
									if (found == 'XXII')	order = 22;
									if (found == 'XXIII') 	order = 23;
									if (found == 'XXIV')	order = 24;
			 						if (found == 'XXV')	order = 25;
									if (found == 'XXVI')	order = 26;
									if (found == 'XXVII') 	order = 27;
									if (found == 'XXVIII')	order = 28;
									if (found == 'XXIX')	order = 29;
									if (found == 'XXX')	order = 30;
									if (found == 'XXXI')	order = 31;
									if (found == 'XXXII')	order = 32;
									if (found == 'XXXIII') order = 33;
									if (found == 'XXXIV')	order = 34;
			 						if (found == 'XXXV')	order = 35;
									if (found == 'XXXVI')	order = 36;
									if (found == 'XXXVII') order = 37;
									if (found == 'XXXVIII')order = 38;
									if (found == 'XXXIX')	order = 39;
									if (found == 'XL')		order = 40;
									if (found == 'XLI')	order = 41;
									if (found == 'XLII')	order = 42;
									if (found == 'XLIII') 	order = 43;
									if (found == 'XLIV')	order = 44;
			 						if (found == 'XLV')	order = 45;
									if (found == 'XLVI')	order = 46;
									if (found == 'XLVII') 	order = 47;
									if (found == 'XLVIII')	order = 48;
									if (found == 'XLIX')	order = 49;
									if (found == 'L')		order = 50;
									if (found == 'LI')	order = 51;
									if (found == 'LII')	order = 52;
									if (found == 'LIII') 	order = 53;
									if (found == 'LIV')	order = 54;
			 						if (found == 'LV')	order = 55;
									if (found == 'LVI')	order = 56;
									if (found == 'LVII') 	order = 57;
									if (found == 'LVIII')	order = 58;
									if (found == 'LIX')	order = 59;
									if (found == 'LX')	order = 60;
									if (found == 'LXI')		order = 61;
									if (found == 'LXII')		order = 62;
									if (found == 'LXIII') 	order = 63;
									if (found == 'LXIV')		order = 64;
			 						if (found == 'LXV')		order = 65;
									if (found == 'LXVI')		order = 66;
									if (found == 'LXVII') 	order = 67;
									if (found == 'LXVIII')	order = 68;
									if (found == 'LXIX')		order = 69;
									if (found == 'LXX')		order = 70;
									if (found == 'LXXI')		order = 71;
									if (found == 'LXXII')	order = 72;
									if (found == 'LXXIII') 	order = 73;
									if (found == 'LXXIV')	order = 74;
			 						if (found == 'LXXV')		order = 75;
									if (found == 'LXXVI')	order = 76;
									if (found == 'LXXVII') 	order = 77;
									if (found == 'LXXVIII')	order = 78;
									if (found == 'LXXIX')	order = 79;
									if (found == 'LXXX')		order = 80;
									if (found == 'LXXXI')	order = 81;
									if (found == 'LXXXII')	order = 82;
									if (found == 'LXXXIII') 	order = 83;
									if (found == 'LXXXIV')	order = 84;
			 						if (found == 'LXXXV')	order = 85;
									if (found == 'LXXXVI')	order = 86;
									if (found == 'LXXXVII') 	order = 87;
									if (found == 'LXXXVIII')	order = 88;
									if (found == 'LXXXIX')	order = 89;
									if (found == 'XC')		order = 90;
									if (found == 'XCI')		order = 91;
									if (found == 'XCII')	order = 92;
									if (found == 'XCIII') 	order = 93;
									if (found == 'XCIV')	order = 94;
			 						if (found == 'XCV')		order = 95;
									if (found == 'XCVI')	order = 96;
									if (found == 'XCVII') 	order = 97;
									if (found == 'XCVIII')	order = 98;
									if (found == 'XCIX')	order = 99;
									if (found == 'C')		order = 100;
									if (found == 'CI')		order = 101;
									if (found == 'CII')		order = 102;
									if (found == 'CIII') 	order = 103;
									if (found == 'CIV')		order = 104;
			 						if (found == 'CV')		order = 105;
									if (found == 'CVI')		order = 106;
									if (found == 'CVII') 	order = 107;
									if (found == 'CVIII')	order = 108;
									if (found == 'CIX')		order = 109;
									if (found == 'CX')		order = 110;
									if (found == 'CXI')		order = 111;
									if (found == 'CXII')	order = 112;
									if (found == 'CXIII') 	order = 113;
									if (found == 'CXIV')	order = 114;
			 						if (found == 'CXV')		order = 115;
									if (found == 'CXVI')	order = 116;
									if (found == 'CXVII') 	order = 117;
									if (found == 'CXVIII')	order = 118;
									if (found == 'CXIX')	order = 119;
									if (found == 'CXX')		order = 120;
									if (found == 'CXXI')	order = 121;
									if (found == 'CXXII')	order = 122;
									if (found == 'CXXIII') 	order = 123;
									if (found == 'CXXIV')	order = 124;
			 						if (found == 'CXXV')	order = 125;
									if (found == 'CXXVI')	order = 126;
									if (found == 'CXXVII') 	order = 127;
									if (found == 'CXXVIII')	order = 128;
									if (found == 'CXXIX')	order = 129;
									if (found == 'CXXX')	order = 130;
									if (found == 'CXXXI')	order = 131;
									if (found == 'CXXXII')	order = 132;
									if (found == 'CXXXIII') order = 133;
									if (found == 'CXXXIV')	order = 134;
			 						if (found == 'CXXXV')	order = 135;
									if (found == 'CXXXVI')	order = 136;
									if (found == 'CXXXVII') order = 137;
									if (found == 'CXXXVIII')order = 138;
									if (found == 'CXXXIX')	order = 139;
									if (found == 'CXL')		order = 140;
									if (found == 'CXLI')	order = 141;
									if (found == 'CXLII')	order = 142;
									if (found == 'CXLIII') 	order = 143;
									if (found == 'CXLIV')	order = 144;
			 						if (found == 'CXLV')	order = 145;
									if (found == 'CXLVI')	order = 146;
									if (found == 'CXLVII') 	order = 147;
									if (found == 'CXLVIII')	order = 148;
									if (found == 'CXLIX')	order = 149;
									if (found == 'CL')		order = 150;
									if (found == 'CLI')	order = 151;
									if (found == 'CLII')	order = 152;
									if (found == 'CLIII') 	order = 153;
									if (found == 'CLIV')	order = 154;
			 						if (found == 'CLV')	order = 155;
									if (found == 'CLVI')	order = 156;
									if (found == 'CLVII') 	order = 157;
									if (found == 'CLVIII')	order = 158;
									if (found == 'CLIX')	order = 159;
									if (found == 'CLX')	order = 160;
									if (found == 'CLXI')		order = 161;
									if (found == 'CLXII')		order = 162;
									if (found == 'CLXIII') 	order = 163;
									if (found == 'CLXIV')		order = 164;
			 						if (found == 'CLXV')		order = 165;
									if (found == 'CLXVI')		order = 166;
									if (found == 'CLXVII') 	order = 167;
									if (found == 'CLXVIII')	order = 168;
									if (found == 'CLXIX')		order = 169;
									if (found == 'CLXX')		order = 170;
									if (found == 'CLXXI')		order = 171;
									if (found == 'CLXXII')	order = 172;
									if (found == 'CLXXIII') 	order = 173;
									if (found == 'CLXXIV')	order = 174;
			 						if (found == 'CLXXV')		order = 175;
									if (found == 'CLXXVI')	order = 176;
									if (found == 'CLXXVII') 	order = 177;
									if (found == 'CLXXVIII')	order = 178;
									if (found == 'CLXXIX')	order = 179;
									if (found == 'CLXXX')		order = 180;
									if (found == 'CLXXXI')	order = 181;
									if (found == 'CLXXXII')	order = 182;
									if (found == 'CLXXXIII') 	order = 183;
									if (found == 'CLXXXIV')	order = 184;
			 						if (found == 'CLXXXV')	order = 185;
									if (found == 'CLXXXVI')	order = 186;
									if (found == 'CLXXXVII') 	order = 187;
									if (found == 'CLXXXVIII')	order = 188;
									if (found == 'CLXXXIX')	order = 189;
									if (found == 'CXC')		order = 190;
									if (found == 'CXCI')		order = 191;
									if (found == 'CXCII')	order = 192;
									if (found == 'CXCIII') 	order = 193;
									if (found == 'CXCIV')	order = 194;
			 						if (found == 'CXCV')		order = 195;
									if (found == 'CXCVI')	order = 196;
									if (found == 'CXCVII') 	order = 197;
									if (found == 'CXCVIII')	order = 198;
									if (found == 'CXCIX')	order = 199;
									if (found == 'CC')		order = 200;
									if (found == 'CCI')		order = 201;
									if (found == 'CCII')		order = 202;
									if (found == 'CCIII') 	order = 203;
									if (found == 'CCIV')		order = 204;
			 						if (found == 'CCV')		order = 205;
									if (found == 'CCVI')		order = 206;
									if (found == 'CCVII') 	order = 207;
									if (found == 'CCVIII')	order = 208;
									if (found == 'CCIX')		order = 209;
									if (found == 'CCX')		order = 210;
									if (found == 'CCXI')		order = 211;
									if (found == 'CCXII')	order = 212;
									if (found == 'CCXIII') 	order = 213;
									if (found == 'CCXIV')	order = 214;
			 						if (found == 'CCXV')		order = 215;
									if (found == 'CCXVI')	order = 216;
									if (found == 'CCXVII') 	order = 217;
									if (found == 'CCXVIII')	order = 218;
									if (found == 'CCXIX')	order = 219;
									if (found == 'CCXX')		order = 220;
									if (found == 'CCXXI')	order = 221;
									if (found == 'CCXXII')	order = 222;
									if (found == 'CCXXIII') 	order = 223;
									if (found == 'CCXXIV')	order = 224;
			 						if (found == 'CCXXV')	order = 225;
									if (found == 'CCXXVI')	order = 226;
									if (found == 'CCXXVII') 	order = 227;
									if (found == 'CCXXVIII')	order = 228;
									if (found == 'CCXXIX')	order = 229;
									if (found == 'CCXXX')	order = 230;
									if (found == 'CCXXXI')	order = 231;
									if (found == 'CCXXXII')	order = 232;
									if (found == 'CCXXXIII') order = 233;
									if (found == 'CCXXXIV')	order = 234;
			 						if (found == 'CCXXXV')	order = 235;
									if (found == 'CCXXXVI')	order = 236;
									if (found == 'CCXXXVII') order = 237;
									if (found == 'CCXXXVIII')order = 238;
									if (found == 'CCXXXIX')	order = 239;
									if (found == 'CCXL')		order = 240;
									if (found == 'CCXLI')	order = 241;
									if (found == 'CCXLII')	order = 242;
									if (found == 'CCXLIII') 	order = 243;
									if (found == 'CCXLIV')	order = 244;
			 						if (found == 'CCXLV')	order = 245;
									if (found == 'CCXLVI')	order = 246;
									if (found == 'CCXLVII') 	order = 247;
									if (found == 'CCXLVIII')	order = 248;
									if (found == 'CCXLIX')	order = 249;
									if (found == 'CCL')		order = 250;
									if (found == 'CCLI')	order = 251;
									if (found == 'CCLII')	order = 252;
									if (found == 'CCLIII') 	order = 253;
									if (found == 'CCLIV')	order = 254;
			 						if (found == 'CCLV')	order = 255;
									if (found == 'CCLVI')	order = 256;
									if (found == 'CCLVII') 	order = 257;
									if (found == 'CCLVIII')	order = 258;
									if (found == 'CCLIX')	order = 259;
									if (found == 'CCLX')	order = 260;
									if (found == 'CCLXI')		order = 261;
									if (found == 'CCLXII')		order = 262;
									if (found == 'CCLXIII') 	order = 263;
									if (found == 'CCLXIV')		order = 264;
			 						if (found == 'CCLXV')		order = 265;
									if (found == 'CCLXVI')		order = 266;
									if (found == 'CCLXVII') 	order = 267;
									if (found == 'CCLXVIII')	order = 268;
									if (found == 'CCLXIX')		order = 269;
									if (found == 'CCLXX')		order = 270;
									if (found == 'CCLXXI')		order = 271;
									if (found == 'CCLXXII')	order = 272;
									if (found == 'CCLXXIII') 	order = 273;
									if (found == 'CCLXXIV')	order = 274;
			 						if (found == 'CCLXXV')		order = 275;
									if (found == 'CCLXXVI')	order = 276;
									if (found == 'CCLXXVII') 	order = 277;
									if (found == 'CCLXXVIII')	order = 278;
									if (found == 'CCLXXIX')	order = 279;
									if (found == 'CCLXXX')		order = 280;
									if (found == 'CCLXXXI')	order = 281;
									if (found == 'CCLXXXII')	order = 282;
									if (found == 'CCLXXXIII') 	order = 283;
									if (found == 'CCLXXXIV')	order = 284;
			 						if (found == 'CCLXXXV')	order = 285;
									if (found == 'CCLXXXVI')	order = 286;
									if (found == 'CCLXXXVII') 	order = 287;
									if (found == 'CCLXXXVIII')	order = 288;
									if (found == 'CCLXXXIX')	order = 289;
									if (found == 'CCXC')		order = 290;
									if (found == 'CCXCI')		order = 291;
									if (found == 'CCXCII')	order = 292;
									if (found == 'CCXCIII') 	order = 293;
									if (found == 'CCXCIV')	order = 294;
			 						if (found == 'CCXCV')		order = 295;
									if (found == 'CCXCVI')	order = 296;
									if (found == 'CCXCVII') 	order = 297;
									if (found == 'CCXCVIII')	order = 298;
									if (found == 'CCXCIX')	order = 299;
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

angular.module('FrontModule.services').service('UserService', function(API, $auth, $http, $cookies, $window) {
	
	var service = {
		
		loadUser: function(user) {

			API.sendRequest('/api/user/', 'GET').then(function(response) {
				
				if (response) {
					
					user = {
						name: response.name,
						faction: response.faction,
						picture: response.picture,
						superuser: response.superuser,
						authenticated: $auth.isAuthenticated(),
					}
				}
				else {
					
					user = {
						name: null,
						faction: null,
						superuser: false,
						authenticated: false,
					}
				}

			}, function(response) {
				
				delete $http.defaults.headers.common.Authorization;
		    	delete $cookies.token;
				
				$auth.removeToken();
		
				API.sendRequest('/api/user/logout/', 'POST');
				
				user = {
					name: null,
					faction: null,
					superuser: false,
					authenticated: false,
				}
			});
		},
		
		signin: function(provider, next) {
				
			$auth.authenticate(provider).then(function(response) {
				
				$auth.setToken(response.data.token);
				$cookies.token = response.data.token;
				
				$window.location.href = next;
			});
		},
	}
	
	return service;
});