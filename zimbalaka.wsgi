# MUST TODO
# edit the following line before you copy this to /var/www
path = '/full/path/to/zimbalaka/'

activate_this = path + 'env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
if path not in sys.path:
    sys.path.insert(0, path)

from zimbalaka import app as application
