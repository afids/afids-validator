import sys
path = '/home/fidvalidator/'

if path not in sys.path:
    sys.path.append(path)

from controller import app as application
