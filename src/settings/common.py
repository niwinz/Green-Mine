# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
import os.path, sys, os


PROJECT_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
LOGS_PATH = os.path.join(PROJECT_ROOT, 'logs')

if not os.path.exists(LOGS_PATH):
    os.mkdir(LOGS_PATH)

ADMINS = (
    ('Andrei Antoukh', 'niwi@niwi.be'),
)

LANGUAGES = (
    ('es', _('Spanish')),
    ('en', _('English')),
    ('ru', _('Russian')),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PROJECT_ROOT, 'database.sqlite'), # Or path to database file if using sqlite3.
        'OPTIONS': {'timeout': 20}
    }
}

SEND_BROKEN_LINK_EMAILS = True
IGNORABLE_404_ENDS = ('.php', '.cgi')
IGNORABLE_404_STARTS = ('/phpmyadmin/',)

REPO_ROOT = os.path.join(PROJECT_ROOT, 'repos')
AUTH_REALM = "Greenmine mercurial proxy"

TIME_ZONE = 'Europe/Madrid'
LANGUAGE_CODE = 'es'
USE_I18N = True
USE_L10N = True
LOGIN_URL='/login/'

#SESSION BACKEND
SESSION_ENGINE='django.contrib.sessions.backends.db'
#SESSION_ENGINE='django.contrib.sessions.backends.cache'
#SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = False
#SESSION_COOKIE_AGE = 1209600 # (2 weeks)


# MAIL OPTIONS
#EMAIL_USE_TLS = False
#EMAIL_HOST = 'localhost'
#EMAIL_HOST_USER = 'user'
#EMAIL_HOST_PASSWORD = 'password'
#EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = "niwi@niwi.be"

# Message System
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
#MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'


# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Don't forget to use absolute paths, not relative paths.
)

LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, 'greenmine', 'locale'),
)

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

SECRET_KEY = 'aw3+t2r(8(0kkrhg8)gx6i96v5^kv%6cfep9wxfom0%7dy0m9e'

TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

import django
# django 1.4 compatibility
if django.VERSION[:2] > (1,3):
    i = MIDDLEWARE_CLASSES.index("django.middleware.csrf.CsrfResponseMiddleware")
    del MIDDLEWARE_CLASSES[i]


TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'django.core.context_processors.static',
    "django.contrib.messages.context_processors.messages",
    "greenmine.context.main",
]

ROOT_URLCONF = 'greenmine.urls'

TEMPLATE_DIRS = [
    #os.path.join(project_root, "templates"),
]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'greenmine',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(levelname)s:%(asctime)s:%(module)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'fileout': {
            'level':'DEBUG',
            'class':'logging.FileHandler',
            'filename': os.path.join(LOGS_PATH, 'greenmine.log'),
            'formatter': 'simple',
        },
        'queryhandler': {
            'level':'DEBUG',
            'class':'logging.FileHandler',
            'filename': os.path.join(LOGS_PATH, 'greenmine-querys.log'),
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers':['null'],
            'propagate': True,
            'level':'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends':{
            'handlers': ['queryhandler'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'greenmine': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}

AUTH_PROFILE_MODULE = 'greenmine.Profile'
FORMAT_MODULE_PATH = 'greenmine.formats'
DATE_INPUT_FORMATS = ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%b %d %Y',
'%b %d, %Y', '%d %b %Y', '%d %b, %Y', '%B %d %Y',
'%B %d, %Y', '%d %B %Y', '%d %B, %Y')
