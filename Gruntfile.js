module.exports = function(grunt) {

	grunt.initConfig({
		
		pkg: grunt.file.readJSON('package.json'),
		
		concat: {
			css: {
				src: [
					'vendor/flag-icon-css/css/flag-icon.min.css',
					'vendor/font-awesome/css/font-awesome.min.css',
					'vendor/angularjs-slider/css/rzslider.min.css',
					'vendor/angular-uibootstrap/css/ui-bootstrap.css',
					'vendor/angular-toastr/css/angular-toastr.min.css',
					
					'front/css/styles.css',
				],
				dest: 'static/front.css'
			},
			frontmodulejs: {
				src: [
					'vendor/tether/js/tether.min.js',
					'vendor/jquery/js/jquery.min.js',
					'vendor/angular/js/angular.min.js',
					'vendor/satellizer/js/satellizer.min.js',
					'vendor/angular-uibootstrap/js/ui-bootstrap.js',
					'vendor/angular-cookies/js/angular-cookies.min.js',
					'vendor/angular-toastr/js/angular-toastr.tpls.min.js',
					'vendor/angular-translate/js/angular-translate.min.js',
					'vendor/angular-ui-router/js/angular-ui-router.min.js',
					
					'front/lang/en.js',
					'front/lang/fr.js',
					
					'front/scripts/services.js',
					'front/scripts/directives.js',
					'front/scripts/controllers.js',
					'front/scripts/module.js',
				],
				dest: 'static/front.js'
			},
			accountappjs: {
				src: [
					'front/apps/account/scripts/services.js',
					'front/apps/account/scripts/directives.js',
					'front/apps/account/scripts/controllers.js',
					'front/apps/account/scripts/app.js',
				],
				dest: 'static/account.js'
			},
			creatorappjs: {
				src: [
					'front/apps/creator/scripts/services.js',
					'front/apps/creator/scripts/directives.js',
					'front/apps/creator/scripts/controllers.js',
					'front/apps/creator/scripts/app.js',
				],
				dest: 'static/creator.js'
			},
			homeappjs: {
				src: [
					'front/apps/home/scripts/services.js',
					'front/apps/home/scripts/directives.js',
					'front/apps/home/scripts/controllers.js',
					'front/apps/home/scripts/app.js',
				],
				dest: 'static/home.js'
			},
			mapappjs: {
				src: [
					'front/apps/map/scripts/services.js',
					'front/apps/map/scripts/directives.js',
					'front/apps/map/scripts/controllers.js',
					'front/apps/map/scripts/app.js',
				],
				dest: 'static/map.js'
			},
			mosaicappjs: {
				src: [
					'front/apps/mosaic/scripts/services.js',
					'front/apps/mosaic/scripts/directives.js',
					'front/apps/mosaic/scripts/controllers.js',
					'front/apps/mosaic/scripts/app.js',
				],
				dest: 'static/mosaic.js'
			},
			registrationappjs: {
				src: [
					'front/apps/registration/scripts/services.js',
					'front/apps/registration/scripts/directives.js',
					'front/apps/registration/scripts/controllers.js',
					'front/apps/registration/scripts/app.js',
				],
				dest: 'static/registration.js'
			},
			searchappjs: {
				src: [
					'front/apps/search/scripts/services.js',
					'front/apps/search/scripts/directives.js',
					'front/apps/search/scripts/controllers.js',
					'front/apps/search/scripts/app.js',
				],
				dest: 'static/search.js'
			},
		},
	});
	
	grunt.loadNpmTasks('grunt-contrib-concat');
	
	grunt.registerTask('default', ['concat']);
};