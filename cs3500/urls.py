from grades import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('', views.index),
    path('admin/', admin.site.urls),
    path('profile/', views.profile),
    path('profile/login/', views.login_form),
    path('<int:assignment_id>/submissions/', views.submissions),
    path("<int:assignment_id>/", views.assignment),
    path('uploads/<str:filename>', views.show_upload),
    path("profile/logout/", views.logout_form)
]


