from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("hello! It's http response")

# Create your views here.
