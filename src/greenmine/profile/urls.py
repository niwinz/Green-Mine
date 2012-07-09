# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url

from . import views


urlpatterns = patterns('',
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
    url(r'^remember-password/$', views.RememberPasswordView.as_view(), name='remember-password'),
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^activate/(?P<token>[\d\w\-]+)/$',
        views.AccountActivation.as_view(), name='activate'),

    url(r'^profile/$', views.ProfileView.as_view(), name='profile'),

    url(r'^profile/password/change/$',
        views.PasswordChangeView.as_view(), name='profile-password'),

    url(r'^password/recovery/(?P<token>[\d\w\-]+)/$',
        views.PasswordRecoveryView.as_view(), name='password-recovery'),
)
