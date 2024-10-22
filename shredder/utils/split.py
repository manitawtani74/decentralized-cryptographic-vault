import sys, os
from django.conf import settings

# Config-Param
CHUNK_SIZE = int(settings.CHUNK_SIZE)


def split(fromfile, todir, CHUNK_SIZE=CHUNK_SIZE):
    """
    Splits the file in the provided filepath into chunks of size CHUNK_SIZE, and stores in todir directory.
    """
    if not os.path.exists(todir):
        os.mkdir(todir)
    else:
        for fname in os.listdir(todir):
            os.remove(os.path.join(todir, fname))
    partnum = 0
    parts: list = []

    with open(fromfile, "rb") as input:
        while 1:
            chunk = input.read(CHUNK_SIZE)
            if not chunk:
                break
            partnum = partnum + 1
            filename = os.path.join(todir, ("part%04d" % partnum))
            parts.append(filename)
            fileobj = open(filename, "wb")
            fileobj.write(chunk)
            fileobj.close()
    # input.close()
    assert partnum <= 9999
    return parts
