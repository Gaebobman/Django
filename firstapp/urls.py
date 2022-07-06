from django.urls import path
from firstapp import views

# path(''),     사용자가 홈으로 들어옴
# path('read/<id>/', views.read)    가변적으로 바뀌는 id 는 <> 안에 넣고 view.read의 두번째 인자에 id로 지정

urlpatterns = [
    path('', views.index),
    path('create/', views.create),
    path('read/<id>/', views.read),
    path('update/<id>/', views.update),
    path('delete/', views.delete)
]
