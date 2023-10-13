from django.urls import path

from .views import CommonView, ApplicationRoleAPI, UserModulePermissionApi, AvailableDomainApi

MAIN_PATH = 'common'

urlpatterns = [
    path(MAIN_PATH, CommonView.as_view()),
    path(MAIN_PATH+'/application-roles', ApplicationRoleAPI.as_view(), name='application-roles'),
    path(MAIN_PATH + '/user-module-permissions/<user_id>', UserModulePermissionApi.as_view(),
         name='user-module-permissions'),
    path(MAIN_PATH + '/domains', AvailableDomainApi.as_view(), name='domains')

]
