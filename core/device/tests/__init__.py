from dateutil import parser
import json
import os

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.device.serializers import *
from core.helpers.helpers_tests import *
