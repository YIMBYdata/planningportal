import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import PIL
import PIL.Image

from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from django.db.models import Count

from ppts.models import DwellingType
from ppts.models import LandUse
from ppts.models import Location
from ppts.models import Planner
from ppts.models import ProjectFeature
from ppts.models import ProjectDescription
from ppts.models import Record
from ppts.models import RecordType

def index(request):
    """Returns the ppts index page."""
    graph_list = []
    
    #append names of graphs
    graph_list.append('sample_1')
    graph_list.append('sample_2')
    
    #use list of graphs as context and render page
    context = {'graph_list': graph_list}
    return render(request, 'ppts/index.html', context)

def graphs_manager(request, graphname):
    """Generates the graph with the given name and returns an http response."""
    graph_func = globals()['graph_' + graphname]
    return figure_to_http(graph_func())
    #to be added: 404 error when there's no graph

def graph_sample_1():
    """A sample graph with a straight line."""
    fig, ax = plt.subplots()
    x = range(0, 20, 1)
    s = range(0, 40, 2)
    ax.plot(x, s)

    ax.set_xlabel('xlabel(X)')
    ax.set_ylabel('ylabel(Y)')
    ax.set_title('Sample Graph')
    
    return fig

def graph_sample_2():
    """A sample graph with a pie chart of PRJ statuses"""
    fig, ax = plt.subplots()
    
    projects = Record.objects.filter(record_type__pk='PRJ').values('status').annotate(
        status_counts=Count('pk'))
    status_counts = []
    status = []
    for item in projects:
        status.append(item['status'])
        status_counts.append(item['status_counts'])
    
    ax.pie(status_counts, labels=status)
    
    return fig
    
def figure_to_http(figure):
    """Stores a figure as bytes, and then returns an HttpResponse."""
    buffer = io.BytesIO()
    
    canvas = FigureCanvas(figure)
    canvas.draw()
    
    pil_image = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
    pil_image.save(buffer, "PNG")
    
    return HttpResponse(buffer.getvalue(), content_type="image/png")
