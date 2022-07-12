from django.shortcuts import render
from .models import Post
from django.views.generic import ListView
# CBV


# index() 와 동일한 역할
class PostList(ListView):
    model = Post
    ordering = '-pk'






# FBV
# def index(request):
#     posts = Post.objects.all().order_by('-pk')
#
#     return render(
#         request,
#         'blog/index.html',
#         {
#             'posts': posts,
#         }
#     )
#
#
def single_post_page(request, pk):
    post = Post.objects.get(pk=pk)

    return render(
        request,
        'blog/single_post_page.html',
        {
            'post': post,
        }
    )
