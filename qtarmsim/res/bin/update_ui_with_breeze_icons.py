#!/usr/bin/env python3
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

import fnmatch
import os
import re
import sys
from shutil import copyfile

def svg_match(path, name):
    matches = []
    for root, dirnames, filenames in os.walk(path):  # @UnusedVariable dirnames
        for filename in fnmatch.filter(filenames, '{}.svg'.format(name)):
            matches.append(os.path.join(root, filename))
    matches.sort()
    return matches[-1] if matches else None

def main():
    if len(sys.argv) != 2:
        print("A Qt ui file must be provided")
        sys.exit(-1)
    current_iconset_theme = None
    current_svg_icon = None
    # <iconset theme="system-help">
    iconset_theme_re = re.compile('<iconset theme="([^"]+)">')
    # <normalon>:/themes/...</normalon>../../../../../../.designer/backup</iconset>
    normalon_re = re.compile("^(.*<normalon>)[^<]+(<.*)$")
    #/home/barrachi/datos/aplicaciones/pyqt/qtarmsim/qtarmsim/res/breeze/actions/24/debug-run.svg
    #svg_re = re.compile('.*breeze/([^/]+)/([0-9]+)/(.*)')
    svg_re = re.compile('.*breeze/(.*)')
    # Create backup file
    file_name = sys.argv[1]
    file_name_bak = "{}.bak".format(file_name)
    copyfile(file_name, file_name_bak)
    f = open(file_name_bak)
    d = open(file_name, 'w')
    ui_path = os.path.dirname(sys.argv[1])
    icon_path = os.path.abspath(os.path.join(ui_path, "..", "res", "breeze"))
    for line in f:
        line = line.rstrip()
        result_iconset_themem_re = iconset_theme_re.search(line)
        if result_iconset_themem_re:
            current_iconset_theme = result_iconset_themem_re.groups()[0]
            current_svg_icon = svg_match(icon_path, current_iconset_theme)
            d.write(line+'\n')
            continue
        if current_iconset_theme and current_svg_icon:
            result_normalon_re = normalon_re.search(line)
            if result_normalon_re:
                prefix, postfix = result_normalon_re.groups()
                result_svg_re = svg_re.search(current_svg_icon)
                if result_svg_re:
                    normalon = ':themes/breeze/{}'.format(result_svg_re.groups()[0])
                    d.write('{}{}{}\n'.format(prefix, normalon, postfix))
                    continue
        d.write(line+'\n')
    f.close()
    d.close()

if __name__ == "__main__":
    main()
