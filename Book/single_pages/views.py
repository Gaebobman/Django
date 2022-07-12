from django.shortcuts import render

# Single pages


def landing(request):
    return render(
        request,
        'single_pages/landing.html'
    )


def about_me(request):
    return render(
        request,
        'single_pages/about_me.html'
    )
