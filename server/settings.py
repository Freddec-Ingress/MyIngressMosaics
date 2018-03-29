import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'kax0(s#e6r)q$ut!&uwmtbps3zf0-ijg^l@vkhi+ji(in-b_qs'

DEBUG = True

ALLOWED_HOSTS = ['www.myingressmosaics.com', 'myingressmosaics.com', 'myingressmosaics-freddec.c9users.io', 'www.ingress.com', 'ingressmosaik.com']

CORS_ORIGIN_WHITELIST = (
    'www.myingressmosaics.com',
    'myingressmosaics.com',
    'myingressmosaics-freddec.c9users.io',
    'www.ingress.com',
    'ingressmosaik.com',
)

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SITE_ID = 1

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

MEDIA_URL = '/preview/'
MEDIA_ROOT = os.path.join(BASE_DIR, '/static/preview')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',

    'storages',
    'corsheaders',
    
	'rest_framework',
	'rest_framework.authtoken',
    'background_task',

	'social_django',
	'rest_social_auth',
    
    'api',
    'front',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'server.wsgi.application'

import dj_database_url

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, default='postgres://myingressmosaicsuser:' + 'freddec@2012' + '@localhost:5432/myingressmosaics')
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

STATICFILES_DIRS = (
   os.path.join(BASE_DIR, 'static'),
)

SOCIAL_AUTH_REDIRECT_IS_HTTPS = 'True'

SOCIAL_AUTH_FACEBOOK_KEY = '237811833398918'
SOCIAL_AUTH_FACEBOOK_SECRET = 'ed990f9824156e64ba36e71f4fe0cf97'
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', ]

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '404579985700-eig13jlsdvbe6bhmtsis46tsn7nij4ju.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '5YRXxGQOfnrBAWtNgLb2ulds'
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email', ]

REST_SESSION_LOGIN = False

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.TokenAuthentication',
    ],
    
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

AUTHENTICATION_BACKENDS = (
	'social_core.backends.google.GoogleOAuth2',
	'social_core.backends.facebook.FacebookOAuth2',
	'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PIPELINE = (
	'api.pipeline.auto_logout',
	'social_core.pipeline.social_auth.social_details',
	'social_core.pipeline.social_auth.social_uid',
	'social_core.pipeline.social_auth.auth_allowed',
	'social_core.pipeline.social_auth.social_user',
	'social_core.pipeline.user.get_username',
	'social_core.pipeline.user.create_user',
	'social_core.pipeline.social_auth.associate_user',
	'social_core.pipeline.social_auth.load_extra_data',
	'social_core.pipeline.user.user_details',
)

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'verbose': {
			'format': '%(levelname)s:%(name)s: %(message)s '
								'(%(asctime)s; %(filename)s:%(lineno)d)',
			'datefmt': "%Y-%m-%d %H:%M:%S",
		},
	},
	'handlers': {
		'console': {
			'level': 'DEBUG',
			'class': 'logging.StreamHandler',
			'formatter': 'verbose',
		},
	},
	'loggers': {
		'rest_social_auth': {
			'handlers': ['console', ],
			'level': "DEBUG",
		},
	}
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_PORT = 587

EMAIL_HOST = 'ssl0.ovh.net'
EMAIL_HOST_USER = 'admin@myingressmosaics.com'
EMAIL_HOST_PASSWORD = 'freddec@2012'

EMAIL_USE_TLS = True
