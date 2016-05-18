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
import json
import logging
import os
import os.path
import requests

from .codec import CodecRegister

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

    """
    Responsible for storing data/pulling on servers after serialization/deserialization.
    """

    def __init__(self, server, user=None, password=None, session=None):
        """
        Create a HTTP transport for MIMEJSON.
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


class MIMEJSON(object):

    """
    MIMEJSON Serialization Manager.

    FILE: This implementation is naive and uses a temporary storage for all the data that have to be transmitted
    TODO: make upload async and parallel
    """

    def __init__(self, server=None, user=None, password=None, basepath=None, use_tmp_storage=True, session=None):
        """
        Initialise the MIMEJSON serialiser.

        If no arguments given the decode will not send to the server.
        you can change those following variable after init.
        """
        self.codecs = CodecRegister.get_instance()

        self.storage = os.getcwd()
        self.using_tmp_storage = use_tmp_storage
        if use_tmp_storage:
            self.storage = os.path.join("/tmp", ".mjson-" + str(os.getpid()))

        if basepath:
            self.storage = basepath

        self.session = session or requests
        self.transport = None

        self._objects = {}  # < temporaries (bad design to be removed)

        if server is not None and user is not None and password is not None:
            self.transport = HTTPTransport(server, user, password, session)

    def __mimejson_encode_item(self, obj, key):
        ret = obj
        for mc in self.codecs._register.items():
            can_apply = mc[1].can_apply
            if can_apply(obj):
                ret = mc[1].encode(obj, self.storage)

                # store encoded file for future transmission
                if key is not None and '$path$' in ret:
                    c = self.codecs['file']
                    self._objects[key] = c.decode(ret, ret['$path$'])

        return ret

    def __mimejson_decode_item(self, obj, key):
        # for each obj of the dictionary, this fct is call
        if isinstance(obj, dict) and "$mimetype$" in obj:
            if (obj["$mimetype$"]) in self.codecs._register:
                path = obj['$path$']
                f = None
                if path.startswith("http"):
                    f = self.session.get(obj['$path$']).content
                    path = f[0]

                obj = self.codecs._register[obj["$mimetype$"]].decode(obj, path)

                if f is not None:
                    os.unlink(f[0])
            else:
                logging.warning("mimejson: unsupported mimetype: %s\n" % (obj['$mimetype$'],))
        return obj

    def _mimejson_encode_object(self, obj):
        return _xmap(obj, self.__mimejson_encode_item)

    def _mimejson_decode_object(self, obj):
        return _xmap(obj, self.__mimejson_decode_item)

    def _dump(self, data):
        """
        Encode an object and push the encoded object to the server.

        :return: a mimejson object with reference to encoded elements
        """
        data = self._mimejson_encode_object(data)
        return json.dumps(data)

    def push(self, data, url):
        """
        Use MIMEJSON Serializer and its associated transport as a way to make a multipart query on a server.

        :param data: The object to be sent
        :param url: the endpoint to be queried
        :return: response from the API endpoint (assumed to be MIMEJSON)
        """
        data = self._dump(data)
        if not self.transport:
            raise ValueError("Not connected")

        # clean_data = {}
        # for k in data:
        #     if type(self.data[k]) not in JSON_ATOMS:
        #         clean_data[k] = json.dumps(data[k])  # ENSURE ALL DATA ARE COMPATBLE
        #     else:
        #         clean_data[k] = data[k]

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
            data = json.load(json_file)
            json_file.close()
        else:
            data = self.session.get(uri).json()

        data = self._mimejson_decode_object(data)
        return data

    def loads(self, data):
        """
        Load object from string json.
        """
        data = self._mimejson_decode_object(json.loads(data))
        return data

    def loadd(self, object_instance):
        """
        Load object from dict.
        """
        data = self._mimejson_decode_object(object_instance)
        return data

    # current implementation requires a temporary folder
    # with pattern ensures this folder is created and deleted as necessary
    def __enter__(self):
        if os.path.exists(self.storage) and self.using_tmp_storage:
            errmsg = """
            Temporary folder %s must be a non-existent as it will be deleted on exit
            """ % (self.storage,)
            raise Exception(errmsg)

        if not os.path.exists(self.storage):
            _mkdir_p(self.storage)
            os.chmod(self.storage, 0o700)
        return self

    def __exit__(self, *_args):
        if self.using_tmp_storage:
            for f in os.listdir(self.storage):
                os.unlink(os.path.join(self.storage, f))
            os.rmdir(self.storage)
