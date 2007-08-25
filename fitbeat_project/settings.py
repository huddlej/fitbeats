# Django settings for fitbeat_project project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('John Huddleston', 'huddlej@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '/home/huddlej/fitbeats/fitbeat_project/research.db'
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '5&02cw1#gn)gl0o%a*t(p$7yl17ny-^an$v22dr%_pq%d%$rb)'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'fitbeat_project.django-cas.middleware.CASMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'fitbeat_project.middleware.threadlocals.ThreadLocals',
)

#AUTHENTICATION_BACKENDS = (
    #'fitbeat_project.django-cas.backend.CASBackend',
#)

#CAS_SERVICE_URL = 'https://websso.wwu.edu/cas/'
#CAS_POPULATE_USER = 'fitbeat_project.utils.caslogin'

ROOT_URLCONF = 'fitbeat_project.urls'

TEMPLATE_DIRS = (
    "/home/huddlej/fitbeats/fitbeat_project/fitbeats/templates",
    "/home/huddlej/fitbeats/fitbeat_project/templates",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'fitbeat_project.fitbeats',
#    'fitbeat_project.django-cas',
)
