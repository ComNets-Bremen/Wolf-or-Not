from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('img/<uuid:uuid>/', views.get_image, name='get_image'),
    path('original-img/<uuid:uuid>/', views.get_image, {"max_size":None}, name='get_original_image'),
    path('poll', views.PollImageView.as_view(), name='poll'),
    path('upload', views.UploadImagesView.as_view(), name='upload_images'),
    path('statistics', views.get_statistics, name="get_statistics"),
    path('download', views.DownloadView.as_view(), name='download_results'),
]


