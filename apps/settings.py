# Django settings for localground project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG
GDAL_LIBRARY_PATH='/usr/lib/libgdal.so'     #replace with your GDAL path

ADMINS = (
    ('Jane Admin', 'email@yoursite.com'),
)
DEFAULT_FROM_EMAIL = '"Site Support" <support@yoursite.com>'
ADMIN_EMAILS = ['admin1@yoursite.com', 'admin2@yoursite.com']
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
REGISTRATION_OPEN = True
ONLY_SUPERUSERS_CAN_REGISTER_PEOPLE = False
ACCOUNT_ACTIVATION_DAYS = 5

MANAGERS = ADMINS
AUTH_PROFILE_MODULE = 'account.UserProfile'

HOST = '127.0.0.1'          #Your Database Host
PORT = '#####'              #Your Database Port
USERNAME = 'DB_USER'        #Your Database Username
PASSWORD = 'DB_PASSWORD'    #Your Database Password
DATABASE = 'DB_NAME'        #Your Database Name

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', #Code works w/PostGIS
        'NAME': DATABASE, 
        'USER': USERNAME,
        'PASSWORD': PASSWORD,
        'HOST': HOST,
        'PORT': PORT, 
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None

DATE_INPUT_FORMATS = ('%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y', '%m-%d-%y', '%m-%d-%Y')
TIME_INPUT_FORMATS = ('%I:%M:%S %p', '%H:%M:%S', '%H:%M')

#dynamically build datetime formats from tuples above:
DATETIME_INPUT_FORMATS = []
for date_format in DATE_INPUT_FORMATS:
    for time_format in TIME_INPUT_FORMATS:
        DATETIME_INPUT_FORMATS.append(date_format + ' ' + time_format)  
DATETIME_INPUT_FORMATS = tuple(DATETIME_INPUT_FORMATS)

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory root of the local ground instance:
FILE_ROOT = '/home/directory/for/localground'
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'
CUSTOM_MEDIA_PREFIX = '/static/'
JQUERY_UI_PATH = 'http://ajax.aspnetcdn.com/ajax/jquery.ui/1.8.8/jquery-ui.min.js'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+z2(@u0ev(4k5p())l38j$ea6o$@irxtc_8qgp-^a60qn239**'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'localground.apps.middleware.impersonate.ImpersonateMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'localground.apps.middleware.context_processors.persistant_queries', #for our application-level context objects
)

ROOT_URLCONF = 'localground.apps.urls'
SESSION_COOKIE_NAME = 'sessionid'

TEMPLATE_DIRS = (
    '%s/templates' % FILE_ROOT,
    '%s/account/templates' % FILE_ROOT,
)
FIXTURE_DIRS = (
    '%s/fixtures' % FILE_ROOT,
)

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.gis',
    'django.contrib.messages',
    'localground.apps',
    'localground.apps.account',
    'localground.apps.api',
    'localground.apps.helpers',
    'localground.apps.prints',
    'localground.apps.uploads',
    'localground.apps.overlays',
    'localground.apps.registration',     #taken from the django-registration module
    'tagging',                      #for tagging of blog posts in Django
    'django.contrib.admin',
    'localground.apps.jobs'

)
TAGGING_AUTOCOMPLETE_JS_BASE_URL = '/static/scripts/jquery-autocomplete'

#OS variables:
USER_ACCOUNT = 'linux-user-account'     #account to use for creating new OS files / directories
GROUP_ACCOUNT = 'linux-user-group'      #group to use for creating new OS files / directories

FILE_UPLOAD_MAX_MEMORY_SIZE = 4621440   #default is 2621440
CLOUDMADE_KEY = 'CLOUDMADE_KEY'         #http://support.cloudmade.com/answers/api-keys-and-authentication
IS_GOOGLE_REGISTERED_NONPROFIT = False
QR_READER_PATH = '%s/utils/' % FILE_ROOT

# Custom Local Variables
SERVER_HOST = 'yoursite.com'
SERVER_URL = 'http://%s' % SERVER_HOST
STATIC_ROOT = '%s/static' % FILE_ROOT
FONT_ROOT = '%s/static/css/fonts/' % FILE_ROOT
TEMP_DIR = STATIC_ROOT + '/tmp/'
MAP_FILE = FILE_ROOT + '/mapserver/localground.map'
DEFAULT_BASEMAP_ID = 12

# Local settings override project settings
try:
    LOCAL_SETTINGS
except NameError:
    try:
        from settings_local import *
    except ImportError:
        pass

