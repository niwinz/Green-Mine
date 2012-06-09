#!/usr/bin/env python
import os, sys

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'extern'))
sys.path.insert(0, os.path.join(current_dir, 'extern', 'django-randomfilenamestorage'))

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
