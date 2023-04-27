import scripts.functions as Functions

from pathlib import Path
import os


# Constants for the site

SITE_DOMAIN = 'http://127.0.0.1:8000/'


# Build paths inside the project like this: BASE_DIR / 'subdir'.

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = True
ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ['127.0.0.1']


# Check and create folders

if Functions.if_find_folder_or_file(BASE_DIR, 'logs') == False:
	os.mkdir(BASE_DIR / 'logs')

if Functions.if_find_folder_or_file(BASE_DIR, 'data') == False:
	os.mkdir(BASE_DIR / 'data')


# SECURITY WARNING: keep the secret key used in production secret!

if Functions.if_find_folder_or_file(BASE_DIR / 'data', 'secret.key') == False:
	SECRET_KEY = f"django-insecure-{Functions.generator_secret_string(length=50, chars='abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()_')}"
	
	with open( BASE_DIR / 'data/secret.key', 'w') as f:
		f.write(SECRET_KEY)
else:
	with open(BASE_DIR / 'data/secret.key', 'r') as f:
		SECRET_KEY = f.read()


# Logs settings

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'verbose': {
			'format': '[{asctime}]: {name} > {funcName} || {message}',
			'style': '{',
		},
		'simple': {
			'format': '[{asctime}]: {message}',
			'style': '{',
		},
	},
	'handlers': {
		'console': {
			'level': 'INFO',
			'class': 'logging.StreamHandler',
			'formatter': 'simple',
		},
		'info_file': { 
			'level': 'INFO',
			'class': 'logging.FileHandler',
			'filename': BASE_DIR / 'logs/info.log',
			'formatter': 'simple',
		},
		'debug_file': { 
			'level': 'DEBUG',
			'class': 'logging.FileHandler',
			'filename': BASE_DIR / 'logs/debug.log',
			'formatter': 'verbose',
		},
		'warning_file': { 
			'level': 'WARNING',
			'class': 'logging.FileHandler',
			'filename': BASE_DIR / 'logs/warning.log',
			'formatter': 'verbose',
		},
		'error_file': { 
			'level': 'ERROR',
			'class': 'logging.FileHandler',
			'filename': BASE_DIR / 'logs/error.log',
			'formatter': 'verbose',
		},
	},
	'loggers': {
		'django': {
			'handlers': [
				'console',
				'info_file',
				'debug_file',
				'warning_file',
				'error_file',
			],
			'propagate': True,
		},
		'django.request': {
			'handlers': [
				'console',
				'info_file',
				'debug_file',
				'warning_file',
				'error_file',
			],
			'propagate': False,
		},
		'django.template': {
			'handlers': [
				'debug_file',
			],
			'propagate': False,
		},
		'django.db.backends': {
			'handlers': [
				'debug_file',
				'warning_file',
				'error_file',
			],
			'propagate': False,
		},
	},
}


# Application definition

INSTALLED_APPS = [
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',

	'debug_toolbar',

	'scripts.apps.ScriptsConfig',

	'user.apps.UserConfig',
	'telegram_bot.apps.TelegramBotConfig',

	'home.apps.HomeConfig',
	'donation.apps.DonationConfig',
	'personal_cabinet.apps.PersonalCabinetConfig',

	'learn_more.apps.LearnMoreConfig',
	'privacy_policy.apps.PrivacyPolicyConfig',
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'constructor_telegram_bots.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [BASE_DIR / 'templates'],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	}
]

WSGI_APPLICATION = 'constructor_telegram_bots.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': BASE_DIR / 'data/DataBase.db',
	}
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
	{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
	{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
	{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
	{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

AUTH_USER_MODEL = 'user.User'

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Tallinn'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/static/'

if DEBUG:
	STATICFILES_DIRS = [
		BASE_DIR / 'static/',
	]
else:
	STATIC_ROOT = BASE_DIR / 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
