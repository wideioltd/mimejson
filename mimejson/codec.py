#!/usr/bin/env python2
# ############################################################################
# |W|I|D|E|I|O|L|T|D|W|I|D|E|I|O|L|T|D|W|I|D|E|I|O|L|T|D|W|I|D|E|I|O|L|T|D|
# Copyright (c) WIDE IO LTD 2014-2016
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the WIDE IO LTD nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
# |D|O|N|O|T|R|E|M|O|V|E|!|D|O|N|O|T|R|E|M|O|V|E|!|D|O|N|O|T|R|E|M|O|V|E|!|
# ############################################################################
import imp
import logging
import os


class CodecRegister(object):

    """
    Register identifying CODECs that MIMEJSON may use.
    """

    instance = None

    def __init__(self):
        """
        Initialize CODEC register.
        """
        self.all_codecs = {}

    @classmethod
    def get_instance(cls):
        """
        Return the shared instance of the Codec Register.

        :return: the shared instanced of the codec register.
        """
        if cls.instance is None:
            cls.instance = CodecRegister()
            paths = [
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "mimetype")
            ]
            for p in paths:
                print(p)
                cls.instance._load_codecs_from_directory(p)

        return cls.instance

    def _load_codecs_from_directory(self, path):
        """
        Load every codec mimetype from mimetype folder.

        Codecs must be found in mimetype/codecs.py
        with an Serializer class
        """
        for f in os.listdir(path):
            af = os.path.join(path, f)
            if os.path.isdir(af) and os.path.exists(os.path.join(af, "__init__.py")):
                try:
                    e = self._load_codec_module(af, 'Serializer')
                    if e is not None:
                        self.register_codec(e)
                except:
                    logging.warning('mimejson: unable to load serialization module %r\n' % (af,))
            elif f.endswith("py") and not f.startswith("__init__"):
                try:
                    e = self._load_codec_module(af, 'Serializer')
                    if e is not None:
                        self.register_codec(e)
                except:
                    logging.warning('mimejson: unable to load serialization module %r\n' % (af,))

    def _load_codec_module(self, path, expected_class):
        """
        Return and load expected_class from path file.
        """
        if os.path.isfile(path):
            mod_name, file_ext = os.path.splitext(os.path.basename(path))
            if file_ext.lower() == '.py':
                py_mod = imp.load_source(mod_name, path)
            elif file_ext.lower() == '.pyc':
                py_mod = imp.load_compiled(mod_name, path)
        else:
            mod_name = os.path.basename(path)
            py_mod = imp.load_package(mod_name, path)

        if hasattr(py_mod, expected_class):
            return getattr(py_mod, expected_class)()
        return None

    def register_codec(self, codec):
        """
        Add codec to the list of register codecs.

        mimetype can be string or tuple of string.
        """
        if isinstance(codec.mimetype, tuple):
            for m in codec.mimetype:
                self.all_codecs[m] = codec
        else:
            self.all_codecs[codec.mimetype] = codec

    def __getitem__(self, item):
        return self.all_codecs[item]
