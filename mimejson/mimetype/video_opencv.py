# ############################################################################
# |W|I|D|E|I|O|L|T|D|W|I|D|E|I|O|L|T|D|W|I|D|E|I|O|L|T|D|W|I|D|E|I|O|L|T|D|
# Copyright (c) WIDE IO LTD
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
import functools
import os

import cv2.cv as cv


class Serializer:
    mimetype = (
        "video/FMP4",
        "video/DIVX"
    )

    @staticmethod
    def can_apply(obj):
        frames = None
        required = ("$name$", "$fps$", "$encodage$",
                    "$frame_size$", "$color$", "$frames_list$")
        if not isinstance(obj, dict):
            return False
        for check in required:
            if check not in obj:
                return False
        frames = obj["$frames_list$"]
        if frames is None or not isinstance(frames, list):
            return False
        for frame in frames:
            if not isinstance(frame, cv.iplimage):
                return False
        return True

    @classmethod
    def serialize(cls, obj, pathdir):
        fn = os.path.join(pathdir, obj["$name$"])
        writer = cv.CreateVideoWriter(fn, obj["$encodage$"], obj["$fps$"],
                                      obj["$frame_size$"], obj["$color$"])
        write = functools.partial(cv.WriteFrame, writer)
        map(write, obj["$frames_list$"])
        return {'$path$': fn, '$length$': os.stat(fn).st_size,
                '$mimetype$': obj["$mimetype$"]}

    @staticmethod
    def deserialize(obj, filepath):
        video = cv.CaptureFromFile(obj["$path$"])
        obj["$frames_list$"] = []
        obj["$color$"] = 1
        obj["$name$"] = os.path.basename(obj["$path$"])
        obj["$fps$"] = int(cv.GetCaptureProperty(video, cv.CV_CAP_PROP_FPS))
        obj["$encodage$"] = int(cv.GetCaptureProperty(video,
                                                      cv.CV_CAP_PROP_FOURCC))
        f_w = int(cv.GetCaptureProperty(video, cv.CV_CAP_PROP_FRAME_WIDTH))
        f_h = int(cv.GetCaptureProperty(video, cv.CV_CAP_PROP_FRAME_HEIGHT))
        obj["$frame_size$"] = (f_w, f_h)
        del obj["$path$"]
        nu_frame = cv.GetCaptureProperty(video, cv.CV_CAP_PROP_FRAME_COUNT)
        for i in range(int(nu_frame)):
            frame = cv.QueryFrame(video)
            obj["$frames_list$"].append(cv.CloneImage(frame))
        return obj
