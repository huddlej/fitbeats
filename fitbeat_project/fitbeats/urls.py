from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list
import fitbeats
from fitbeats.models import Pattern

base_generic_dict = {'paginate_by': 20}
    
pattern_info_dict = dict(base_generic_dict,
                         queryset=Pattern.objects.all(),
                         template_object_name='pattern',
                         extra_context={'title': "View Patterns",
                                        'heading': "View Patterns",})

urlpatterns = patterns('',
    url(r'^patterns/$', object_list, pattern_info_dict, name='view_patterns'),
    url(r'^patterns/add/$', 'fitbeats.views.add_pattern', name='add_pattern'),
    (r'^patterns/(\d+)/$', 'fitbeats.views.edit_pattern'),

    # Trajectories
    (r'^patterns/(\d+)/trajectories/$', 'fitbeats.views.view_trajectories'),
    url(r'^patterns/(\d+)/trajectories/add/(\w+)/$', 'fitbeats.views.add_trajectory', name='add_trajectory'),
    url(r'^patterns/(\d+)/trajectories/(\d+)/$', 'fitbeats.views.edit_trajectory', name='edit_trajectory'),
    url(r'^patterns/(\d+)/trajectories/delete/(\d+)/$', 'fitbeats.views.delete_trajectory', name='delete_trajectory'),
    (r'^patterns/(\d+)/trajectories/(\d+)/xml/$', 'fitbeats.views.xml_trajectory'),

    # Parameters
    url(r'^patterns/(\d+)/parameters/$', 'fitbeats.views.edit_parameters', name='edit_parameters'),

    # Evolution
    (r'^patterns/(\d+)/evolve/$', 'fitbeats.views.evolve_pattern'),
    (r'^patterns/(\d+)/evolve/run/$', 'fitbeats.views.evolve_pattern_run'),
    (r'^patterns/(\d+)/evolve/display/$', 'fitbeats.views.evolve_pattern_display'),
    (r'^patterns/(\d+)/evolve/stop/$', 'fitbeats.views.evolve_pattern_stop'),
    (r'^patterns/instances/(\d+)/$', 'fitbeats.views.view_pattern_instance'),
    (r'^$', 'fitbeats.views.index'),
)
