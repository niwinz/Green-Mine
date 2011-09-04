#!/usr/bin/env python
import os, sys

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'extern'))
sys.path.insert(0, os.path.join(current_dir, 'extern', 'django-randomfilenamestorage'))
sys.path.insert(0, os.path.join(current_dir, 'extern', 'django-html5-forms')

from django.core.management import execute_manager
import settings.local as settings

if __name__ == "__main__":
    execute_manager(settings)

