from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
import oauth2_provider.views as oauth2_views
import chapeau.kepi.urls
import chapeau.trilby_api.urls
from . import settings

##################################
# OAuth2 provider endpoints

oauth2_endpoint_views = [
    path('authorize', oauth2_views.AuthorizationView.as_view(), name="authorize"),
    path('token', oauth2_views.TokenView.as_view(), name="token"),
    path('revoke-token', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]

##################################################

urlpatterns = [
        path(r'admin/', admin.site.urls),

        # auth
        path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
        path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
        path('oauth/', include((oauth2_endpoint_views, 'oauth2_provider'), namespace="oauth2_provider")),

        # chapeau's own stuff
        # path('', chapeau.tophat_ui.views.FrontPageView.as_view()), # or something
        path(r'', include(chapeau.kepi.urls)),
        path(r'', include(chapeau.trilby_api.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
