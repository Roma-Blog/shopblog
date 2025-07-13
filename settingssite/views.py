from django.shortcuts import render
from wagtail.contrib.settings.registry import registry
from django.http import HttpResponse
from wagtail.models import Site
from .models import SiteDataSettings


def robots(request):
    current_site = Site.find_for_request(request)
    site_settings = SiteDataSettings.for_site(current_site)
    content = site_settings.robots if site_settings.robots else """
        User-agent: *
        Allow: /
        """
    
    return HttpResponse(content, content_type="text/plain")
