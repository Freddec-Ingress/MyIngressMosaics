module.exports = function(grunt) {

	grunt.initConfig({
		
		pkg: grunt.file.readJSON('package.json'),
		
		concat: {
			css: {
				src: [
					'vendor/flag-icon-css/css/flag-icon.min.css',
					'vendor/font-awesome/css/font-awesome.min.css',
					'vendor/angular-toastr/css/angular-toastr.min.css',

					'front/css/styles.css',
				],
				dest: 'static/front.css'
			},
			css2: {
				src: [
					'vendor/flag-icon-css/css/flag-icon.min.css',
					'vendor/font-awesome/css/font-awesome.min.css',

					'front/css/html.css',
					'front/css/tabs.css',
					'front/css/badge.css',
					'front/css/modal.css',
					'front/css/utils.css',
					'front/css/layout.css',
					'front/css/button.css',
				],
				dest: 'static/newfront.css'
			},
		    js: {
				src: [
					'vendor/jquery/js/jquery.min.js',
					'vendor/angular/js/angular.min.js',
					'vendor/satellizer/js/satellizer.min.js',
					'vendor/angular-cookies/js/angular-cookies.min.js',
					'vendor/angular-toastr/js/angular-toastr.min.js',
					'vendor/angular-toastr/js/angular-toastr.tpls.min.js',
					
					'front/data/country_locale.js',
					'front/data/region_locale.js',
					'front/data/city_locale.js',
					
					'front/scripts/services.js',
					'front/scripts/directives.js',
					'front/scripts/controllers.js',
					'front/scripts/ctrl.registration.js',
					'front/scripts/ctrl.newmosaic.js',
					'front/scripts/module.js',
				],
				dest: 'static/front.js'
            },
		},
	});
	
	grunt.loadNpmTasks('grunt-contrib-concat');
	
	grunt.registerTask('default', ['concat']);
};