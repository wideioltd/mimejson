[![Codacy Badge](https://api.codacy.com/project/badge/Grade/a2a36d1e8d0e40c5b5d26878998492fb)](https://www.codacy.com/app/bn/mimejson?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=wideioltd/mimejson&amp;utm_campaign=Badge_Grade)
# MIMEJSON

MIMEJSON is a minimal extension to JSON to allow to perform serialisation and transport of
 large MULTIPART objects in an intelligent fashion.
 This is particularly suitable for the transfer of large complex multimedia/scientific data.

## The issue with multipart and binary data and JSON

JSON has became an ubiquitous standard to transmit structured objects
between computers. However, it is not suitable to serialise all types of
object: It does not apply to images, video, and other binary objects
such as large matrices, and cannot apply easily to any object that contain
such an element.

The natural way of solving this limitation is to give an external link to the external object, however
currently there is no way to properly detect these links and to decide how these must serialised or
deserialised. Consequently, the transmissions of JSON containing references to other objects is often
handled in an ad hoc way.

## Mimejson
MIMEJSON allow to introduce reference to binary objects in documents by introducing object with a `$mimetype$` key
 and `$path$` and `$length$` can then be used to indicate the client where to find the other part of the object.
 The mimetype provide the essential information required to serialises/deserialises the objects using a specific
mimetype handlers. By default, the files are stored in the folder (local or remote) as the JSON object being read.


## Schemas
MIMEJSON also allow your data to refer to explicit schema.

## Supported datatypes
The MIMEJSON library is designed to be extensible.

The MIMEJSON library has an engine that allows to associate to mimetypes specific serialisers / deserialisers:
 each application can get serialised data deserialised to the type it prefers.

The current version includes support for PIL and OpenCV.

## Example


```python
#!/usr/bin/env python
import mimejson

import PIL.Image
img=PIL.Image.open("/usr/share/pixmaps/ubuntu-logo.png")

# the multimedia data that we want to serialise
data={'image':img}

## serialisation using local filesystem
with mimejson.MIMEJSON() as mj:
  print "original object", data
  r=mj.push(data)
  print "serialised object",r
  rdata=mj.loads(r)
  print "reconstructed object", rdata
```

The output of this program is :
```
original object {'image': <PIL.PngImagePlugin.PngImageFile image mode=RGBA size=44x44 at 0x7FD73ECAF6C8>}
serialised object {"image": {"$path$": "/home/user/mimejson/.mjson-23176/a4a0f794-3e64-11e4-b2f2-902b34a1ef7b.png","$mimetype$": "image/png", "$length$": 2063}}
reconstructed object {u'image': <PIL.PngImagePlugin.PngImageFile image mode=RGBA size=44x44 at 0x7FD73E0EF128>}

```

## Upload to servers and mimejson compatible APIs

The MIMEJSON library can also upload forms via HTTP and HTTPS. The current protocol transmit via the POST method all the variables of the base document.  Variables that are documents are serialised to MIMEJSON. Multimedia object that are encoded as files are uploaded via a multipart form.

## Status

MIMEJSON is currently at the state of a proposal. It has been tested in a few projects and fits nicely our internal needs.  We are looking for feedbacks to know if it corresponds to your needs as well.

Currenlty, only PYTHON is supported. We believe it should be reasonably easy to implement similar extension libraries in languages like : Ruby, Java, or C#.

## Documentation

Please check the source code and the PDF documentation for more details about the current implementation.

## License

MIMEJSON is released under a BSD-style license.

## About us

MIMEJSON is developed and supported by [WIDE IO LTD](http://www.wide.io) .
