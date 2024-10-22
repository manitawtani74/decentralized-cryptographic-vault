import imp
import os, sys
from django.conf import settings

READ_SIZE = int(settings.READ_SIZE)


def join(fromdir, tofile):
    """
    Joins all chunks in specified directory, and recreates file.
    """
    output = open(tofile, "wb")
    parts = os.listdir(fromdir)
    parts.sort()
    for filename in parts:
        filepath = os.path.join(fromdir, filename)
        fileobj = open(filepath, "rb")
        while 1:
            filebytes = fileobj.read(READ_SIZE)
            if not filebytes:
                break
            output.write(filebytes)
        fileobj.close()
    output.close()
