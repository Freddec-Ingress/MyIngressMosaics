angular.module('AccountApp.controllers', [])

angular.module('AccountApp.controllers').controller('LoginCtrl', function($scope, UserService) {
	
	$scope.page_title = 'login_TITLE';
	
	$scope.loginModel = { username:null, password:null };
	
	$scope.localLogin = UserService.localLogin;
	$scope.socialLogin = UserService.socialLogin;
});

angular.module('AccountApp.controllers').controller('RegisterCtrl', function($scope, UserService) {
	
	$scope.page_title = 'register_TITLE';
	
	$scope.registerModel = { username:null, password1:null, password2:null, email:null };
	
	$scope.register = UserService.register;
});

angular.module('AccountApp.controllers').controller('ProfileCtrl', function($scope, UserService, toastr, $filter) {

	$scope.user = UserService.data;
	
	/* Edit */
	
	$scope.editMode = false;
	$scope.editLoading = false;
	
	$scope.editModel = {name:null};
	
	$scope.openEdit = function() {
		
		$scope.editModel.name = $scope.user.name;
		
		$scope.editMode = true;
	}
	
	$scope.closeEdit = function() {
		
		$scope.editMode = false;
	}
	
	$scope.edit = function() {
		
		$scope.editLoading = true;
			
		UserService.updateName($scope.editModel.name).then(function(response) {
			
			toastr.success($filter('translate')('success_EDIT'));

			$scope.editMode = false;
			$scope.editLoading = false;
			
		}, function(response) {
			
			$scope.editMode = false;
			$scope.editLoading = false;
		});
	}
});
