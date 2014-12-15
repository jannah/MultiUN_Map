# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="Hassan"
__date__ ="$Dec 12, 2014 9:27:21 PM$"


from app import app
from app import change_map_file
import sys

if __name__ == '__main__':
    print sys.argv
    if len(sys.argv)>1:
        change_map_file(sys.argv[1])
    app.run(debug=True)