from wowstats import views
from django.conf.urls import url

app_name = "wowstats"

urlpatterns = [
    url(r'^$', views.MainView.as_view(), name='main'),
    url(r'^callback/$', views._callback, name="callback"),
    # url(r'^$', views.CharactersView.as_view(), name='main'),
]
