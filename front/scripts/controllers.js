angular.module('AngularApp.controllers', [])

angular.module('AngularApp.controllers').controller('RootCtrl', function($rootScope, $scope, $stateParams, $translate, $window, UserService) {
	
	var supported_lang = ['en', 'fr'];
	
	var user_lang = 'en';
	
	if ($stateParams.codelang) {
		
		if (supported_lang.indexOf($stateParams.codelang) != -1) user_lang = $stateParams.codelang;
      	$translate.use(user_lang);
	}
	else {
		
		var lang = $window.navigator.language || $window.navigator.userLanguage;
		if (supported_lang.indexOf(lang) != -1) user_lang = lang;
		
    	$window.location.href = '/' + user_lang + '/home';
	}
	
	$scope.user = UserService.data;
	
	$scope.logout = UserService.logout;
	
	$rootScope.menu_open = false;
	
	$scope.openMenu = function() {
		$rootScope.menu_open = true;
	}
	
	$scope.closeMenu = function() {
		$rootScope.menu_open = false;
	}
});

angular.module('AngularApp.controllers').controller('HomeCtrl', function($scope) {
	
	$scope.page_title = 'home_TITLE';
});

angular.module('AngularApp.controllers').controller('LoginCtrl', function($scope, UserService) {
	
	$scope.page_title = 'login_TITLE';
	
	$scope.loginModel = { username:null, password:null };
	
	$scope.localLogin = UserService.localLogin;
	$scope.socialLogin = UserService.socialLogin;
});

angular.module('AngularApp.controllers').controller('RegisterCtrl', function($scope, UserService) {
	
	$scope.page_title = 'register_TITLE';
	
	$scope.registerModel = { username:null, password1:null, password2:null, email:null };
	
	$scope.register = UserService.register;
});

angular.module('AngularApp.controllers').controller('ProfileCtrl', function($scope, UserService, $timeout) {
	
	$scope.page_title = 'profile_TITLE';
	
	$scope.user = UserService.data;
	
	/* Name */
	
	$scope.editname = false;
	$scope.newname = UserService.data.name;
	
	$scope.nameClick = function() {
		
		$scope.editname = true;
			
		$timeout(function() {
			$('#input-name').focus();
		});
	}
	
	$scope.nameBlur = function(newvalue) {
		
		$scope.editname = false;
		
		if (newvalue && newvalue != UserService.data.name) {
			
			$scope.loadingname = true;
			UserService.updateName(newvalue).then(function() {
				$scope.loadingname = false;
			});
		}
	}
});

angular.module('AngularApp.controllers').controller('MissionsCtrl', function($scope, $state, UserService, CreateService) {
	
	$scope.page_title = 'missions_TITLE';

	CreateService.init();
	
	$scope.missions = UserService.data.missions;
	
	$scope.isSelected = function(ref) {
		
		if (CreateService.getRefArray().indexOf(ref) != -1) {
			return true;
		} else {
			return false;
		}
	}
	
	$scope.toggle = function(index, event, item) {
		
		if (event.shiftKey) {
			event.preventDefault();
			
			if (index > $scope.lastSelectedIndex) {
				
				for (var i = ($scope.lastSelectedIndex + 1); i <= index; i++) {
					
					var m = $scope.missions[i];
					if (!$scope.isSelected(m.ref)) {
						CreateService.add(m);
					}
				}
			}
			else {
				
				for (var i = index; i < $scope.lastSelectedIndex; i++) {
					
					var m = $scope.missions[i];
					if (!$scope.isSelected(m.ref)) {
						CreateService.add(m);
					}
				}
			}
		}
		else {
			
			if ($scope.isSelected(item.ref)) {
				CreateService.remove(item);
			}
			else {
				CreateService.add(item);
			}
		}
		
		$scope.lastSelectedIndex = index;
	}
	
	$scope.hasSelected = function() {
		
		if (CreateService.data.missions.length > 0) {
			return true;
		} else {
			return false;
		}
	}
	
	$scope.nextStep = function() {
		$state.go('root.create');
	}
	
	$scope.delete = function(item) {
		UserService.deleteMission(item);
	}
});

angular.module('AngularApp.controllers').controller('CreateCtrl', function($scope, $state, CreateService) {
	
	$scope.page_title = 'create_TITLE';

	if (CreateService.data.missions.length < 1) {
		$state.go('root.missions');
	}

	CreateService.default();

	$scope.data = CreateService.data;
	$scope.create = CreateService.create;

	$scope.rows = function() {
		
		var temp = 1;
		if ($scope.data.count > 0 && $scope.data.cols > 0) temp = Math.ceil($scope.data.count / $scope.data.cols);
		if (!temp) temp = 1;
		
		var rows = [];
		for (var i = 0; i < temp; i++) {
			rows.push(i);
		}
		
		return rows;
	}
	
	$scope.cols = function() {
		
		var temp = 1;
		if ($scope.data.cols > 0) temp = $scope.data.cols;
		if (!temp) temp = 1;
		
		var cols = [];
		for (var i = 0; i < temp; i++) {
			cols.push(i);
		}
		
		return cols;
	}
	
	$scope.getImage = function(i, j) {
		
		var order = (i * $scope.data.cols + j) + 1;
		return CreateService.getImageByOrder(order);
	}
});

angular.module('AngularApp.controllers').controller('MosaicCtrl', function($scope, $timeout, MosaicService) {
	
	$scope.page_title = MosaicService.data.mosaic.title;
	
	$scope.mosaic = MosaicService.data.mosaic;

	$scope.rows = function() {
		
		var temp = 1;
		if ($scope.mosaic.count > 0 && $scope.mosaic.cols > 0) temp = Math.ceil($scope.mosaic.count / $scope.mosaic.cols);
		if (!temp) temp = 1;
		
		var rows = [];
		for (var i = 0; i < temp; i++) {
			rows.push(i);
		}
		
		return rows;
	}
	
	$scope.cols = function() {
		
		var temp = 1;
		if ($scope.mosaic.cols > 0) temp = $scope.mosaic.cols;
		if (!temp) temp = 1;
		
		var cols = [];
		for (var i = 0; i < temp; i++) {
			cols.push(i);
		}
		
		return cols;
	}
	
	$scope.getImage = function(i, j) {
		
		var order = (i * $scope.mosaic.cols + j) + 1;
		return MosaicService.getImageByOrder(order);
	}
	
	/* Name */
	
	$scope.editname = false;
	$scope.newname = MosaicService.data.mosaic.title;
	
	$scope.nameClick = function() {
		
		$scope.editname = true;
			
		$timeout(function() {
			$('#input-name').focus();
		});
	}
	
	$scope.nameBlur = function(newvalue) {
		
		$scope.editname = false;
		
		if (newvalue && newvalue != MosaicService.data.mosaic.title) {
			
			$scope.loadingname = true;
			MosaicService.updateName(newvalue).then(function() {
				$scope.loadingname = false;
			});
		}
	}
});

angular.module('AngularApp.controllers').controller('MyMosaicsCtrl', function($scope, $state, UserService) {
	
	$scope.page_title = 'mymosaics_TITLE';

	$scope.mosaics = UserService.data.mosaics;
	
	$scope.go = function(item) {
		$state.go('root.mosaic', {ref: item.ref});
	}
});