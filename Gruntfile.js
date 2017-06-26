module.exports = function(grunt) {

	grunt.initConfig({
		
		pkg: grunt.file.readJSON('package.json'),
		
		concat: {
			css: {
				src: [
					'front/css/styles.css',
				],
				dest: 'front/static/front/css/front.css'
			},
			js: {
				src: [
					'front/scripts/controllers.js',
					
					'front/scripts/app.js',
				],
				dest: 'front/static/front/js/front.js'
			},
		},
	});
	
	grunt.loadNpmTasks('grunt-contrib-concat');
	
	grunt.registerTask('default', ['concat']);
};