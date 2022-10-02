import io
import json
import pyminizip
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import hashlib

# 'https://www.googleapis.com/auth/contacts.readonly'
SCOPES = ['https://www.googleapis.com/auth/drive.file']


def get_drive_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)
        return service

    except HttpError as error:
        print(f'An error occurred: {error}')


def upload_file(service, file_name, mime_type):
    try:
        file_metadata = {'name': file_name}
        media = MediaFileUpload(file_name,
                                mimetype=mime_type)
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute()
        print(F'File ID: {file.get("id")}')
        return file.get("id")

    except HttpError as error:
        print(f'An error occurred: {error}')


def download_file(service, file_id, out_path):
    try:
        request = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    # write file to disk
    with open(out_path, 'wb') as f:
        f.write(file.getbuffer())

    return file.getvalue()


def get_people():
    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        service = build('people', 'v1', credentials=creds)

        # Call the People API
        print('List 10 connection names')
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=10,
            personFields='names,emailAddresses').execute()
        connections = results.get('connections', [])

        for person in connections:
            names = person.get('names', [])
            if names:
                name = names[0].get('displayName')
                print(name)
    except HttpError as err:
        print(err)


if __name__ == '__main__':

    # create zip file
    in_path = "files/dummy.txt"
    zip_path = "files/myzip.zip"
    pwd = "password1"
    compress_level = 5
    curr_dir = os.path.dirname(os.path.abspath(__file__))

    pyminizip.compress(in_path, None, zip_path, pwd, compress_level)

    drive_service = get_drive_service()

    # upload zip file
    file_id = upload_file(drive_service, zip_path, 'application/zip')

    out_path = 'out'

    # download_file
    download_file(drive_service, file_id, out_path)

    # unzip
    pyminizip.uncompress(out_path, pwd, None, compress_level)

    # hash
    sha256_hash = hashlib.sha256()

    with open('dummy.txt', "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    print(sha256_hash.hexdigest())
    hash = sha256_hash.hexdigest()

    # upload file
    file_id2 = upload_file(drive_service, 'dummy.txt', 'text/plain')

    # get logs
    events = {}
    res = drive_service.files().get(fileId=file_id, fields="*").execute()
    events[file_id] = res

    res = drive_service.files().get(fileId=file_id2, fields="*").execute()
    events[file_id] = res

    with open("log.json", "w") as outfile:
        json.dump(events, outfile)

    # get people API
    get_people()
