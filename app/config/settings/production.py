from .base import *  # noqa
from decouple import config

DEBUG = config('DEBUG', cast=bool, default=False)

SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', cast=bool, default=False)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
