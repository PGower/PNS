from django.shortcuts import render


def dashboard_page(request):
    return render(request, 'dashboard.html.j2', {})

def realtime_updates_page(request):
    return render(request, 'realtime.html.j2', {})
