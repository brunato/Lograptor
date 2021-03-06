#
# Copyright (C), 2011-2020, by SISSA - International School for Advanced Studies.
#
# This file is part of lograptor.
#
# Lograptor is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# file 'LICENSE' in the root directory of the present distribution
# for more details.
#
# @Author Davide Brunato <brunato@sissa.it>
#
import io
import pytest
import sys
import os
import gzip
import tempfile

from lograptor.utils import do_chunked_gzip, get_value_unit, get_fmt_results, \
    htmlsafe, safe_expand, results_to_string, protected_property, normalize_path, \
    open_resource, is_redirected


class TestUtils(object):
    def setup_method(self, method):
        print("\n%s:%s" % (type(self).__name__, method.__name__))

    def test_do_chunked_gzip_with_io(self, capsys):
        infh = io.StringIO('Sample content')
        outfh = io.BytesIO()

        assert do_chunked_gzip(infh, outfh, filename='sample.txt.gz') is None
        out, err = capsys.readouterr()
        assert out.startswith("Gzipping sample.txt.gz:")
        assert out.endswith("14 bytes gzipped\n")
        assert err == ''
        assert outfh.getvalue() != b'Sample content'
        assert gzip.decompress(outfh.getvalue()) == b'Sample content'

        infh = io.StringIO('Sample content 2')
        infh.close()
        outfh = io.BytesIO()

        with pytest.raises(ValueError) as exc_info:
            do_chunked_gzip(infh, outfh, filename='sample2.txt.gz')

        assert exc_info.value.args[0] == 'I/O operation on closed file'

    def test_do_chunked_gzip_with_system_file(self, capsys):
        infh = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        infh.write('Sample content')
        infh.close()

        outfh = tempfile.NamedTemporaryFile(mode='wb+', delete=True)

        assert do_chunked_gzip(infh, outfh, filename='sample.txt.gz') is None
        out, err = capsys.readouterr()
        os.unlink(infh.name)

        assert out.startswith("Gzipping sample.txt.gz:")
        assert out.endswith("14 bytes gzipped\n")
        assert err == ''
        outfh.seek(0)
        gzipped_data = outfh.read()
        assert gzipped_data != b'Sample content'
        assert gzip.decompress(gzipped_data) == b'Sample content'

    def test_get_value_unit(self):
        assert get_value_unit(1000) == (1000, '')
        assert get_value_unit(1000, 'TB') == (1000, 'TB')
        assert get_value_unit(10, 'PB') == (10000, 'TB')
        assert get_value_unit(10 ** 4, 'GB') == (10, 'TB')
        assert get_value_unit(10 ** 4, 'MB') == (10, 'GB')
        assert get_value_unit(10 ** 7, 'MB') == (10, 'TB')
        assert get_value_unit(10 ** 7, 'MB') == (10, 'TB')
        assert get_value_unit(10 ** 10, 'MB') == (10000, 'TB')
        assert get_value_unit(10 ** 7, 'MB', 'G') == (10000, 'GB')

        assert get_value_unit(1024 ** 3, 'MiB', 'G') == (1024 ** 2, 'GiB')
        assert get_value_unit(1024 ** 3, 'PiB', 'G') == (1024 ** 5, 'GiB')
        assert get_value_unit(1024 ** 3, 'PiB', 'Mi') == (1024 ** 6, 'MiB')
        assert get_value_unit(1000 ** 3, 'PB', 'Gi') == (1000 ** 5, 'GB')

        assert get_value_unit(1000 ** 6, 'B', 'G') == (1000 ** 3, 'GB')
        assert get_value_unit(1024 ** 6, 'B', 'Gi') == (1024 ** 3, 'GiB')

        with pytest.raises(ValueError) as exc_info:
            get_value_unit(1024 ** 3, 'MiX')
        assert exc_info.value.args[0] == "unknown measure unit 'X'"

        with pytest.raises(ValueError) as exc_info:
            get_value_unit(1024 ** 3, 'MiB', 'X')
        assert exc_info.value.args[0] == "unknown metric prefix 'X'"

    def test_htmlsafe(self):
        assert htmlsafe('ab<&;cd>') == 'ab&lt;&amp;;cd&gt;'

    def test_get_fmt_results(self):
        fmt = '<font color="darkred">{0}</font>'
        results = {
            ('raptor', '192.168.0.1'): 2,
            ('rex', '192.168.0.4'): 1,
            ('dino', '192.168.0.2'): 3,
        }
        assert get_fmt_results(results) == [
            'dino::192.168.0.2(3)', 'raptor::192.168.0.1(2)', 'rex::192.168.0.4(1)'
        ]
        assert get_fmt_results(results, sep=', ') == [
            'dino, 192.168.0.2(3)', 'raptor, 192.168.0.1(2)', 'rex, 192.168.0.4(1)'
        ]
        assert get_fmt_results(results, limit=2) == [
            'dino::192.168.0.2(3)', 'raptor::192.168.0.1(2)', '[1 more skipped]'
        ]
        assert get_fmt_results(results, limit=2, fmt=fmt) == [
            'dino::<font color="darkred">192.168.0.2</font>(3)',
            'raptor::<font color="darkred">192.168.0.1</font>(2)',
            '<font color="darkred">[1 more skipped]</font>',
        ]

    def test_safe_expand(self):
        tmpl = '(|${ALPHA})'

        substitution_map = {'ALPHA': 'foo'}
        assert safe_expand(tmpl, substitution_map) == '(|foo)'

        substitution_map = {'ALPHA': '${BETA}', 'BETA': 'bar'}
        assert safe_expand(tmpl, substitution_map) == '(|bar)'

        substitution_map = {'ALPHA': '${BETA}', 'BETA': '${ALPHA}'}
        with pytest.raises(ValueError) as exc_info:
            safe_expand(tmpl, substitution_map)
        assert exc_info.value.args[0] == "substitution map has a circularity!"

    def test_results_to_string(self):
        results = {
            ('raptor', '192.168.0.1'): 2,
            ('rex', '192.168.0.4'): 1,
            ('dino', '192.168.0.2'): 3,
        }
        assert results_to_string(results) == \
            "('dino', '192.168.0.2')(3), ('raptor', '192.168.0.1')(2), ('rex', '192.168.0.4')(1)"

    def test_protected_property(self):
        def _foo(): pass

        with pytest.raises(ValueError) as exc_info:
            protected_property(_foo)
        assert "cannot decorate a protected method!" in exc_info.value.args[0]

    def test_normalize_path(self):
        base_path = '/opt'
        assert normalize_path('/home') == '/home'
        assert normalize_path('/home', base_path) == '/home'
        assert normalize_path('other/foo') == 'other/foo'
        assert normalize_path('other/foo', base_path) == '/opt/other/foo'
        assert normalize_path('./other/foo') == './other/foo'
        assert normalize_path('./other/foo', base_path) == '/opt/other/foo'
        assert normalize_path('~/foo') == '%s/foo' % os.path.expanduser('~')
        assert normalize_path('~/foo', base_path) == '%s/foo' % os.path.expanduser('~')

    def test_open_resource(self):
        res = open_resource("samples/postfix.log")
        assert res.name == "samples/postfix.log"

        res = open_resource(open("samples/dovecot.log"))
        assert res.name == "samples/dovecot.log"

        res = open_resource("file:samples/postfix.log")
        assert res.name == "file://samples/postfix.log"

        with pytest.raises((OSError, IOError)):
            open_resource("samples/nofile.log")

        with pytest.raises(TypeError):
            open_resource(["samples/postfix.log"])

    def test_is_redirected(self):
        try:
            STDIN_FILENO = sys.stdin.fileno()
        except ValueError:
            STDIN_FILENO = 0
        assert is_redirected(STDIN_FILENO) is False
