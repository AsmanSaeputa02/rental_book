from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta

# --- Path setup ---
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# --- Security ---
SECRET_KEY = 'django-insecure-+h4su3wzz^@sfezz+o!ek5%x)izheo7b&_pq6!+)%$3h^6j4p^'
DEBUG = True  # โปรดักชันให้ False
ALLOWED_HOSTS = [
    "localhost", "127.0.0.1",
    "branch_a.localhost", "branch_b.localhost", ".localhost",
    ]
WEB_REAL_PATH = "book_project"

# --- Tenant Config ---
TENANT_MODEL = "tenants.Client"
TENANT_DOMAIN_MODEL = "tenants.Domain"

AUTH_USER_MODEL = "user.User"

SHARED_APPS = (
    "django_tenants",      # ต้องมาก่อน
    "tenants",
    "company",
    "user",

    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",

    "rest_framework",
    "drf_yasg",
    "jazzmin",
    # "tests",  # ถ้าคุณมีแอป tests รวม ใส่ไว้ที่ SHARED (ไม่ใช่ TENANT_APPS)
)

TENANT_APPS = (
    "services",
    "book",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rental",
    "dashboard",     # ✅ แก้จาก "dashbord"
    # "tests",       # ❌ ไม่ควรอยู่ใน TENANT_APPS
)

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,  # เราใช้ JWT ไม่ใช่ session
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": 'JWT Authorization header. ใช้รูปแบบ: Bearer <token>',
        }
    },
    # ให้ Swagger UI จำ token ไว้ (หลังรีเฟรชหน้า)
    "PERSIST_AUTH": True,
}




INSTALLED_APPS = list(SHARED_APPS) + [x for x in TENANT_APPS if x not in SHARED_APPS]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # โปรดักชันมักเปิด permission default ให้ต้อง auth:
    # "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
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
STATIC_URL = "/static/"                                  # ✅ แก้ให้มี / นำหน้า
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")      # => /app/staticfiles

# --- Proxy / Nginx ---
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")  # เตรียมพร้อมตอนเปิด HTTPS
CSRF_TRUSTED_ORIGINS = [
    "http://localhost", "http://127.0.0.1",
    "http://branch_a.localhost", "http://branch_b.localhost",
    "https://localhost", "https://branch_a.localhost", "https://branch_b.localhost",
    # เปิดโปรดักชันค่อยเติม "https://your-domain", "https://*.your-domain"
]

# --- Internationalization ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Bangkok"   # ใช้โซนไทยตามเครื่องคุณ
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
