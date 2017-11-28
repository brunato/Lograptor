# -*- coding: utf-8 -*-
"""
This module contain general info about lograptor package.
"""
#
# Copyright (C), 2011-2017, by SISSA - International School for Advanced Studies.
#
# This file is part of lograptor.
#
# Lograptor is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Lograptor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with lograptor; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# See the file 'LICENSE' in the root directory of the present
# distribution for more details.
#
# @Author Davide Brunato <brunato@sissa.it>
#
__author__ = "Davide Brunato"
__copyright__ = "Copyright 2011-2017, SISSA"
__license__ = "LGPLv2.1+"
__version__ = "1.2b1"
__maintainer__ = "Davide Brunato"
__email__ = "brunato@sissa.it"
__status__ = "Development"
__description__ = ("Command-line utility for processing log files. "
                   "Produces matching outputs, data and reports.")
LONG_DESCRIPTION = """
lograptor is a tool which provides a command-line interface for system logs processing.

Pattern matching's searches can be performed together with filtering
rules and scope delimitation options. Each run can produce data and
a report that can be easily sent by e-mail or saved into a file system
directory.
The program can parse logs written in RFC 3164 and RFC 5424 formats.
Lograptor requires Python >= 2.7, and is provided with a base configuration for a set
of well known applications. You can easily extend this set adding new applications
with specific pattern search rules.
"""
