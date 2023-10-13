import datetime
from django.core.cache import cache
from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, status
from rest_framework.decorators import parser_classes
from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer
from core.helpers.rest_api import rest_default_response
from core.helpers.rest_api import StandardApplicationSetPagination
from django.db.models import Q, Max, Min
from app.settings import SIMPLE_JWT
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.dateparse import parse_date
import requests


token_prefix = SIMPLE_JWT['JWT_AUTH_HEADER_PREFIX'] + ' '
