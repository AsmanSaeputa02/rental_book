from pathlib import Path
import os
from dotenv import load_dotenv

# --- Path setup ---
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# --- Security ---
SECRET_KEY = 'django-insecure-+h4su3wzz^@sfezz+o!ek5%x)izheo7b&_pq6!+)%$3h^6j4p^'
DEBUG = True
ALLOWED_HOSTS = ["10.180.0.43","10.180.1.126","10.180.0.42", "localhost", "127.0.0.1", "edr-service.local"]
WEB_REAL_PATH = "book_project"
# --- Tenant Config ---
TENANT_MODEL = "tenants.Client"             # <app_name>.<model>
TENANT_DOMAIN_MODEL = "tenants.Domain"      # <app_name>.<model>

AUTH_USER_MODEL = "user.User"

SHARED_APPS = (
    "django_tenants",     # ต้องมาก่อน
    "tenants",    
    "company",
    "user", # app ที่มี Client / Domain
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "rest_framework",
    "drf_yasg",
    "jazzmin",   
)

TENANT_APPS = (
    "services", 
    "book",    
    "dashbord",
    "django.contrib.contenttypes",
    "django.contrib.auth",
)



INSTALLED_APPS = list(SHARED_APPS) + [x for x in TENANT_APPS if x not in SHARED_APPS]
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
}


DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

# --- Middleware ---
MIDDLEWARE = [
    "django_tenants.middleware.main.TenantMainMiddleware",  # ต้องมาก่อน
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }   
}


# --- URL ---
ROOT_URLCONF = "myproject.urls"
PUBLIC_SCHEMA_URLCONF = "myproject.urls"

# --- Templates ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "myproject.wsgi.application"

# --- Static files ---
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# --- Internationalization ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Default primary key field type ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Password validation ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
