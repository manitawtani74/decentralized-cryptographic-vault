import json
from stat import FILE_ATTRIBUTE_NO_SCRUB_DATA
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from shredder.models import File as CustomFile
from shredder.Serializers.File import (
    UserSerializer,
    GroupSerializer,
    FileSerializer,
)

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from shredder.utils.downloader import download_file_from_gstorage

# File shred/join helpers.
from shredder.utils.split import split
from shredder.utils.join import join

# Import Mimetype
import mimetypes

# Encrypter
import pyAesCrypt
ENCYPTION_SECRET = "super-sec"

# absolute path module.
from os.path import abspath
import os

# hashing helper
import hashlib

# Upload handler
from shredder.utils.gcloud_bucket_upload import upload_blob

# Get custom django global constant
from django.conf import settings

# Ramdom choice helper
from random import choice as random_choice

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class FileView(APIView):
    """
    API class that pdovides the different handlers for file.
    """

    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        """
        API endpoint that accepts, stores, a file and creates file metadata including the chunk-map in DB.
        """
        file_serializer = FileSerializer(data=request.data)

        if file_serializer.is_valid():
            file_instance: CustomFile = file_serializer.save()

            abs_file_path = abspath(f'.{file_serializer.data.get("file")}')
            abs_enc_file_path = ''

            print(abs_file_path)

            # Encrypt
            print(request.data["enc_key"])
            pyAesCrypt.encryptFile(abs_file_path, abs_file_path+".aes", request.data["enc_key"])
            abs_enc_file_path = abs_file_path+".aes"

            # Get abs-file name
            file_path = str(file_serializer.data.get("file"))
            file_name = file_path[file_path.rindex("/") + 1 : file_path.rindex(".")]
            file_name_ext = file_path[file_path.rindex("/") + 1 :]


            # Destination directory for file chunks.
            abs_dest_dir_path = abspath(f"media/chunks/{file_name}")

            # Parts list
            parts: list = []

            # TIME TO SHRED FILE
            try:
                # Encrypt the src file using AES algo.
                parts: list = split(fromfile=abs_enc_file_path, todir=abs_dest_dir_path)
            except Exception as err:
                print(f"Error in splitting!\nERROR: {err}")

            try:
                # Storage map
                chunk_map = dict()
                #  Get avb bucket names.
                AVB_BUCKETS: list = settings.AVB_BUCKETS

                for chunk_num, file in enumerate(parts):

                    # Choose a random bucket.
                    for i in range(3):
                        dest_file = file[file.rindex("/") + 1 :]
                        dest_file_path = file_name + "/" + dest_file
                        target_bucket = random_choice(AVB_BUCKETS)
                        chunk_map.update({f"chunk#{chunk_num}_replica#{i}": [target_bucket, dest_file_path]})
                        upload_blob(
                            bucket_name=target_bucket,
                            source_file_name=file,
                            destination_blob_name=dest_file_path,
                        )
                # Update mapping in DB and save.
                file_instance.chunkmap = chunk_map
                file_instance.processed = True
                file_instance.save()

            except Exception as err:
                print("Error uploading", err)

            # Sendback file uuid.
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        """
        API endpoint that facilitates retreiving, joining, and dowloading the recreated file.
        """

        file_name_ext = request.GET.get("file")
        file_name = file_name_ext[: file_name_ext.rindex(".")]

        abs_new_file_path = abspath(f"media/RECREATED_{file_name_ext}")
        abs_src_dir_path = abspath(f"media/chunks/{file_name}")

        filename_in_db = "media/" + file_name_ext
        print(filename_in_db)
        
        # Get abs file paths from DB
        file_instance = CustomFile.objects.get(file=file_name_ext)

        # Download file chunks
        download_file_from_gstorage(file_instance)

        # JOIN FILE
        try:
            join(fromdir=abs_src_dir_path, tofile=abs_new_file_path)
        except Exception as err:
            print(f"Error in joining!\nERROR: {err}")

        # Decrypt FILE
        try:
            pyAesCrypt.decryptFile(filename_in_db+".aes", file_name_ext, request.GET.get("key"))
            # Response
            with open(file_name_ext, 'r'):
                mime_type, _ = mimetypes.guess_type(file_name_ext)
                return Response(
                    {"download-link": "File stitched :)"}, status=status.HTTP_200_OK
                )
                
        except ValueError as e:
            print("Wrong password")
            # Response
            return Response(
                {"download-link": "PROTECTED", "reason" : "ENCRYPTION KEY MISMATCH"}, status=status.HTTP_200_OK
            )

        
