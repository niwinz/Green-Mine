#!/usr/bin/env python
import os, sys

from django.core.management import execute_manager
import settings.local as settings

if __name__ == "__main__":
    execute_manager(settings)
