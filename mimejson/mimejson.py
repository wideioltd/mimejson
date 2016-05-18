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
"""
MIMEJSON.

Mimejson a serializer/deserializer and transport for object containing large
objects.

It is designed to
   1. allow to transport multipart object across the web.
   2. to be extensible
   3. to rely on existing standards
   4. to be easy to implement in any language
"""

import errno
import imp
import json
import logging
import os
import os.path
import requests

JSON_ATOMS = (int, str, unicode, bool, float)

#
# utility functions
#


def _xmap(obj, fct, key=None):
    """
    Recursive map function to deep transform an object.

    :param object: the name of the object to be transformed
    :param fct: the function to be applied
    :param key: an indication for the function on the location of the object processed (FIXME: check needed)
    """
    if type(obj) in [list, dict, tuple]:
        if isinstance(obj, list):
            obj = [_xmap(item, fct) for item in obj]
        elif isinstance(obj, dict):
            obj = dict([
                (k[0], _xmap(v, fct, key=k))
                for k, v in obj.items()
            ])
        elif isinstance(obj, tuple):
            obj = tuple([_xmap(item, fct) for item in obj])
    return fct(obj, key=key)


def _mkdir_p(path):
    """
    Reproduce `mkdir -p` behaviour.

    :param path: path to be created
    :return: none
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class HTTPTransport(object):
    def __init__(self, server, user=None, password=None, session=None):
        """
        Creates a HTTP transport for mimejson.
        """
        self.url = server
        self.session = session or requests
        if user:
            self.kwargs = dict(auth=(user, password))
        else:
            self.kwargs = {}

    def send(self, files, data, url=None):
        """
        Send file to a remote location using the transport.

        :param: files to be sent
        :data: payload
        """
        target_url = self.url
        if url:
            target_url = url
        res = self.session.post(target_url, files=files, data=data, **self.kwargs)
        return json.loads(res.text)


class Serializers(object):
    instance = None

    def __init__(self):
        self.mime_codecs = {}

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = Serializers()

            cls.instance._load_codecs(os.path.join(os.path.dirname(os.path.realpath(__file__)), "mimetype"))

        return cls.instance

    def _load_codecs(self, folder):
        """
        Load every codec mimetype from mimetype folder.

        Codecs must be found in mimetype/codecs.py
        with an Serializer class
        """
        for f in os.listdir(folder):
            if os.path.isfile(f) and f.endswith("py") and not f.startswith("__init__"):
                try:
                    e = self._load_mimetype_module_file(os.path.join(folder, f), 'Serializer')
                    if e is not None:
                        self.register_codec(e)
                except:
                    logging.warning('mimejson: unable to load serialization module %r\n' % (f,))
            elif os.path.isdir(f) and os.path.exists(os.path.join(f, "__init__.py")):
                try:
                    e = self._load_mimetype_module_file(os.path.join(folder, f), 'Serializer')
                    if e is not None:
                        self.register_codec(e)
                except:
                    logging.warning('mimejson: unable to load serialization module %r\n' % (f,))

    def _load_mimetype_module_file(self, path, expected_class):
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
                self.mime_codecs[m] = codec
        else:
            self.mime_codecs[codec.mimetype] = codec

    def __getitem__(self, item):
        return self.mime_codecs[item]


class MIMEJSON(object):
    """
    Serializer/Deserializer for mimejson.

    FILE: This implementation is naive and uses a temporary storage for all the data that have to be transmitted
    TODO: make upload async and parallel
    """

    def __init__(self, server=None, user=None, password=None, basepath=None, use_tmp_storage=True, session=None):
        """
        Initialised the MIMEJSON serialiser.

        If no arguments given the deserialize will not send to the server.
        you can change those following variable after init.
        """
        self.data = None  # < currently opened json
        self.serializers = Serializers.get_instance()

        self.storage = os.getcwd()
        if use_tmp_storage:
            self.storage = os.path.join("/tmp", ".mjson-" + str(os.getpid()))

        if basepath:
            self.storage = basepath

        self.using_tmp_storage = use_tmp_storage

        self.session = session or requests
        self.transport = None

        self._objects = {}  # < temporaries (bad design to be removed)

        if server is not None and user is not None and password is not None:
            self.transport = HTTPTransport(server, user, password, session)

    def __mimejson_serialize_item(self, obj, key):
        ret = obj
        for mc in self.serializers.mime_codecs.items():
            can_apply = mc[1].can_apply
            if can_apply(obj):
                ret = mc[1].serialize(obj, self.storage)

                # store serialized file for future transmission
                if key is not None and '$path$' in ret:
                    c = self.serializers['file']
                    self._objects[key] = c.deserialize(ret, ret['$path$'])

        return ret

    def __mimejson_deserialize_item(self, obj, key):
        # for each obj of the dictionary, this fct is call
        if isinstance(obj, dict) and "$mimetype$" in obj:
            if (obj["$mimetype$"]) in self.serializers.mime_codecs:
                path = obj['$path$']
                f = None
                if path.startswith("http"):
                    f = self.session.get(obj['$path$']).content
                    path = f[0]

                obj = self.serializers.mime_codecs[obj["$mimetype$"]].deserialize(obj, path)

                if f is not None:
                    os.unlink(f[0])
            else:
                logging.warning("mimejson: unsupported mimetype: %s\n" % (obj['$mimetype$'],))
        return obj

    def _mimejson_serialize_object(self, obj):
        return _xmap(obj, self.__mimejson_serialize_item)

    def _mimejson_deserialize_object(self, obj):
        return _xmap(obj, self.__mimejson_deserialize_item)

    def _deserialize_all(self):
        """
        Deserialize jsondict $path$ (path/url) into object (from mimetype)
        need a mimejson dict loaded to work
        """
        self.data = self._mimejson_deserialize_object(self.data)

    def _serialize_all(self):
        """
        Serialize in self.pathdir and send toward server if loaded.
        need a mimejson dict loaded to work
        change self.pathdir to change the path of serialized files
        """
        self.data = self._mimejson_serialize_object(self.data)

    def _dump(self, data=None, send=True, url=None):
        """
        Serialize and object and push the serialize object to the server.

        :return: a mimejson object with reference to serialized elements
        """
        if data is not None:
            self.data = data

        self._serialize_all()
        return json.dumps(self.data)

    def push(self, data=None, url=None):
        self._dump()
        if not self.transport:
            raise ValueError("Not connected")
        data = {}
        for k in self.data:
            if type(self.data[k]) not in JSON_ATOMS:
                data[k] = json.dumps(self.data[k])  # ENSURE ALL DATA ARE COMPATBLE
            else:
                data[k] = self.data[k]

        result = self.transport.send(data=data, files=self._objects, url=url)

        for k in self._objects:
            self._objects[k].close()
        self._objects = {}
        return result

    def dumps(self, data, url=None):
        """
        Dump to a mimejson string WITHOUT transporting the data.
        """
        return self._dump(data=data)

    def load(self, uri):
        """
        Load object from url/path/file.
        """
        if os.path.isfile(uri):
            json_file = open(uri, 'r+')
            self.data = json.load(json_file)
            json_file.close()
        else:
            self.data = self.session.get(uri).json()

        self._deserialize_all()
        return self.data

    def loads(self, data):
        """
        Load object from string json.
        """
        self.data = json.loads(data)
        self._deserialize_all()
        return self.data

    def loadd(self, object_instance):
        """
        Load object from dict.
        """
        self.data = object_instance
        self._deserialize_all()
        return self.data

    def __enter__(self):
        if os.path.exists(self.storage) and self.using_tmp_storage:
            errmsg = """
            temporary folder %s must be a non existent folder as it will be deleted after completion of the program
            """ % (self.storage,)
            raise Exception(errmsg)

        if not os.path.exists(self.storage):
            _mkdir_p(self.storage)
        return self

    def __exit__(self, *_args):
        if self.using_tmp_storage:
            for f in os.listdir(self.storage):
                os.unlink(os.path.join(self.storage, f))
            os.rmdir(self.storage)
