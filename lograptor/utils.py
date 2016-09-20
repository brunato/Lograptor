# -*- coding: utf-8 -*-
"""
This module contains various utility functions for Lograptor.
"""
#
# Copyright (C), 2011-2016, by Davide Brunato and
# SISSA (Scuola Internazionale Superiore di Studi Avanzati).
#
# This file is part of Lograptor.
#
# Lograptor is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# See the file 'LICENSE' in the root directory of the present
# distribution or http://www.gnu.org/licenses/gpl-2.0.en.html.
#
# @Author Davide Brunato <brunato@sissa.it>
#
import sys
import os
import logging

from .tui import ProgressBar

GZIP_CHUNK_SIZE = 8192


def set_logger(name, loglevel=1, logfile=None):
    """
    Setup a basic logger with an handler and a formatter, using a
    corresponding numerical range [0..4], where a higher value means
    a more verbose logging. The loglevel value is mapped to correspondent
    logging module's value:

    LOG_CRIT=0 (syslog.h value is 2) ==> logging.CRITICAL
    LOG_ERR=1 (syslog.h value is 3) ==> logging.ERROR
    LOG_WARNING=2 (syslog.h value is 4) ==> logging.WARNING
    LOG_INFO=3 (syslog.h value is 6) ==> logging.INFO
    LOG_DEBUG=4 (syslog.h value is 7) ==> logging.DEBUG

    If a logfile name is passed then writes logs to file, instead of
    send logs to the standard output.

    :param name: logger name
    :param loglevel: Simplified POSIX's syslog like logging level index
    :param logfile: Logfile name for non-scripts runs
    """
    logger = logging.getLogger(name)
    print("name", name)

    # Higher or lesser argument values are also mapped to DEBUG or CRITICAL
    effective_level = max(logging.DEBUG, logging.CRITICAL - loglevel * 10)

    logger.setLevel(effective_level)

    # Add the first new handler
    if not logger.handlers:
        if logfile is None:
            lh = logging.StreamHandler()
        else:
            lh = logging.FileHandler(logfile)
        lh.setLevel(effective_level)

        if effective_level <= logging.DEBUG:
            formatter = logging.Formatter("[%(levelname)s:%(module)s:%(funcName)s: %(lineno)s] %(message)s")
        elif effective_level <= logging.INFO:
            formatter = logging.Formatter("[%(levelname)s:%(module)s] %(message)s")
        else:
            formatter = logging.Formatter("%(levelname)s: %(message)s")

        lh.setFormatter(formatter)
        logger.addHandler(lh)
    else:
        for handler in logger.handlers:
            handler.setLevel(effective_level)


def do_chunked_gzip(infh, outfh, filename):
    """
    A memory-friendly way of compressing the data.
    """
    import gzip

    gzfh = gzip.GzipFile('rawlogs', mode='wb', fileobj=outfh)

    if infh.closed:
        infh = open(infh.name, 'r')
        
    readsize = 0
    sys.stdout.write('Gzipping {0}: '.format(filename))

    infh.seek(0)
    progressbar = ProgressBar(sys.stdout, os.stat(infh.name).st_size, "bytes gzipped")
    while True:
        chunk = infh.read(GZIP_CHUNK_SIZE)
        if not chunk:
            break

        if sys.version_info[0] >= 3:
            # noinspection PyArgumentList
            gzfh.write(bytes(chunk, "utf-8"))
        else:
            gzfh.write(chunk)
            
        readsize += len(chunk)
        progressbar.redraw(readsize)

    gzfh.close()


def mail_smtp(smtpserv, fromaddr, toaddr, msg):
    """
    Send mail using smtp.
    """
    import smtplib

    server = smtplib.SMTP(smtpserv)
    server.sendmail(fromaddr, toaddr, msg)
    server.quit()


def mail_sendmail(sendmail, msg):
    """
    Send mail using sendmail.
    """
    p = os.popen(sendmail, 'w')
    p.write(msg)
    p.close()


def get_value_unit(value, unit, prefix):
    """
    Return a human-readable value with unit specification. Try to
    transform the unit prefix to the one passed as parameter. When
    transform to higher prefix apply nearest integer round. 
    """
    prefixes = ('', 'K', 'M', 'G', 'T')

    if len(unit):
        if unit[:1] in prefixes:
            valprefix = unit[0] 
            unit = unit[1:]
        else:
            valprefix = ''
    else:
        valprefix = ''
    
    while valprefix != prefix:
        uidx = prefixes.index(valprefix)

        if uidx > prefixes.index(prefix):
            value *= 1024
            valprefix = prefixes[uidx-1]
        else:
            if value < 10240:
                return value, '{0}{1}'.format(valprefix, unit)
            value = int(round(value/1024.0))
            valprefix = prefixes[uidx+1]
    return value, '{0}{1}'.format(valprefix, unit)


def htmlsafe(unsafe):
    """
    Escapes all x(ht)ml control characters.
    """
    unsafe = unsafe.replace('&', '&amp;')
    unsafe = unsafe.replace('<', '&lt;')
    unsafe = unsafe.replace('>', '&gt;')
    return unsafe


def get_fmt_results(resdict, limit=5, sep='::', fmt=None):
    """
    Return a list of formatttes strings representation on a result dictionary.
    The elements of the key are divided by a separator string. The result is
    appended after the key beetween parentheses. Apply a format transformation
    to odd elements of the key if a fmt parameter is passed.
    """
    reslist = []
    for key in sorted(resdict, key=lambda x: resdict[x], reverse=True):
        if len(reslist) >= limit and resdict[key] <= 1:
            break
        if fmt is not None:
            fmtkey = []
            for i in range(len(key)):
                if i % 2 == 1:
                    fmtkey.append(fmt.format(key[i]))
                else:
                    fmtkey.append(key[i])
            reslist.append(u'{0}({1})'.format(sep.join(fmtkey), resdict[key]))
        else:
            reslist.append(u'{0}({1})'.format(sep.join(key), resdict[key]))
    else:
        return reslist
    if fmt is not None:
        reslist.append(fmt.format(u'[%d more skipped]' % (len(resdict)-len(reslist))))
    else:
        reslist.append(u'[%d more skipped]' % (len(resdict)-len(reslist)))
    return reslist
