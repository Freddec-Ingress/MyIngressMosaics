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
		    js: {
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
		},
	});
	
	grunt.loadNpmTasks('grunt-contrib-concat');
	
	grunt.registerTask('default', ['concat']);
};