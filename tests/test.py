from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from src.targets_plot_generator import image_addresses
import json
from src import settings
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
import os


def resolve_TargetPlotsUpload(_, info,case,predicted_targets,actual_targets,dates):
    try:
        def authenticate():
            """Authenticate with Google Drive API and return credentials."""
            try:
                with open(settings.credentials_file) as f:
                    credentials = json.load(f)
                creds = service_account.Credentials.from_service_account_info(credentials)
                return creds
            except FileNotFoundError:
                print("OAuth file not found.")
                return None
            except json.JSONDecodeError:
                print("Error decoding OAuth file. Make sure it contains valid JSON.")
                return None

        def upload_image_to_folder(folder_id,plot_name,image_path):
            """Upload an image to a folder in Google Drive and return the folder's web link."""
            try:
                # Authenticate with Google Drive API
                # creds = service_account.Credentials.from_service_account_file(credentials_file, scopes=['https://www.googleapis.com/auth/drive'])
                # service = build("drive", "v3", credentials=creds)

                # Create folder if it doesn't exist
                # folder_id = get_folder_id_by_name(folder_path)
                # Check if the file already exists in the folder
                # file_name = image_path.split('/')[-1]
                query = f"'{folder_id}' in parents and name = '{plot_name}' and trashed=false"
                response = service.files().list(q=query, fields='files(id)').execute()
                files = response.get('files', [])
                # print(files)
                if files:
                    print(f"File '{plot_name}' already exists in the folder. Skipping upload.")
                    file_id = files[0]['id']
                    print(file_id)
                    # revoke_all_permissions_except_owner(folder_id, settings.domain,credentials_file)

                else:
                    # Upload image to the folder
                    file_metadata = {
                        'name': plot_name,
                        'parents': [folder_id]
                    }
                    media = MediaFileUpload(image_path, mimetype="image/png")
                    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                    file_id = file['id']
                    # revoke all permissions 
                    # Set permissions for the uploaded file
                # set_file_permissions(service, file_id)
                # share_file(file_id,settings.username,settings.domain)
                # Generate URL for the uploaded file
                web_link = f'https://drive.google.com/file/d/{file_id}/view?usp=drivesdk'
                return file_id, web_link
            except HttpError as error:
                print(f"An error occurred: {error}")
                return None, None

        def get_folder_id_by_name(parent_folder_name):
            """Get the ID of a folder by its name."""
            try:
                query = f"name='{parent_folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
                response = service.files().list(q=query, fields='files(id)').execute()
                folders = response.get('files', [])
                if folders:
                    print("folder exists")
                    return folders[0]['id']
                else:
                    return None
            except HttpError as error:
                print(f"An error occurred: {error}")
                return None
            
        def get_folder_id_by_name(parent_folder_name):
            """Get the ID of a folder by its name."""
            try:
                query = f"name='{parent_folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
                response = service.files().list(q=query, fields='files(id)').execute()
                folders = response.get('files', [])
                if folders:
                    return folders[0]['id']
                else:
                    return None
            except HttpError as error:
                print(f"An error occurred: {error}")
                return None
        # def create_folder_if_not_exists(service, folder_name, parent_folder_name):
        #     """Create a folder in Google Drive if it doesn't exist and return its ID."""

        #     # Get the parent folder ID
        #     parent_folder_id = get_folder_id_by_name(service, parent_folder_name)

        #     # Create the folder in the parent folder
        #     return create_folder_if_not_exists(service, folder_name, parent_folder_id)

        # def get_folder_id_by_name(service,folder_path):
        #     """
        #         Returns the ID of a subfolder within a predefined folder path.

        #         Args:
        #             folder_path: The path to the subfolder, separated by '/'.

        #         Returns:
        #             The ID of the subfolder, or None if not found.
        #         """

                # Authenticate with Google Drive API
            # drive_service = build('drive', 'v3')

            # Split the folder path into individual folder names
            # folder_names = list(folder_path.split('/'))
            # print(folder_names)  
            # Get the root folder ID
            # parent_folder_id = 'root'
            # query = f"'{parent_folder_id}' in parents and name = '{folder_name}'"
            # response = service.files().list(q=query).execute()

            # # If the folder is found, update the parent folder ID
            # if response['files']:
            #     parent_folder_id = response['files'][0]['id']
            #     print("parent_folder_id:",parent_folder_id)
            # # Otherwise, the subfolder was not found
            # else:
            #     return None
            #     response = service.files().list(q=query).execute()

            #     # If the folder is found, update the parent folder ID
            #     if response['files']:
            #         parent_folder_id = response['files'][0]['id']
            # Iterate through the folder names to find the subfolder ID
            # all_folder_ids = {}
            # print("allok")
            # for folder_name in folder_names:
            #     # Query for folders with the given name and parent folder ID
            #     print(folder_name)
            #     query = f"'{parent_folder_id}' in parents and name = '{folder_name}'"
            #     response = service.files().list(q=query).execute()
            #     print(response['files'])
            #     # If the folder is found, update the parent folder ID
            #     if response['files']:
            #         parent_folder_id = response['files'][0]['id']
            #         all_folder_ids[folder_name] = parent_folder_id
            #     # Otherwise, the subfolder was not found
            #     else:
            #         return None

            # Return the ID of the final subfolder
            # return all_folder_ids
        def create_folder_if_not_exists(service, new_folder,parent_folder_id):
            """Create a folder in Google Drive if it doesn't exist and return its ID."""
            try:
                # Check if the folder already exists
                if parent_folder_id==None:
                    query = f"name='{new_folder}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
                else:
                    query = f"name='{new_folder}' and mimeType='application/vnd.google-apps.folder' and trashed=false and '{parent_folder_id}' in parents"

                # query = f"'{folder_id}' in parents and name = '{plot_name}' and trashed=false"
                response = service.files().list(q=query, fields='files(id)').execute()
                folders = response.get('files', [])
                if folders:
                    print("folder exists",folders[0]['id'])
                    share_file(
                        real_file_id=folders[0]['id'],
                        real_user=settings.username,
                        real_domain=settings.domain,
                    )
                    return folders[0]['id']  # Return existing folder ID
                else:
                    # Create the folder if it doesn't exist
                    file_metadata = {
                        'name': new_folder,
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [parent_folder_id]
                    }
                    folder = service.files().create(body=file_metadata, fields='id').execute()
                share_file(
                    real_file_id=folder['id'],
                    real_user=settings.username,
                    real_domain=settings.domain,
                )
                # set_file_permissions(service, folder['id'])
                print(folder['id'])
                return folder['id']  # Return newly created folder ID
            except HttpError as error:
                print(f"An error occurred: {error}")
                return None


        def get_folder_web_link(service, folder_id):
            """Get the web link for the specified folder."""
            try:
                # Get the metadata for the folder
                folder = service.files().get(fileId=folder_id, fields='webViewLink').execute()
                return folder.get('webViewLink')  # Return the web link for the folder
            except HttpError as error:
                print(f"An error occurred: {error}")
                return None
            

        # def set_file_permissions(service, file_id):
        #     """Set permissions for a file to allow anyone with the link to view it."""
        #     try:
        #         permission = {
        #             'role': 'reader',
        #             'type': 'domain',
        #             "domain": settings.domain,
        #             'allowFileDiscovery': True
        #         }
        #         service.permissions().create(fileId=file_id, body=permission).execute()
        #         print('File permissions set successfully.')
        #     except HttpError as error:
        #         print(f"An error occurred: {error}")


        def share_file(real_file_id, real_user, real_domain):
            """Batch permission modification.
            Args:
                real_file_id: file Id
                real_user: User ID
                real_domain: Domain of the user ID
            Prints modified permissions

            Load pre-authorized user credentials from the environment.
            TODO(developer) - See https://developers.google.com/identity
            for guides on implementing OAuth2 for the application.
            """
            #   creds, _ = google.auth.default()
            #   creds = settings.credentials_file
            creds = authenticate()

            try:
                # create drive api client
                service = build("drive", "v3", credentials=creds)
                ids = []
                file_id = real_file_id

                def callback(request_id, response, exception):
                    if exception:
                        # Handle error
                        print(exception)
                    else:
                        print(f"Request_Id: {request_id}")
                        print(f'Permission Id: {response.get("id")}')
                        ids.append(response.get("id"))

                # pylint: disable=maybe-no-member
                batch = service.new_batch_http_request(callback=callback)
                user_permission = {
                    "type": "user",
                    "role": "writer",
                    "emailAddress": real_user,
                }
                print("user_permission done")
                batch.add(
                    service.permissions().create(
                        fileId=file_id,
                        body=user_permission,
                        fields="id",
                    )
                )
                # domain_permission = {
                #     "type": "domain",
                #     "role": "reader",
                #     "domain": settings.domain,
                # }
                # print("domain_permission done")
                # domain_permission["domain"] = real_domain
                # batch.add(
                #     service.permissions().create(
                #         fileId=file_id,
                #         body=domain_permission,
                #         fields="id",
                #     )
                # )
                # batch.execute()
                # print("permissions added sucessfully")
            
            except HttpError as error:
                print(f"An error occurred: {error}")
                ids = None
                
            return ids

        def revoke_all_permissions_except_owner(file_id, domains,credentials_file):
            """Revoke all permissions for a given file except the owner's."""
            try:
            # Create the Drive API client.
                creds = service_account.Credentials.from_service_account_file(credentials_file, scopes=['https://www.googleapis.com/auth/drive'])
                service = build("drive", "v3", credentials=creds)

                # Get the list of permissions for the folder.
                permissions = service.permissions().list(fileId=file_id).execute().get('permissions', [])
                # for permission in permissions:
                #     if permission['type'] == 'domain' and permission['domain'] == domains:
                #         service.permissions().delete(fileId=file_id, permissionId=permission['id']).execute()
                #         break
                # Revoke all permissions except for the owner's.
                for permission in permissions:
                    if permission['type'] != 'user':
                        service.permissions().delete(fileId=file_id, permissionId=permission['id']).execute()
                print("All permissions (except owner) revoked successfully.")
            except HttpError as error:
                print(f"An error occurred: {error}")

        
            # Authenticate with Google Drive API
        credentials = authenticate()

        # Build Google Drive service
        service = build('drive', 'v3', credentials=credentials)
        # Create the folder if it doesn't exist
        # print("created")
        # Create a plot
        # plt.figure()
        # plt.plot([1, 2, 3, 4], [10, 20, 25, 30])
        # plt.title("Test Plot")
        # # plt.show("Test Plot")
        # # Save to a temporary file
        # temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        # plt.savefig(temp_file.name)
        # plt.close()
        # print(f"Temperory file address:{temp_file.name}")
        # image_path = str(temp_file.name)
        asset = case.split('_')[-5]
        target = case.split('_')[-4]
        training_time_duration = case.split('_')[-3]
        Run_case = case.split('_')[-2]
        folder_path = f"Learn Unit/Price Prediction Models/{asset} Stock/{target} target/{training_time_duration} Training Dataset/{Run_case} Case/Target Prediction Plots"
        all_folders = list(folder_path.split("/"))
        # first_parent_folder_id = get_folder_id_by_name(all_folders[0])
        folder_ids = []
        for i in range(len(all_folders)-1):
            if i==0:
                new_folder = all_folders[0]
                parent_folder_id = None
            else:
                new_folder = all_folders[i]
                parent_folder_id = get_folder_id_by_name(all_folders[i-1])
            folder_id = create_folder_if_not_exists(service, new_folder,parent_folder_id)
            # folder_id = create_folder_if_not_exists(service, new_folder)
            folder_ids.append(folder_id)
        # all_folder_id = get_folder_id_by_name(folder_path[1])
        # folder_id = list(all_folder_id)[-1]
        print(folder_ids)
        plot_addresses = image_addresses(predicted_targets,actual_targets,dates,target)
        # print("got address")
        temp_plot_address = [value for value in plot_addresses.values()]
        print(f"Temperory Plot addresses:{temp_plot_address}")
        plot_types = [key for key in plot_addresses.keys()]
        print(f"Plot Names:{plot_types}")
        new_dates = pd.Series(pd.to_datetime(dates))
        start_date = str(new_dates.min())
        end_date = str(new_dates.max())
        plot_names =[]
        for plot_type in plot_types:
            # case = "SPP-MSFT_20140102-20221230_MPN7P_S0/LSTM-15710760-B64E100L0.0005T10-DOHLCAV-NNNEKNR_VS_11013L0.75-100-1_DM"
            plot_title = f'{plot_type} - Predicted and Actual Targets versus Dates for {target} from {start_date} to {end_date}'
            plot_name = case + ' - ' + plot_title
            plot_names.append(plot_name)
        # print(plot_names)
        # plot_addresses = []
        file_ids = []
        file_web_links = []

        # Loop through each plot name and address
        for plot_name, plot_address in zip(plot_names, temp_plot_address):
            # Call the function for each plot
            file_id, file_web_link = upload_image_to_folder(folder_ids[-1], plot_name, plot_address)
            share_file(
                real_file_id=file_id,
                real_user=settings.username,
                real_domain=settings.domain,
            )
            # Append the results to the lists
            file_ids.append(file_id)
            file_web_links.append(file_web_link)
        # Now you have all file IDs and web links stored
        print("File IDs:", file_ids)
        print("File_Web Links:", file_web_links)
        folder_web_link = get_folder_web_link(service, folder_id)
        if folder_web_link:
            print(f"Folder web link: {folder_web_link}")
        # for plot_addresses in results_list :
        # # if folder_id:
        #     # plot_address= int(plot_address)
        #     # Set permissions for the folder
        #     print(plot_addresses)
        #     # Upload image to the folder
        #     file_id, file_web_link = upload_image_to_folder(new_folder_name,plot_names, plot_addresses, credentials)
        #     print("uploaded")
        #     share_file(
        #         real_file_id=file_id,
        #         real_user=settings.username,
        #         real_domain=settings.domain,
        #     )
        #     if file_web_link:
        #         print(f"File web link: {file_web_link}")
        #     # Print the web link for the folder
        #     folder_web_link = get_folder_web_link(service, folder_id)
        #     if folder_web_link:
        #         print(f"Folder web link: {folder_web_link}")
            
        response= {
        'success': True,
        'error': None,
        'file_web_link':file_web_links,
        'folder_web_link':folder_web_link
        }
        # os.unlink(plot_name) # remove the file after upload

    except Exception as error:
        response = {
            'success': False,
            'error': error
        }
        return response

    return response

result=resolve_TargetPlotsUpload('_','info',settings.case,settings.predicted_targets,settings.actual_targets,settings.dates)
print(result)