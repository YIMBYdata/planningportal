from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404

import matplotlib.pyplot as plt
import PIL, PIL.Image
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from ppts.models import DwellingType
from ppts.models import LandUse
from ppts.models import Location
from ppts.models import Planner
from ppts.models import ProjectFeature
from ppts.models import ProjectDescription
from ppts.models import Record
from ppts.models import RecordType
from django.db.models import Count

def index(request):
    graph_list = []
    
    #append names of graphs
    graph_list.append('samplegraph')
    graph_list.append('samplegraph2')
    graph_list.append('samplegraph')
    
    #use list of graphs as context and render page
    context = {'graph_list': graph_list}
    return render(request, 'ppts/index.html', context)

def graphmanager(request, graphname):
    '''given the name of the graph, sends request to appropriate function'''
    graph_func = globals()['graph_' + graphname]
    return figureToHttp(graph_func())
    #to be added: 404 error when there's no graph

def graph_samplegraph():
    # Construct the graph
    fig,ax = plt.subplots()
    x = range(0, 20, 1)
    s = range(0,40,2)
    ax.plot(x, s)

    ax.set_xlabel('xlabel(X)')
    ax.set_ylabel('ylabel(Y)')
    ax.set_title('Sample Graph')
    
    return fig

def graph_samplegraph2():
    #a basic graph that uses ppts data
    fig,ax = plt.subplots()
    
    projects = Record.objects.filter(record_type__pk = 'PRJ').values('status').annotate(status_counts = Count('pk'))
    status_counts = []
    status = []
    for item in projects:
        status.append(item['status'])
        status_counts.append(item['status_counts'])
    
    ax.pie(status_counts, labels=status)
    
    return fig
    
def figureToHttp(figure):
    '''Stores a figure as bytes, and then returns an HttpResponse.'''
    buffer = io.BytesIO()
    
    canvas=FigureCanvas(figure)
    #canvas = figure.canvas
    canvas.draw()
    
    pilImage = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
    pilImage.save(buffer, "PNG")
    
    return HttpResponse(buffer.getvalue(), content_type="image/png")