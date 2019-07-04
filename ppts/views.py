from django.shortcuts import render
from django.http import HttpResponse

import matplotlib.pyplot as plt
import PIL, PIL.Image
import io

def index(request):
    context = {}
    return render(request, 'ppts/index.html', context)

def getimage(request):
    # Construct the graph
    x = range(0, 20, 1)
    s = range(0,40,2)
    plt.plot(x, s)

    plt.xlabel('xlabel(X)')
    plt.ylabel('ylabel(Y)')
    plt.title('Simple Graph!')
    #plt.grid(True)
    
    buffer = io.BytesIO()
    canvas = plt.gca().figure.canvas
    #canvas = pylab.get_current_fig_manager().canvas
    canvas.draw()
    
    pilImage = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
    pilImage.save(buffer, "PNG")
    #pylab.close()
    
    return HttpResponse(buffer.getvalue(), content_type="image/png")