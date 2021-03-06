import pickle
import random
import subprocess
import signal
from xml.dom.minidom import parse
from django import newforms as forms
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from fitbeat_project.fitbeats.models import *
from fitbeat_project.fitbeats.widgets import TextHiddenInput
import evolve_beats

COORDINATE_TRAJECTORY_NAMES = ('Initial', 'Control Point 1', 'Control Point 2', 'Final')
STATFILE = "/home/huddlej/fitbeats/testData.txt"
STOPFILE = "/home/huddlej/fitbeats/stopfile.txt"

def index(request):
    try:
        del(request.session['piece'])
    except(KeyError):
        pass

    if request.user.is_authenticated():
        currentUser = True
    else:
        currentUser = False
    title = "Rhythm Research"
    return render_to_response('fitbeats/index.html', {'title': title, 'currentUser': currentUser})

def user_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')

    errorMessage = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            errorMessage = "Login failed"
    title = "Login"
    return render_to_response('fitbeats/login.html', {'title': title, 'errorMessage': errorMessage})

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')
    
def add_pattern(request):
    #fields = ('length', 'instruments', 'selector', 'crossover', 'mutators')
    PatternForm = forms.form_for_model(Pattern)
    
    if request.method == "POST":
        data = request.POST
    else:
        data = None

    form = PatternForm(data)
    if form.is_valid():
        pattern = Pattern(length=form.cleaned_data['length'],
                          selector=form.cleaned_data['selector'],
                          crossover=form.cleaned_data['crossover'],
                          author=request.user)
        pattern.save()
        pattern.instruments = form.cleaned_data['instruments']
        pattern.mutators = form.cleaned_data['mutators']
        pattern.save()
        
        #mutators=form.cleaned_data['mutators'],
        return HttpResponseRedirect(pattern.get_absolute_url())

    title = heading = "Add Pattern"
    context = {'title': title, 'heading': heading, 'form': form}
    
    return render_to_response('fitbeats/edit_pattern.html',
                              context,
                              context_instance=RequestContext(request))
add_pattern = login_required(add_pattern)

def edit_pattern(request, id):
    fields = ('length', 'instruments', 'selector', 'crossover', 'mutators')
    pattern = get_object_or_404(Pattern, pk=id, author__pk=request.user.id)
    PatternForm = forms.form_for_instance(pattern)

    if request.method == "POST":
        form = PatternForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(pattern.get_absolute_url())
    else:
        form = PatternForm()
    
    title = heading = "Edit Pattern"
    context = {'title': title, 
               'heading': heading,
               'form': form,
               'pattern': pattern}
    
    return render_to_response('fitbeats/edit_pattern.html',
                              context,
                              context_instance=RequestContext(request))
edit_pattern = login_required(edit_pattern)

def view_trajectories(request, pattern_id):
    pattern = get_object_or_404(Pattern, pk=pattern_id, author__pk=request.user.id)
    trajectories = pattern.fitnesstrajectory_set.all()
    title = heading = "View Trajectories"
    context = {'title': title, 
               'heading': heading,
               'pattern': pattern,
               'trajectory_types': TRAJECTORY_TYPES,
               'trajectories': trajectories}
    return render_to_response('fitbeats/view_trajectories.html',
                              context,
                              context_instance=RequestContext(request))
view_trajectories = login_required(view_trajectories)

@transaction.commit_manually
def add_trajectory(request, pattern_id, trajectory_type):
    pattern = get_object_or_404(Pattern, pk=pattern_id, author__pk=request.user.id)
    value_forms = []

    if request.method == "POST":
        data = request.POST
    else:
        data = None

    functions = FitnessFunction.objects.filter(trajectory_type=trajectory_type)
    functions = tuple([(function.id, str(function)) for function in functions])

    TrajectoryForm = forms.form_for_model(FitnessTrajectory)
    TrajectoryForm.base_fields['function'].widget = forms.widgets.Select(choices=functions)
    TrajectoryValueForm = eval("forms.form_for_model(FitnessTrajectory%s)" % trajectory_type.capitalize())

    if trajectory_type == "coordinate":
        form_count = 4
        for i in xrange(0, form_count):
            TrajectoryValueForm.base_fields['sequence_number'].widget = TextHiddenInput(attrs={'value': i,
                                                                                               'display': COORDINATE_TRAJECTORY_NAMES[i]})

            value_forms.append(TrajectoryValueForm(data, prefix=str(i)))
    else:
        value_id = 1
        for instrument in pattern.instruments.all().order_by('sequence_number'):            
            TrajectoryValueForm.base_fields['instrument'].widget = TextHiddenInput(attrs={'value': instrument.id,
                                                                                          'display': instrument.name})
            value_forms.append(TrajectoryValueForm(data, prefix=str(value_id)))
            value_id += 1

    form = TrajectoryForm(data)
        
    if form.is_valid():
        # Add trajectory
        trajectory = FitnessTrajectory(pattern=pattern,
                                       function=form.cleaned_data['function'],
                                       trajectory_type=trajectory_type)
        trajectory.save()
        
        # Add values
        errors = []
        valid_value_forms_count = 0
        for f in value_forms:
            if f.is_valid():
                valid_value_forms_count += 1
                value = f.save()
                value.trajectory = trajectory
                value.save()
            else:
                errors.append(f.errors)
        # Only commit changes if at least one of the value forms validated
        if valid_value_forms_count > 0:
            transaction.commit()
            return HttpResponseRedirect(trajectory.get_absolute_url())
        else:
            transaction.rollback()

    trajectory_types = dict(TRAJECTORY_TYPES)
    title = heading = "Add %s Trajectory" % trajectory_types[trajectory_type]
    context = {'title': title, 
               'heading': heading,
               'pattern': pattern,
               'trajectory_type': trajectory_type,
               'trajectory_types': TRAJECTORY_TYPES,
               'form': form,
               'value_forms': value_forms,
               }
    return render_to_response('fitbeats/edit_trajectory.html',
                              context,
                              context_instance=RequestContext(request))
add_trajectory = login_required(add_trajectory)
add_trajectory = transaction.commit_manually(add_trajectory)

def edit_trajectory(request, pattern_id, id):
    pattern = get_object_or_404(Pattern, pk=pattern_id, author__pk=request.user.id)
    value_forms = []

    if request.method == "POST":
        data = request.POST
    else:
        data = None

    trajectory = get_object_or_404(FitnessTrajectory, pk=id, pattern__pk=pattern_id)
    trajectory_type = trajectory.trajectory_type
    functions = FitnessFunction.objects.filter(trajectory_type=trajectory_type)
    functions = tuple([(function.id, str(function)) for function in functions])

    TrajectoryForm = forms.form_for_instance(trajectory)
    TrajectoryForm.base_fields['function'].widget = forms.widgets.Select(choices=functions)
    
    #trajectory_values = eval("trajectory.fitnesstrajectory%s_set.all()" % trajectory_type)
    trajectory_values = trajectory.trajectory_set
    value_id = 1
    for v in trajectory_values:
        TrajectoryValueForm = forms.form_for_instance(v)
        
        if trajectory_type == "coordinate":
            TrajectoryValueForm.base_fields['sequence_number'].widget = TextHiddenInput(attrs={'value': v.sequence_number,
                                                                                               'display': COORDINATE_TRAJECTORY_NAMES[v.sequence_number]})
        else:
            TrajectoryValueForm.base_fields['instrument'].widget = TextHiddenInput(attrs={'value': v.instrument.id,
                                                                                          'display': v.instrument.name})

        value_forms.append(TrajectoryValueForm(data, prefix=str(value_id)))
        value_id += 1

    form = TrajectoryForm(data)
        
    if form.is_valid():
        # Update trajectory
        form.save()
        
        # Update values
        errors = []
        valid_value_forms_count = 0
        for f in value_forms:
            if f.is_valid():
                valid_value_forms_count += 1
                value = f.save()
            else:
                errors.append(f.errors)

        # Only commit changes if at least one of the value forms validated
        if valid_value_forms_count > 0:
            transaction.commit()
            return HttpResponseRedirect(trajectory.get_absolute_url())
        else:
            transaction.rollback()
            raise Exception(errors)

    trajectory_types = dict(TRAJECTORY_TYPES)
    title = heading = "Edit %s Trajectory" % trajectory_types[trajectory_type]
    context = {'title': title, 
               'heading': heading,
               'pattern': pattern,
               'trajectory': trajectory,
               'trajectory_type': trajectory_type,
               'trajectory_types': TRAJECTORY_TYPES,
               'form': form,
               'value_forms': value_forms,
               }
    return render_to_response('fitbeats/edit_trajectory.html',
                              context,
                              context_instance=RequestContext(request))
edit_trajectory = login_required(edit_trajectory)
edit_trajectory = transaction.commit_manually(edit_trajectory)

def delete_trajectory(request, pattern_id, id):
    pattern = get_object_or_404(Pattern, pk=pattern_id, author__pk=request.user.id)
    trajectory = get_object_or_404(FitnessTrajectory, pk=id, pattern__pk=pattern_id)
    trajectory.delete()
    return HttpResponseRedirect("%strajectories/" % pattern.get_absolute_url())
delete_trajectory = login_required(delete_trajectory)

def edit_parameters(request, pattern_id):
    pattern = get_object_or_404(Pattern, pk=pattern_id, author__pk=request.user.id)

    if request.method == "POST":
        data = request.POST
    else:
        data = None
    
    parameters = pattern.parameters.all().order_by('name')
    parameter_forms = []
    value_id = 1
    errors = []
    valid_form_count = 0

    for parameter in parameters:
        # population_max_generations -> Population Max Generations
        label_name = " ".join([s.capitalize() for s in parameter.name.split("_")])
    
        ParameterForm = forms.form_for_instance(parameter)
        ParameterForm.base_fields['value'].label = label_name
        f = ParameterForm(data, prefix=str(value_id))
        parameter_forms.append(f)
        value_id += 1

        if data is not None:
            if f.is_valid():
                valid_form_count += 1
                value = f.save()
            else:
                errors.append(f.errors)

    if data is not None:
        # Only commit changes if at least one of the value forms validated
        if valid_form_count > 0:
            transaction.commit()
            return HttpResponseRedirect("%sparameters/" % pattern.get_absolute_url())
        else:
            transaction.rollback()
            raise Exception("Could not save all parameters: %s" % ", ".join(errors))

    title = heading = "Edit Parameters"
    context = {'title': title, 
               'heading': heading,
               'pattern': pattern,
               'parameter_forms': parameter_forms,
               }
    return render_to_response('fitbeats/edit_parameters.html',
                              context,
                              context_instance=RequestContext(request))
edit_parameters = login_required(edit_parameters)
edit_parameters = transaction.commit_manually(edit_parameters)

@login_required
def evolve_pattern(request, pattern_id):
    pattern = get_object_or_404(Pattern, pk=pattern_id, author__pk=request.user.id)
    
    # Clear the existing data
    fhandle = open(STATFILE, "w")
    fhandle.close()
    
    fhandle = open(STOPFILE, "w")
    fhandle.close()
    
    title = heading = "Evolve Pattern"
    context = {'title': title,
               'heading': heading,
               'pattern': pattern,
               }
    return render_to_response('fitbeats/evolve.html',
                              context,
                              context_instance=RequestContext(request))

@login_required
def evolve_pattern_display(request, pattern_id):
    pattern = get_object_or_404(Pattern, pk=pattern_id, author__pk=request.user.id)
    pattern_instances = pattern.patterninstance_set.all()
    instruments = pattern.instruments.order_by('sequence_number')
    instruments = [[instrument.name] for instrument in instruments]

    try:
        fhandle = open(STATFILE, "r")
        data = pickle.load(fhandle)
        fhandle.close()

        if isinstance(data, dict) and data.has_key('is_done'):
            is_done = data['is_done']
            fitness = data['bestfitness']
            population_fitness = data['popfitness']
            diversity = data['diversity']
            best_pattern = data['best_pattern']    
            best_pattern = best_pattern.genes.tolist()
            
            for i in xrange(len(instruments)):
                instruments[i].extend(best_pattern[i])
            best_pattern = instruments
            generation = data['generation']
        else:
            raise Exception
    except:
        best_pattern = []
        is_done = False
        fitness = None
        population_fitness = None
        diversity = None
        generation = 0
    
    title = heading = "Best Pattern"
    context = {'pattern': pattern,
               'pattern_instances': pattern_instances,
               'best_pattern': best_pattern,
               'is_done': is_done,
               'fitness': fitness,
               'population_fitness': population_fitness,
               'diversity': diversity,
               'generation': generation
               }
    return render_to_response('fitbeats/evolve_pattern_results.html',
                              context,
                              context_instance=RequestContext(request))

@login_required
def evolve_pattern_run(request, pattern_id):
    pattern = get_object_or_404(Pattern, pk=pattern_id, author__pk=request.user.id)    
    request.session[str(pattern_id)] = subprocess.Popen(["python", 
                                                         "/home/huddlej/fitbeats/evolve_beats.py",
                                                         "-d",
                                                         str(pattern_id)]).pid
    return HttpResponse("Finished evolving pattern %s." % pattern)

@login_required
def evolve_pattern_stop(request, pattern_id):
    pattern = get_object_or_404(Pattern, pk=pattern_id, author__pk=request.user.id)
    
    stop = True
    fhandle = open(STOPFILE, "w")
    pickle.dump(stop, fhandle)
    fhandle.close()

    return HttpResponseRedirect("%sevolve/display/" % pattern.get_absolute_url())
    
@login_required
def view_pattern_instance(request, instance_id):
    instance = get_object_or_404(PatternInstance, pk=instance_id)
    response = HttpResponse(mimetype="text/xml")
    response['Content-Disposition'] = 'attachment; filename=yoursong.h2song'
    response.write(instance.value)
    
    return response

def xml_trajectory(request, pattern_id, id):
    bezFilename = "/home/huddlej/fitbeats/media/xmltest.xml"
    pattern = get_object_or_404(Pattern, pk=pattern_id, author__pk=request.user.id)
    trajectory = get_object_or_404(FitnessTrajectory, pk=id, pattern__pk=pattern_id)

    pattern.length = pattern.length
    trajectory_set = trajectory.trajectory_set

    rowMax = 150
    xScale = 280 / pattern.length
    yScale = 10
    
    x1 = trajectory_set[0].x
    y1 = rowMax - (trajectory_set[0].y * yScale)
    
    cx1 = trajectory_set[1].x * xScale
    cy1 = rowMax - (trajectory_set[1].y * yScale)

    cx2 = trajectory_set[2].x * xScale
    cy2 = rowMax - (trajectory_set[2].y * yScale)

    x2 = trajectory_set[3].x * xScale
    y2 = rowMax - (trajectory_set[3].y * yScale)

    bez = parse(bezFilename)
    bezsh = bez.getElementsByTagName("shape")[0]
    
    vals = ["x1", "y1", "x2", "y2", "cx1", "cy1", "cx2", "cy2"]
    
    for val in vals:
        bezsh.setAttribute(val, str(eval(val)))

    #print bez.toxml()
    bezFile = open(bezFilename, "w")
    bez.writexml(bezFile)
    bezFile.close()
    return HttpResponseRedirect('/site_media/xmltest.xml')
    return HttpResponseRedirect('/xml/')
