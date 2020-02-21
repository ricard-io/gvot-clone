const gulp = require('gulp');
const plugins = require('gulp-load-plugins');
const merge = require('merge-stream');
const sherpa = require('style-sherpa');
const named = require('vinyl-named');
const webpack = require('webpack');
const webpackStream = require('webpack-stream');

const browser = require('browser-sync').create();

// Load all Gulp plugins into one variable
const $ = plugins({
  rename: {
    'gulp-touch-fd': 'touch'
  }
});

/// Configuration -------------------------------------------------------------

const CONFIG = {
  // Proxy target of the BrowserSync'server
  SERVER_PROXY: 'http://127.0.0.1:8000',

  // Port on which the BrowserSync'server will listen
  SERVER_PORT: 8090,

  // Paths to other assets which will be copied
  ASSETS_FILES: [
    {
      src: [
        'assets/**/*',
        '!assets/{img,js,scss}',
        '!assets/{img,js,scss}/**/*'
      ],
      dest: ''
    },
    {
      // ForkAwesome
      src: 'node_modules/fork-awesome/fonts/*',
      dest: 'fonts/fork-awesome'
    }
  ],

  // Paths to images which will be compressed and copied
  IMAGES_FILES: [
    'assets/img/**/*'
  ],

  // Paths to JavaScript entries which will be bundled
  JS_ENTRIES: [
    'assets/js/app.js'
  ],

  // Paths to Sass files which will be compiled
  SASS_ENTRIES: [
    'assets/scss/app.scss',
    'assets/scss/fork-awesome.scss'
  ],

  // Paths to Sass libraries, which can then be loaded with @import
  SASS_INCLUDE_PATHS: [
    'node_modules'
  ],

  // Path to the build output, which will never be cleaned
  BUILD_PATH: 'gvot/static'
};

/// CSS -----------------------------------------------------------------------

// Compile Sass into CSS.
gulp.task('sass', function() {
  return gulp.src(CONFIG.SASS_ENTRIES)
    .pipe($.sourcemaps.init())
    .pipe($.sass({
      includePaths: CONFIG.SASS_INCLUDE_PATHS
    }).on('error', $.sass.logError))
    .pipe($.autoprefixer())
    .pipe($.sourcemaps.write('.'))
    .pipe(gulp.dest(`${CONFIG.BUILD_PATH}/css`))
    .pipe($.touch())
    .pipe(browser.reload({ stream: true }));
});

// Lint Sass files.
gulp.task('lint:sass', function() {
  return gulp.src('assets/scss/**/*.scss')
    .pipe($.stylelint({
      failAfterError: true,
      reporters: [
        { formatter: 'verbose', console: true }
      ]
    }));
});

// Compress CSS files.
gulp.task('compress:css', function() {
  return gulp.src([
      `${CONFIG.BUILD_PATH}/css/*.css`,
      `!${CONFIG.BUILD_PATH}/css/*.min.css`
    ])
    .pipe($.cleanCss())
    .pipe($.rename({ suffix: '.min' }))
    .pipe(gulp.dest(`${CONFIG.BUILD_PATH}/css`));
});

gulp.task('css',
  gulp.series('sass', 'compress:css'));

/// JavaScript ----------------------------------------------------------------

let webpackConfig = {
  devtool: 'source-map',
  mode: 'development',
  module: {
    rules: [
      {
        test: /.js$/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
            compact: false
          }
        }
      }
    ]
  },
  stats: {
    chunks: false,
    entrypoints: false,
  }
}

// Bundle JavaScript module.
gulp.task('javascript', function() {
  return gulp.src(CONFIG.JS_ENTRIES)
    .pipe(named())
    .pipe(webpackStream(webpackConfig, webpack))
    .pipe(gulp.dest(`${CONFIG.BUILD_PATH}/js`));
});

// Lint JavaScript source files.
gulp.task('lint:javascript', function() {
  return gulp.src('assets/js/**/*.js')
    .pipe($.eslint())
    .pipe($.eslint.format())
    .pipe($.eslint.failAfterError());
});

// Compress JavaScript files.
gulp.task('compress:javascript', function() {
  return gulp.src([
      `${CONFIG.BUILD_PATH}/js/*.js`,
      `!${CONFIG.BUILD_PATH}/js/*.min.js`
    ])
    .pipe($.terser().on('error', e => { console.log(e); }))
    .pipe($.rename({ suffix: '.min' }))
    .pipe(gulp.dest(`${CONFIG.BUILD_PATH}/js`));
});

gulp.task('scripts',
  gulp.series('javascript', 'compress:javascript'));

/// Other assets --------------------------------------------------------------

// Compress and copy images.
gulp.task('images', function() {
  return gulp.src(CONFIG.IMAGES_FILES)
    .pipe($.imagemin({ progressive: true }))
    .pipe(gulp.dest(`${CONFIG.BUILD_PATH}/img`));
});

// Copy other assets files.
gulp.task('copy', function() {
  return merge(CONFIG.ASSETS_FILES.map(
    item => gulp.src(item.src)
      .pipe(gulp.dest(`${CONFIG.BUILD_PATH}/${item.dest}`))
  ));
});

/// HTML files ----------------------------------------------------------------

// Generate a style guide from the Markdown content.
gulp.task('styleguide', done => {
  sherpa('styleguide/index.md', {
    output: 'styleguide/index.html',
    template: 'styleguide/template.html'
  }, done);
});

/// General tasks -------------------------------------------------------------

// Build and compress CSS, JavaScript and other assets.
gulp.task('build',
  gulp.parallel('css', 'scripts', 'images', 'copy', 'styleguide'));

// Watch for changes to static assets, Sass and JavaScript.
gulp.task('watch', function() {
  gulp.watch([].concat.apply([], CONFIG.ASSETS_FILES.map(a => a.src)),
    gulp.series('copy', reload));

  gulp.watch('assets/scss/**/*.scss',
    gulp.series('sass'));
  gulp.watch('assets/js/**/*.js',
    gulp.series('javascript', reload));
  gulp.watch('assets/img/**/*',
    gulp.series('images', reload));

  gulp.watch(['styleguide/*', '!styleguide/index.html'],
    gulp.series('styleguide', reload));
});

// Run a development server and watch for file changes.
gulp.task('serve',
  gulp.series(proxyServer, 'watch'));

// Run a preview server and watch for file changes.
gulp.task('serve:styleguide',
  gulp.series(styleguideServer, 'watch'));

// Lint Sass and JavaScript sources.
gulp.task('lint',
  gulp.parallel('lint:sass', 'lint:javascript'));

// An alias to the 'build' task.
gulp.task('default',
  gulp.parallel('build'));

/// Internal tasks ------------------------------------------------------------

// Start a server with BrowserSync and proxify the application in.
function proxyServer(done) {
  browser.init({
    proxy: CONFIG.SERVER_PROXY,
    port: CONFIG.SERVER_PORT,
    serveStatic: [
      {
        route: '/static',
        dir: CONFIG.BUILD_PATH
      },
      {
        route: '/styleguide',
        dir: './styleguide'
      }
    ],
    ghostMode: false,
    notify: false
  });
  done();
}

// Start a server with BrowserSync with the styleguide.
function styleguideServer(done) {
  browser.init({
    server: {
      baseDir: './styleguide',
      routes: {
        '/static': CONFIG.BUILD_PATH
      }
    },
    port: CONFIG.SERVER_PORT,
    ghostMode: false,
    notify: false
  });
  done();
}

// Reload the BrowserSync server.
function reload(done) {
  browser.reload();
  done();
}
