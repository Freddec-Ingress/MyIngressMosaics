module.exports = function(grunt) {

	grunt.initConfig({
		
		pkg: grunt.file.readJSON('package.json'),
		
		concat: {
			css: {
				src: [
					'front/vendor/flag-icon-css/css/flag-icon.min.css',
					'front/vendor/font-awesome/css/font-awesome.min.css',
					'front/vendor/angularjs-slider/css/rzslider.min.css',
					'front/vendor/angular-uibootstrap/css/ui-bootstrap.css',
					'front/vendor/angular-toastr/css/angular-toastr.min.css',
					
					'front/css/styles.css',
				],
				dest: 'front/static/front/front.css'
			},
			js: {
				src: [
					'front/vendor/tether/js/tether.min.js',
					'front/vendor/jquery/js/jquery.min.js',
					'front/vendor/angular/js/angular.min.js',
					'front/vendor/satellizer/js/satellizer.min.js',
					'front/vendor/angular-uibootstrap/js/ui-bootstrap.js',
					'front/vendor/angular-cookies/js/angular-cookies.min.js',
					'front/vendor/angular-toastr/js/angular-toastr.tpls.min.js',
					'front/vendor/angular-translate/js/angular-translate.min.js',
					'front/vendor/angular-ui-router/js/angular-ui-router.min.js',
					
					'front/lang/en.js',
					'front/lang/fr.js',
					
					'front/scripts/services.js',
					'front/scripts/directives.js',
					'front/scripts/controllers.js',
					
					'front/scripts/app.js',
				],
				dest: 'front/static/front/front.js'
			},
		},
	});
	
	grunt.loadNpmTasks('grunt-contrib-concat');
	
	grunt.registerTask('default', ['concat']);
};