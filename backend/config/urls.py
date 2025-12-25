from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from apps.authentication.api import router as auth_router

api = NinjaAPI(
    title="My App API",
    version="1.0.0",
    description="API for my application",
)

api.add_router("/auth/", auth_router, tags=["Authentication"])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
