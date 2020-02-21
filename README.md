# GvoT

Logiciel de votation

**Table of content**

- [Give a try](#give-a-try)
- [Installation](#installation)
- [Deployment](#deployment)
- [Structure](#structure)
- [Development](#development)

## Give a try

On a Debian-based host - running at least Debian Stretch:

```
$ sudo apt install python3 virtualenv git make
$ git clone https://forge.cliss21.org/cliss21/gvot
$ cd gvot/
$ make init

A configuration will be created interactively; uncomment
ENV=development

$ make test # optional
$ make serve
```

Then visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your web browser.

## Installation
### Requirements

On a Debian-based host - running at least Debian Stretch, you will need the
following packages:
- python3
- virtualenv
- make
- git (recommended for getting the source)
- python3-mysqldb (optional, in case of a MySQL / MariaDB database)
- python3-psycopg2 (optional, in case of a PostgreSQL database)

### Quick start

It assumes that you already have the application source code locally - the best
way is by cloning this repository - and that you are in this folder.

1.  Define your local configuration in a file named `config.env`, which can be
    copied from `config.env.example` and edited to suits your needs.

    Depending on your environment, you will have to create your database and the
    user at first.

2.  Run `make init`.

    Note that if there is no `config.env` file, it will be created interactively.

That's it! Your environment is now initialized with the application installed.
To update it, once the source code is checked out, simply run `make update`.

You can also check that your application is well configured by running
`make check`.

### Manual installation

If you don't want to use the `Makefile` facilities, here is what is done behind the scene.

It assumes that you have downloaded the last release of GvoT,
extracted it and that you moved to that folder.

1.  Start by creating a new virtual environment under `./venv` and activate it:

        $ virtualenv --system-site-packages ./venv
        $ source ./venv/bin/activate

2.  Install the required Python packages depending on your environment:

        $ pip install -r requirements/production.txt
        ... or ...
        $ pip install -r requirements/development.txt

3.  Configure the application by setting the proper environment variables
    depending on your environment. You can use the `config.env.example` which
    give you the main variables with example values.

        $ cp config.env.example config.env
        $ nano config.env
        $ chmod go-rwx config.env

    Note that this `./config.env` file will be loaded by default when the
    application starts. If you don't want that, just move this file away or set
    the `READ_CONFIG_FILE` environment variable to `0`.

4.  Create the database tables - it assumes that you have created the database
    and set the proper configuration to use it:

        $ ./manage.py migrate

That's it! You should now be able to start the Django development server to
check that everything is working fine with:

    $ ./manage.py runserver

## Deployment

Here is an example deployment using NGINX - as the Web server - and uWSGI - as
the application server.

The uWSGI configuration doesn't require a special configuration, except that we
are using Python 3 and a virtual environment. Note that if you serve the
application on a sub-location, you will have to add `route-run = fixpathinfo:`
to your uWSGI configuration (from
[v2.0.11](https://uwsgi-docs.readthedocs.io/en/latest/Changelog-2.0.11.html#fixpathinfo-routing-action)).

In the `server` block of your NGINX configuration, add the following blocks and
set the path to your application instance and to the uWSGI socket:

```
location / {
    include uwsgi_params;
    uwsgi_pass unix:<uwsgi_socket_path>;
}
location /media {
    alias <app_instance_path>/var/media;
}
location /static {
    alias <app_instance_path>/var/static;
    # Optional: don't log access to assets
    access_log off;
}
location = /favicon.ico {
    alias <app_instance_path>/var/static/favicon/favicon.ico;
    # Optional: don't log access to the favicon
    access_log off;
}
```

## Structure
### Overview

All the application files - e.g. Django code including settings, templates and
statics - are located into `gvot/`.

Two environments are defined - either for requirements and settings:
- `development`: for local application development and testing. It uses a
  SQLite3 database and enable debugging by default, add some useful settings
  and applications for development purpose - i.e. the `django-debug-toolbar`.
- `production`: for production. It checks that configuration is set and
  correct, try to optimize performances and enforce some settings - i.e. HTTPS
  related ones.

### Local changes

You can override and extend statics and templates locally. This can be useful
if you have to change the logo for a specific instance for example. For that,
just put your files under the `local/static/` and `local/templates/` folders.

Regarding the statics, do not forget to collect them after that. Note also that
the `local/` folder is ignored by *git*.

### Variable content

All the variable content - e.g. user-uploaded media, collected statics - are
stored inside the `var/` folder. It is also ignored by *git* as it's specific
to each application installation.

So, you will have to configure your Web server to serve the `var/media/` and
`var/static/` folders, which should point to `/media/` and `/static/`,
respectively.

## Development

The easiest way to deploy a development environment is by using the `Makefile`.

Before running `make init`, ensure that you have either set `ENV=development`
in the `config.env` file or have this environment variable. Note that you can
still change this variable later and run `make init` again.

There is some additional rules when developing, which are mainly wrappers for
`manage.py`. You can list all of them by running `make help`. Here are the main ones:
- `make serve`: run a development server
- `make test`: test the whole application
- `make lint`: check the Python code syntax

### Assets

The assets - e.g. CSS, JavaScript, images, fonts - are generated using a
[Gulp](https://gulpjs.com/)-powered build system with these features:
- SCSS compilation and prefixing
- JavaScript module bundling with webpack
- Styleguide and components preview
- Built-in BrowserSync server
- Compression for production builds

The source files live in `assets/`, and the styleguide in `styleguide/`.

#### Requirements

You will need to have [npm](https://www.npmjs.com/) installed on your system.
If you are running Debian, do not rely on the npm package which is either
outdated or removed - starting from Debian Stretch. Instead, here is a way
to install the last version as a regular user:

1.  Ensure that you have the following Debian packages installed, from at least
    `stretch-backports`:
      - nodejs
      - node-rimraf

2.  Set the npm's installation prefix as an environment variable:

	      $ export npm_config_prefix=~/.node_modules

3.  Retrieve and execute the last npm's installation script:

	      $ curl -L https://www.npmjs.com/install.sh | sh

4.  Add the npm's binary folder to your environment variables:

        $ export PATH="${HOME}/.node_modules/bin:${PATH}"

    In order to keep those environment variables the next time you will log in,
    you can append the following lines to the end of your `~/.profile` file:

    ```bash
    if [ -d "${HOME}/.node_modules/bin" ] ; then
        PATH="${HOME}/.node_modules/bin:${PATH}"
        export npm_config_prefix=~/.node_modules
    fi
    ```

5.  That's it! You can check that npm is now installed by running the following:

        $ npm --version

#### Usage

Start by installing the application dependencies - which are defined in
`package.json` - by running: `npm install`.

The following tasks are then available:
- `npm run build`: build all the assets for development and production use,
  and put them in the static folder - e.g `gvot/static`.
- `npm run styleguide`: run a server with the styleguide and watch for file
  changes.
- `npm run serve`: run a proxy server to the app - which must already be served on
  `localhost:8000` - with the styleguide on `/styleguide` and watch for file
  changes.
- `npm run lint`: lint the JavaScript and the SCSS code.

In production, only the static files will be used. It is recommended to commit
the compiled assets just before a new release only. This will prevent to have a
growing repository due to the minified files.

## License

GvoT is developed by Cliss XXI and licensed under the
[AGPLv3+](LICENSE).
