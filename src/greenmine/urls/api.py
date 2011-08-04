# -*- coding: utf-8 -*- 
from django.conf.urls.defaults import patterns, include, url

from greenmine.views.api import (
    ApiUserAdd, ApiUserView, ApiUserEdit,
    #ForgotPassword, 
    ApiLogin, ApiCreateProject,
)

urlpatterns = patterns('',
    #url(r'^user$', ApiUserView.as_view(), name='api-user-view'),
    #url(r'^user/add$', ApiUserAdd.as_view(), name='api-user-add'),
    #url(r'^user/edit$', ApiUserEdit.as_view(), name='api-user-edit'),
)

#urlpatterns += patterns()

urlpatterns += patterns('',
    #url(r'^request/password$', ForgotPassword.as_view(), name='api-request-password'),
    url(r'^login$', ApiLogin.as_view(), name='api-login'),
    url(r'^project/create$', ApiCreateProject.as_view(), name='api-progect-create'),
)

