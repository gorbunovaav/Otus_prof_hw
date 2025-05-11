from django.shortcuts import render
from django.http import HttpResponse, Http404
from .models import Post

# def home(request):
#     return HttpResponse("hello! It's blog")

def post_list(request):
    posts = Post.published.all()
    return render(request,
                    'blog/post/list.html',
                    {'posts' : posts})

def post_detail(request, id):
    try:
        post = Post.published.get(id=id)
    except Post.DoesNotExist:
        raise Http404
    
    return render(request,
                    'blog/post/detail.html',
                    {'post' : post})