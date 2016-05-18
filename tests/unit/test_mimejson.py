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

import json
import os
import sys

import mimejson

sys.path.append(os.getcwd())


def test_mimejson_trivial_object():
    """
    MIMEJSON serialization/deserialization reproduce the same objects for trivial object.
    """
    with mimejson.MIMEJSON() as mj:
        assert(mj.loads(mj.dumps({})) == {})


def test_mimejson_is_json_equivalent_in_simple_cases():
    """
    MIMEJSON serialize JSON in a standard way.
    """
    with mimejson.MIMEJSON() as mj:
        for x in [{'a': 2}, {'a': [1, 2, 3]}, [1, 2, 3]]:
            assert(mj.dumps(x) == json.dumps(x))


def test_mimejson_load_default_codecs():
    """
    MIMEJSON has a set of native plugins distributed with it.
    """
    with mimejson.MIMEJSON() as mj:
        assert(len(mj.codecs.all_codecs))


# def test_mimejson_use_specific_codecs():
#     """
#     MIMEJSON has a set of native plugins distributed with it.
#     """
#     with mimejson.MIMEJSON() as mj:
#         pass
