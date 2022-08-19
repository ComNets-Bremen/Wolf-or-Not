from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('img/<uuid:uuid>/', views.get_image, name='get_image'),
    path('poll', views.PollImageView.as_view(), name='poll'),
    path('upload', views.UploadImagesView.as_view(), name='upload_images'),
]


