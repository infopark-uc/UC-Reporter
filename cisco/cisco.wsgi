import sys
if sys.version_info[0]<3:       # require python3
 raise Exception("Python3 required! Current (wrong) version: '%s'" % sys.version_info)
sys.path.insert(0, '/var/www/html/cisco/')
from cisco import app as application

