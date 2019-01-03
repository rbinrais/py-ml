import os
from azure.storage.blob import BlockBlobService, PublicAccess
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

def get_env_var(name):
    try:
       return os.getenv(name)
    except KeyError:
        return None


def upload_to_blob(file_name,full_path_to_file):
    container_name = get_env_var('AZURE_CONTAINER_NAME')
    blob = get_block_service_silent()
    upload_file_to_blob(blob,file_name,container_name,full_path_to_file)

def download_from_blob(file_name,full_path_to_file):
    container_name = get_env_var('AZURE_CONTAINER_NAME')
    blob = get_block_service_silent()
    download_file_from_blob(blob,file_name,container_name,full_path_to_file)

def get_block_service(account_name, account_key):
    # Create the BlockBlockService that is used to call the Blob service for the storage account
    block_blob_service = BlockBlobService(account_name, account_key) 
    return block_blob_service
   
def get_block_service_silent():
    # Create the BlockBlockService that is used to call the Blob service for the storage account
    account_key= get_env_var('AZURE_STORAGE_KEY')
    account_name = get_env_var('AZURE_STORAGE_ACCOUNT')

    block_blob_service = BlockBlobService(account_name, account_key) 
    return block_blob_service

def create_blob_container(block_blob_service, container_name):
    
    # Create a container called 'quickstartblobs'.
    block_blob_service.create_container(container_name) 

    # Set the permission so the blobs are public.
    block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)

def upload_file_to_blob(block_blob_service,file_name, container_name,full_path_to_file):
    create_blob_container(block_blob_service,container_name)
    print("Uploading file: "+full_path_to_file+" to azure blob storage: " + container_name)
     # Upload the created file, use filename for the blob name
    block_blob_service.create_blob_from_path(container_name,file_name, full_path_to_file)

def download_file_from_blob(block_blob_service,file_name, container_name,full_path_to_file):
     print("\nDownloading blob file to " + full_path_to_file)
     block_blob_service.get_blob_to_path(container_name, file_name, full_path_to_file)
