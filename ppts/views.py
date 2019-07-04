from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404

import matplotlib.pyplot as plt
import PIL, PIL.Image
import io

def index(request):
    graph_list = []
    
    #append names of graphs
    graph_list.append('samplegraph')
    graph_list.append('samplegraph')
    graph_list.append('samplegraph')
    
    #use list of graphs as context and render page
    context = {'graph_list': graph_list}
    return render(request, 'ppts/index.html', context)

def graphmanager(request, graphname):
    '''given the name of the graph, sends request to appropriate function'''
    graph_view = globals()['graph_' + graphname]
    return graph_view(request)
    #to be added: 404 error when there's no graph

def graph_samplegraph(request):
    # Construct the graph
    x = range(0, 20, 1)
    s = range(0,40,2)
    plt.plot(x, s)

    plt.xlabel('xlabel(X)')
    plt.ylabel('ylabel(Y)')
    plt.title('Sample Graph')
    
    fig = plt.gcf()
    return figureToHttp(fig)
    
def figureToHttp(figure):
    '''Stores a figure as bytes, and then returns an HttpResponse.'''
    buffer = io.BytesIO()
    canvas = figure.canvas
    canvas.draw()
    
    pilImage = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
    pilImage.save(buffer, "PNG")
    
    return HttpResponse(buffer.getvalue(), content_type="image/png")