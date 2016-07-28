/**
 * 1. Download and install Node.js.
 * 2. Install gulp:
 *      $ npm install --global gulp-cli.
 * 3. Install dependencies:
 *      $ npm install --save-dev gulp.
 * 4. Run gulp:
 *      $ gulp.
 * 5. Go to: http://localhost:8080/
 */

// TODO: minify js
var gulp = require('gulp'),
    fileinclude = require('gulp-file-include'),
    sass = require('gulp-sass'),
    connect = require('gulp-connect');

gulp.task('include', function () {
    gulp.src('./html/pages/*.html')
        .pipe(fileinclude())
        .pipe(gulp.dest('./html/'))
        .pipe(connect.reload());
});

gulp.task('sass', function () {
    return gulp.src('./css/scss/*.scss')
        .pipe(sass().on('error', sass.logError))
        .pipe(gulp.dest('./css'))
        .pipe(connect.reload());
});

gulp.task('connect', function () {
    connect.server({
        livereload: true
    });
});

gulp.task('watch', function () {
    gulp.watch('./html/**', ['include']);
    gulp.watch('./css/scss/**', ['sass']);
});

gulp.task('default', ['include', 'sass', 'watch', 'connect']);