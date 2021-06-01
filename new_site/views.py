from django.shortcuts import render

# Create your views here.
def index(request):
    context = {"a": [1, 2, 3, 4]}
    
    return render(request, "new_site/index.html", context)
