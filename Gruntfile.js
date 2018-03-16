module.exports = function(grunt) {

	grunt.initConfig({
		
		pkg: grunt.file.readJSON('package.json'),
		
		concat: {
			css: {
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
					'front/css/form.css',
				],
				dest: 'static/front.css'
			},
		    js: {
				src: [
					'vendor/jquery/js/jquery.min.js',
					'vendor/angular/js/angular.min.js',
					'vendor/satellizer/js/satellizer.min.js',

					'front/scripts/services.js',
					'front/scripts/directives.js',
					'front/scripts/controllers.js',
					'front/scripts/ctrl.newmosaic.js',
					'front/scripts/ctrl.newregistration.js',
					'front/scripts/ctrl.newsearch.js',
					'front/scripts/ctrl.newcountry.js',
					'front/scripts/ctrl.newmap.js',
					'front/scripts/ctrl.newprofile.js',
					'front/scripts/ctrl.newworld.js',
					'front/scripts/ctrl.newregion.js',
					'front/scripts/ctrl.newcity.js',
					'front/scripts/ctrl.newcreator.js',
					'front/scripts/adm.region.js',
					'front/scripts/adm.city.js',
					'front/scripts/adm.registration.js',
					'front/scripts/adm.mosaic.js',
					'front/scripts/adm.mission.js',
					'front/scripts/adm.compare.js',
					'front/scripts/module.js',
				],
				dest: 'static/front.js'
            },
		},
	});
	
	grunt.loadNpmTasks('grunt-contrib-concat');

	grunt.registerTask('default', ['concat']);
};