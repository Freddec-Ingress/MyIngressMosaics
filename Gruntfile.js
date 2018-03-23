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
					'front/scripts/ctrl.page.mosaic.js',
					'front/scripts/ctrl.page.registration.js',
					'front/scripts/ctrl.page.search.js',
					'front/scripts/ctrl.page.country.js',
					'front/scripts/ctrl.page.map.js',
					'front/scripts/ctrl.page.profile.js',
					'front/scripts/ctrl.page.world.js',
					'front/scripts/ctrl.page.region.js',
					'front/scripts/ctrl.page.city.js',
					'front/scripts/ctrl.page.creator.js',
					'front/scripts/adm.registration.js',
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