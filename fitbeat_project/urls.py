from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^login/$', 'fitbeat_project.fitbeats.views.user_login'),
    (r'^logout/$', 'fitbeat_project.fitbeats.views.user_logout'),
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', 
     {'document_root': '/home/huddlej/fitbeats/media'}),
    (r'^', include('fitbeat_project.fitbeats.urls')),
)
