import sys
# path = '/home/fidvalidator' 
path = '/home/tkai/git/fidvalidator/home/fidvalidator'

if path not in sys.path:
    sys.path.append(path)

print("TEST")
from controller import app as application
