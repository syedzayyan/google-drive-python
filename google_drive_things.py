from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io, os
import shutil
from apiclient.http import MediaFileUpload, MediaIoBaseDownload

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

class apiCrap:
    def __init__(self, SCOPES, hospital, credentialForHospital):
        self.SCOPES = SCOPES
        self.hospital = hospital
        self.credentialForHospital = credentialForHospital
    def auth(self):
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.credentialForHospital):
            with open(self.credentialForHospital, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.hospital , self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.credentialForHospital, 'wb') as token:
                pickle.dump(creds, token)

        service = build('drive', 'v3', credentials=creds)
        return service
    def listFilesInFolder(self, folderKey):
        service = self.auth()
        page_token = None
        querystring = "'{!s}' in parents".format(folderKey)
        results = service.files().list(q = querystring,
                                          spaces='drive',
                                          fields='nextPageToken, files(id, name, mimeType)',
                                          pageToken=page_token).execute()
        items = results.get('files', [])
        return items


    # Downloads Whole_Folder to fileDownpath
    def downloadFiles(self, fileDownPath, downLoadFolderKey):
        service = self.auth()
        items = self.listFilesInFolder(downLoadFolderKey)


        for item in items:
            fileMime = item.get("mimeType")
            if fileMime == "application/vnd.google-apps.folder":
                folder_id = (item.get('id'))
                folder_name = (item.get('name'))
                innerFolderItems = self.listFilesInFolder(folder_id)
                for innerItems in innerFolderItems:
                    print(innerItems.get('id'))
                    request = service.files().get_media(fileId=file_id)
                    fh = io.BytesIO()
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print ("Download %d%%." % int(status.progress() * 100) + file_name)
                    filepath = fileDownPath + folder_name + "/" + file_name
                    folderpath = fileDownPath + folder_name + "/"
                    try:
                        os.mkdir(folderpath)
                    except:
                        pass
                    with io.open(filepath, 'wb') as f:
                        fh.seek(0)
                        f.write(fh.read())
            elif fileMime != 'application/vnd.google-apps.folder':
                file_id = (item.get('id'))
                file_name = (item.get('name'))
                request = service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print ("Download %d%%." % int(status.progress() * 100) + file_name)
                filepath = fileDownPath + file_name
                with io.open(filepath, 'wb') as f:
                    fh.seek(0)
                    f.write(fh.read())
            else:
                print ("Nothing Found")

    #UploadFiles method uploads files to a specific folder from specific file path
    def uploadFiles(self, fileUpPath, upLoadFolderKey, filename):
        service = self.auth()
        file_metadata = {'name': filename, 'parents' : [upLoadFolderKey]}
        individualFilesPath = fileUpPath + filename
        media = MediaFileUpload(individualFilesPath)
        file = service.files().create(body=file_metadata,
                                            media_body=media,
                                        fields='id').execute()
        print ('File name: %s' %filename)
        return "Done"

    def updateFiles(self, fileUpPath, upLoadFolderKey, file_id, file_name):
            service = self.auth()
            file = service.files().get(fileId=file_id).execute()
            # File's new content.
            individualFilesPath = fileUpPath + file_name
            media = MediaFileUpload(individualFilesPath)
            # Send the request to the API.
            updated_file = service.files().update(
                fileId=file_id,
                media_body=media).execute()

    def deleteFiles(self, deleteFolderKey):
        service = self.auth()
        items = self.listFilesInFolder(deleteFolderKey)
        for item in items:
            file_id = (item.get('id'))
            deletefile = service.files().delete(fileId = file_id).execute()
    def deleteTrash(self):
        service = self.auth()
        service.files().emptyTrash().execute()
