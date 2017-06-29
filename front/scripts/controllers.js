angular.module('AngularApp.controllers', [])

angular.module('AngularApp.controllers').controller('RootCtrl', function($scope, $stateParams, $translate, $window, UserService) {
	
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
});

angular.module('AngularApp.controllers').controller('HomeCtrl', function($scope) {
});

angular.module('AngularApp.controllers').controller('LoginCtrl', function($scope, UserService) {
	
	$scope.loginModel = { username:null, password:null };
	
	$scope.localLogin = UserService.localLogin;
	$scope.socialLogin = UserService.socialLogin;
});

angular.module('AngularApp.controllers').controller('RegisterCtrl', function($scope, UserService) {
	
	$scope.registerModel = { username:null, password1:null, password2:null, email:null };
	
	$scope.register = UserService.register;
});

angular.module('AngularApp.controllers').controller('ProfileCtrl', function($scope, UserService, $timeout) {
	
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

	CreateService.init();
	
	$scope.missions = UserService.data.missions;
	
	$scope.isSelected = function(ref) {
		
		if (CreateService.getRefArray().indexOf(ref) != -1) {
			return true;
		} else {
			return false;
		}
	}
	
	$scope.toggle = function(item) {
		
		if ($scope.isSelected(item.ref)) {
			CreateService.remove(item);
		}
		else {
			CreateService.add(item);
		}
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
});

angular.module('AngularApp.controllers').controller('CreateCtrl', function($scope, $state, CreateService) {

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

angular.module('AngularApp.controllers').controller('MosaicCtrl', function($scope, MosaicService) {
	
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
});

angular.module('AngularApp.controllers').controller('MyMosaicsCtrl', function($scope, $state, UserService) {

	$scope.mosaics = UserService.data.mosaics;
	
	$scope.go = function(item) {
		$state.go('root.mosaic', {ref: item.ref});
	}
});