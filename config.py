import os
import sys
sys.path.insert(0, '/workspace/agreement_verification')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()
