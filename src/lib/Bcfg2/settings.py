# TODO
# since were merging configs load and warn on deprecated fields

import sys
import Bcfg2.Options

try:
    import django
    has_django = True
except:
    has_django = False

DATABASES = dict()

# Django < 1.2 compat
DATABASE_ENGINE = None
DATABASE_NAME = None
DATABASE_USER = None
DATABASE_PASSWORD = None
DATABASE_HOST = None
DATABASE_PORT = None

TIME_ZONE = None

DEBUG = False
TEMPLATE_DEBUG = DEBUG

MEDIA_URL = '/site_media'


def read_config(cfile='/etc/bcfg2.conf', repo=None, quiet=False):
    global DATABASE_ENGINE, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, \
        DATABASE_HOST, DATABASE_PORT, DEBUG, TEMPLATE_DEBUG, TIME_ZONE, \
        MEDIA_URL

    setup = \
        Bcfg2.Options.OptionParser(dict(repo=Bcfg2.Options.SERVER_REPOSITORY,
                                        configfile=Bcfg2.Options.CFILE,
                                        db_engine=Bcfg2.Options.DB_ENGINE,
                                        db_name=Bcfg2.Options.DB_NAME,
                                        db_user=Bcfg2.Options.DB_USER,
                                        db_password=Bcfg2.Options.DB_PASSWORD,
                                        db_host=Bcfg2.Options.DB_HOST,
                                        db_port=Bcfg2.Options.DB_PORT,
                                        time_zone=Bcfg2.Options.DJANGO_TIME_ZONE,
                                        django_debug=Bcfg2.Options.DJANGO_DEBUG,
                                        web_prefix=Bcfg2.Options.DJANGO_WEB_PREFIX),
                                   quiet=quiet)
    setup.parse([Bcfg2.Options.CFILE.cmd, '/etc/bcfg2-web.conf', cfile])

    if repo is None:
        repo = setup['repo']

    DATABASES['default'] = \
        dict(ENGINE="django.db.backends.%s" % setup['db_engine'],
             NAME=setup['db_name'],
             USER=setup['db_user'],
             PASSWORD=setup['db_password'],
             HOST=setup['db_host'],
             PORT=setup['db_port'])

    if has_django and django.VERSION[0] == 1 and django.VERSION[1] < 2:
        DATABASE_ENGINE = setup['db_engine']
        DATABASE_NAME = DATABASES['default']['NAME']
        DATABASE_USER = DATABASES['default']['USER']
        DATABASE_PASSWORD = DATABASES['default']['PASSWORD']
        DATABASE_HOST = DATABASES['default']['HOST']
        DATABASE_PORT = DATABASES['default']['PORT']

    # dropping the version check.  This was added in 1.1.2
    TIME_ZONE = setup['time_zone']

    DEBUG = setup['django_debug']
    TEMPLATE_DEBUG = DEBUG
    if DEBUG:
        print("Warning: Setting web_debug to True causes extraordinary memory "
              "leaks.  Only use this setting if you know what you're doing.")

    if setup['web_prefix']:
        MEDIA_URL = setup['web_prefix'].rstrip('/') + MEDIA_URL
    else:
        MEDIA_URL = '/site_media'


# initialize settings from /etc/bcfg2.conf, or set up basic defaults.
# this lets manage.py work in all cases
read_config(quiet=True)

ADMINS = (('Root', 'root'))
MANAGERS = ADMINS

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# TODO - sanitize this
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'Bcfg2.Server.Reports.reports',
    'Bcfg2.Server'
)

# Imported from Bcfg2.Server.Reports
MEDIA_ROOT = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
ADMIN_MEDIA_PREFIX = '/media/'

#TODO - make this unique
# Make this unique, and don't share it with anybody.
SECRET_KEY = 'eb5+y%oy-qx*2+62vv=gtnnxg1yig_odu0se5$h0hh#pc*lmo7'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

#TODO - review these.  auth and sessions aren't really used
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

# TODO - move this to a higher root and dynamically import
ROOT_URLCONF = 'Bcfg2.Server.Reports.urls'

# TODO - this isn't usable
# Authentication Settings
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend')

LOGIN_URL = '/login'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

TEMPLATE_DIRS = (
    # App loaders should take care of this.. not sure why this is here
    '/usr/share/python-support/python-django/django/contrib/admin/templates/',
)

# TODO - sanitize this
if django.VERSION[0] == 1 and django.VERSION[1] < 2:
    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.core.context_processors.auth',
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.request'
    )
else:
    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.request'
    )

