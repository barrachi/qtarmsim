# -*- coding: utf-8 -*-

###########################################################################
#                                                                         #
#  This file is part of QtARMSim.                                         #
#                                                                         #
#  QtARMSim is free software: you can redistribute it and/or modify       #
#  it under the terms of the GNU General Public License as published by   #
#  the Free Software Foundation; either version 3 of the License, or      #
#  (at your option) any later version.                                    #
#                                                                         #
#  This program is distributed in the hope that it will be useful, but    #
#  WITHOUT ANY WARRANTY; without even the implied warranty of             #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU      #
#  General Public License for more details.                               #
#                                                                         #
###########################################################################

"""
 module_path has the correct module path depending on whether the application is
 frozen (by cx_freeze) or not.
"""

import os
import sys


if getattr(sys, 'frozen', False):
    my_path = os.path.dirname(__file__) 
    module_path = os.path.realpath(my_path[:my_path.index("library.zip")])
else:
    module_path = os.path.dirname(__file__)
