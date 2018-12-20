import os
from azure.storage.blob import BlockBlobService, PublicAccess


def get_block_service(account_name, account_key):
    # Create the BlockBlockService that is used to call the Blob service for the storage account
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