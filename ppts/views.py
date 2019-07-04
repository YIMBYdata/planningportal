from django.shortcuts import render
from django.http import HttpResponse

import matplotlib.pyplot as plt
import PIL, PIL.Image
import io

def index(request):
    context = {}
    return render(request, 'ppts/index.html', context)

def samplegraph(request):
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
    '''Stores a figure as byes, and then returns an HttpResponse.'''
    buffer = io.BytesIO()
    canvas = figure.canvas
    canvas.draw()
    
    pilImage = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
    pilImage.save(buffer, "PNG")
    
    return HttpResponse(buffer.getvalue(), content_type="image/png")