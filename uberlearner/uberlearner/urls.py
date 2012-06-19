from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', direct_to_template, {'template': 'under-construction.html'}, 'home'),
    (r'^about/$', direct_to_template, {'template': 'about.html'}, 'about'),
    (r'^contact/$', direct_to_template, {'template': 'under-construction.html'}, 'contact'),
    url(r'^account/', include('accounts.urls'), name="account"),
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
