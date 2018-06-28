#coding=utf-8
"""
Django settings for AutoFWOG project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'c5f3+by307s#lg&z-2&qae1ha_)zzo!!)yds20i=zefkgwy3ow'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'AutoFW',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)


# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "asgiref.inmemory.ChannelLayer",
#         "CONFIG": {
#             "hosts": [os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/2')],
#         },
#         "ROUTING": "AutoFWOG.routing.channel_routing",
#     },
# }

ROOT_URLCONF = 'AutoFWOG.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
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

WSGI_APPLICATION = 'AutoFWOG.wsgi.application'

# AutoFWOG/settings.py
# Channels
#ASGI_APPLICATION = "AutoFWOG.routing.application"

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'autofw',
        'USER':'root',
        'PASSWORD':'123456',
        'HOST':'localhost',
        'PORT':'3306',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

#timezone problem
USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS=[
    os.path.join(BASE_DIR,'static')
]



LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        # 'require_debug_true': {
        #     '()': 'django.utils.log.RequireDebugTrue',
        # }, # 针对 DEBUG = True 的情况
    },
    'formatters': {
        'standard': {
            'format': '%(levelname)s %(asctime)s %(pathname)s %(filename)s %(module)s %(funcName)s %(lineno)d: %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(filename)s %(module)s %(funcName)s %(lineno)d: %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
             'formatter':'standard'
        },
        'request_handler': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR,'AutoFW/log/script.log'),
            'maxBytes': 1024*1024*5,
            'backupCount': 5,
            'formatter':'standard',
        },
        # 'file_handler': {
        #      'level': 'INFO',
        #      'class': 'logging.handlers.TimedRotatingFileHandler',
        #      'filename': '/home/fzyzgong/project/AutoFWOG/AutoFW/log/log.txt',
        #      'formatter':'standard'
        # }, # 用于文件输出
        'default': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR,'AutoFW/log/info.log'),     #日志输出文件
            'maxBytes': 1024*1024*5,                  #文件大小
            'backupCount': 5,                         #备份份数
            'formatter':'simple',                   #使用哪种formatters日志格式
        },
        'error': {
            'level':'ERROR',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR,'AutoFW/log/error.log'),
            'maxBytes':1024*1024*5,
            'backupCount': 5,
            'formatter':'standard',
        },
        'scprits_handler': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename':os.path.join(BASE_DIR,'AutoFW/log/script.log'),
            'maxBytes': 1024*1024*5,
            'backupCount': 5,
            'formatter':'standard',
        },
        'console':{
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers' :['default','console'],#,'console'
            'level':'INFO',
            'propagate': False # 是否继承父类的log信息
        }, # handlers 来自于上面的 handlers 定义的内容
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'scripts': {
            'handlers': ['scprits_handler','default'],
            'level': 'INFO',
            'propagate': False
        },
    }
}