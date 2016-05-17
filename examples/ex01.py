#!/usr/bin/env python
import os
import mimejson

import PIL.Image
img = PIL.Image.open("sample.png")

# the multimedia data that we want to serialise is included directly in the json
data = {'image': img}

# serialise using local filesystem
os.chdir('/')
with mimejson.MIMEJSON() as mj:
    print ("original object " + repr(data))
    r = mj.push(data)
    print "serialised object", r, type(r)
    rdata = mj.loads(r)
    print "reconstructed object", rdata
