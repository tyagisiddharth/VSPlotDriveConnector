from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from src.targets_plot_generator import image_addresses
import json
from src import settings
import pandas as pd
import tempfile
from PIL import Image
import datetime


def resolve_TargetPlotsUploader(_, info,case,predicted_targets,actual_targets,dates):
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
                    file_type = image_path.split('.')[-1]
                    if file_type == 'pdf':
                        media = MediaFileUpload(image_path, mimetype='application/pdf')
                    elif file_type == 'jpg':
                        media = MediaFileUpload(image_path, mimetype='image/jpeg')
                    else:
                        media = MediaFileUpload(image_path, mimetype='image/png')
                    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                    file_id = file['id']

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
            

        def share_file(real_file_id, real_user, real_domain):
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
                
                # Uncomment below domain_permissions if folder or file access permission is set to be as per DOMAIN(example- @akgec.ac.in)
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
                batch.execute()
                # print("permissions added sucessfully")
            
            except HttpError as error:
                print(f"An error occurred: {error}")
                ids = None
                
            return ids

        # Currently revoke permissions work for user_mail only not for domains but we haven't used this function because it's easy to do it on Drive UI rather than function 
        def revoke_all_permissions_except_owner(file_id, domains,credentials_file):
            """Revoke all permissions for a given file except the owner's."""
            try:
            # Create the Drive API client.
                creds = service_account.Credentials.from_service_account_file(credentials_file, scopes=['https://www.googleapis.com/auth/drive'])
                service = build("drive", "v3", credentials=creds)

                # Get the list of permissions for the folder.
                permissions = service.permissions().list(fileId=file_id).execute().get('permissions', [])

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
        asset = case.split('/')[0]
        target = case.split('/')[1] 
        training_time_duration = case.split('/')[2]
        Run_case = case.split('/')[3]
        folder_path = f"Learn Unit/Price Prediction Models/{asset} Stock/{target} target/{training_time_duration} Training Dataset/{Run_case} Case/Plots"
        all_folders = list(folder_path.split("/"))
        folder_ids = []
        for i in range(len(all_folders)-1):
            if i==0:
                new_folder = all_folders[0]
                parent_folder_id = None
            else:
                new_folder = all_folders[i]
                parent_folder_id = get_folder_id_by_name(all_folders[i-1])
            folder_id = create_folder_if_not_exists(service, new_folder,parent_folder_id)
            folder_ids.append(folder_id)

        print(folder_ids)
        plot_addresses = image_addresses(predicted_targets,actual_targets,dates,target)
        temp_plot_address = [value for value in plot_addresses.values()]
        print(f"Temperory Plot addresses:{temp_plot_address}")

        pdf_temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        images = [Image.open(jpg).convert('RGB') for jpg in temp_plot_address]
        images[0].save(pdf_temp_path.name, save_all=True, append_images=images[1:], quality=100, dpi=(300, 300))
        pdf_temp_path.close()
        print(f"pdf_temp_path:{pdf_temp_path.name}")
        pdf_final_path = pdf_temp_path.name

        plot_types = [key for key in plot_addresses.keys()]
        print(f"Plot Names:{plot_types}")
        new_dates = pd.Series(pd.to_datetime(dates))
        start_date = str(new_dates.min())
        end_date = str(new_dates.max())

        today_date = datetime.date.today()
        plot_pdf_names = f'{Run_case}-Predicted and Actual Targets versus Dates for {target} from {start_date} to {end_date}.pdf'

        plot_names =[]
        
        for plot_type in plot_types:
            plot_title = f'{plot_type} - Predicted and Actual Targets versus Dates for {target} from {start_date} to {end_date}'
            plot_name = Run_case + ' - ' + plot_title
            plot_names.append(plot_name)

        file_ids = []
        file_web_links = []

        file_id, file_web_link = upload_image_to_folder(folder_ids[-1], plot_pdf_names, pdf_final_path)
        file_ids.append(file_id)
        file_web_links.append(file_web_link)

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

# resolve_TargetPlotsUploader('_','info',settings.case,settings.predicted_targets,settings.actual_targets,settings.dates)
