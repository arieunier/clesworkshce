import os

# hard  coded environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "")
LOG_LEVEL = os.getenv('LOG_LEVEL','INFO')
WEBPORT = os.getenv('PORT', '5000')
DATETIME_PATTERN='%Y-%m-%dT%H:%M:%S'
DATE_PATTERN='%Y-%m-%d'
TEMPLATES_URL = "../templates"
STATIC_URL = "../static"    
