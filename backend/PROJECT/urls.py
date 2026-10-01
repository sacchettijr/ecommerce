from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import (
    URLPattern,
    URLResolver,
    include,
    path,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path(
        route="admin/",
        view=admin.site.urls,
        name="admin",
    ),
    path(
        route="i18n/",
        view=include(
            arg="django.conf.urls.i18n",
        ),
        name="url_i18n",
    ),
    path(
        route="api-auth/",
        view=include(
            arg="rest_framework.urls",
        ),
        name="url_api",
    ),
    path(
        route="api/schema/",
        view=SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        route="api/schema/swagger/",
        view=SpectacularSwaggerView.as_view(
            url_name="schema",
        ),
        name="schema_swagger",
    ),
    path(
        route="api/schema/redoc/",
        view=SpectacularRedocView.as_view(
            url_name="schema",
        ),
        name="schema_redoc",
    ),
    path(
        route="api/core/",
        view=include(
            arg="core.urls",
        ),
        name="url_core",
    ),
    path(
        route="api/account/",
        view=include(
            arg="account.urls",
        ),
        name="url_account",
    ),
    path(
        route="api/product/",
        view=include(
            arg="product.urls",
        ),
        name="url_product",
    ),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path(
            route="__debug__/",
            view=include(
                arg=debug_toolbar.urls,
            ),
            name="url_debug",
        ),
        path(
            route="__reload__/",
            view=include(
                arg="django_browser_reload.urls",
            ),
            name="url_reload",
        ),
    ]


urlpatterns += static(
    prefix=settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT,
)
