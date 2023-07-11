from django.urls import path
from . import views
# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns =[
    path('', views.displayRoutes),
    # path('Api/Schema/', SpectacularAPIView.as_view(), name="schema"),
    # path("Api/Schema/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path('getUsers/', views.get_users, name="getUserListApi"),
    path('createUser/', views.create_user),
    path('loginUser/', views.login_user),
    path('updateUser/', views.update_user),
    path('deleteUser/', views.delete_user),
    path('api/token/', views.getFreshJWTToken),
    path('api/token/validate', views.isJWTValid),
    path('api/protected/test/get',views.testGETendpoint),
    path('api/protected/test/post',views.testPOSTendpoint),
    path("test/http_response", views.test_HTTP_response)
]

# 