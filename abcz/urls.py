"""
URL configuration for abcz project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.staticfiles import finders
from django.contrib.sitemaps.views import sitemap
from django.http import FileResponse, Http404, HttpResponse
from django.urls import path, include

from phonics.admin_views import operations_dashboard
from phonics.sitemaps import sitemaps


def google_site_verification(request):
    return HttpResponse(
        "google-site-verification: googlea532a5ae726057b6.html",
        content_type="text/plain; charset=utf-8",
    )


def robots_txt(request):
    content = "\n".join((
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /profile/",
        "Disallow: /checkout/",
        "Disallow: /payments/",
        "Disallow: /api/",
        "Disallow: /certificate/",
        "Disallow: /health/",
        "",
        "Sitemap: https://www.smartlearningksa.com/sitemap.xml",
        "",
    ))
    return HttpResponse(content, content_type="text/plain; charset=utf-8")


def site_icon(request, filename, content_type):
    icon_path = finders.find(f"brand/{filename}")
    if icon_path is None:
        raise Http404("Site icon not found")
    response = FileResponse(open(icon_path, "rb"), content_type=content_type)
    response["Cache-Control"] = "public, max-age=604800"
    return response


def favicon(request):
    return site_icon(request, "favicon.ico", "image/x-icon")


def apple_touch_icon(request):
    return site_icon(request, "apple-touch-icon.png", "image/png")


def apple_touch_icon_precomposed(request):
    return site_icon(request, "apple-touch-icon-precomposed.png", "image/png")


urlpatterns = [
    path("favicon.ico", favicon, name="favicon"),
    path("apple-touch-icon.png", apple_touch_icon, name="apple_touch_icon"),
    path("apple-touch-icon-precomposed.png", apple_touch_icon_precomposed, name="apple_touch_icon_precomposed"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path(
        'googlea532a5ae726057b6.html',
        google_site_verification,
        name='google_site_verification',
    ),
    path(
        'admin/operations-dashboard/',
        admin.site.admin_view(operations_dashboard),
        name='admin_operations_dashboard',
    ),
    path('admin/', admin.site.urls),
    path('', include('phonics.urls')),
    path('accounts/', include('allauth.urls')),
]
