import argparse
import logging
import boto3
from botocore.exceptions import ClientError
from pathlib import Path
import logging
import os 
from PIL import Image

# We use argparse module to handle command-line interface
parser = argparse.ArgumentParser()
parser.add_argument("source", help="Bucket name with images to be analysed",
                    type=str)
parser.add_argument("destination", help="Bucket name where copying no transparent pixels images",
                    type=str)
parser.add_argument('--Access_key', help="Access key credential for AWS Conecction", default= None, type=str)
parser.add_argument('--secret_access_key', help="Access key credential for AWS Conecction", default= None, type=str)
args = parser.parse_args()

# We define a function that return True when the image has transparent pixels
def img_transparency(path):
        # Create a Image object from PIL
        img = Image.open(path) 
        # If an image does not have an alpha band, transparency may be specified in the info attribute with a “transparency” key
        # We need to add the condition "is not None" because if the image file has white defined as the transparency color (0) would resolve to False 
        if img.info.get("transparency", None) is not None:
            return True
        # If the image has a alpha band (alpha stands for transparency values) means that they have transparency. however it won't be specify in the info atributte so we create a list with the different alpha modes
        if img.mode in ['LA', 'PA', 'RGBA']:
            return True 
        return False


def ejerc_2(source, destination):
    
    # We add AWS credentials if needed 
    if (args.Access_key or args.secret_access_key) is not None:
        session = boto3.Session(
        aws_access_key_id=args.Access_key,
        aws_secret_access_key=args.secret_access_key
        )    
        s3 = session.client('s3')
    else:
        s3 = boto3.client('s3')
    # We list all the files information accesing to the 'Content' key
    try: 
        contents = s3.list_objects_v2(Bucket=source)['Contents']
    except s3.Client.exceptions.NoSuchBucket:
        print('No such Bucket')
    # We create a list with al the extension images that we want to process
    image_extensions = ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.tiff']
    # We take only those files that have the right extension (We will skip those files that are not image and we will process those that are)
    # We use Path fro Pathlib to extract the suffic of the file name and match it with our img extensions
    files = [i['Key'] for i in contents if Path(i['Key']).suffix in image_extensions]

    try:
        # We create a list with the objects corresponding to each file present in the 'Body' key after getting the object information
        image_files = [s3.get_object(
            Bucket=source,
            Key = file 
        )['Body'] for file in files]
    except s3.exceptions.NoSuchKey:
        print('no such Key')
    except s3.exceptions.InvalidObjectState:
        print('Invalid object State')


    # We map the img_transparency function to each object getting a list of booleans specifying whether the file has transparent pixels or not 
    transparency_files = list(map(img_transparency, image_files)) 

    # We concatenate the image path with its corresponding boolean with zip function
    for image, transparency in zip(files, transparency_files):
        # If the image has transparent pixels it will create a log file and the name of the image will be written using the loggin module
        if transparency:
            # It will create a new .log file in case it doesn' t exist. Otherwise, each logging.info will be appendded to the existing file 
            logging.basicConfig(filename="transparent_pixel_img.log", level=logging.INFO, format='%(message)s')
            logging.info(f"{Path(image).name}") # We take the name to only load the name. Otherwise, the log file will also contain the directory where the file is in 

        else:
        # We create a copy using copy_object 
            try: 
                s3.copy_object(
                    # Bucket where we want to copy the file 
                    Bucket=destination,
                    # Name of the file that we are going to copy 
                    Key=Path(image).name, #Same reason that in logging 
                    # Bucket where there is the image and its key 
                    CopySource= {'Bucket': source, 'Key': image})
            except s3.exceptions.ObjectNotInActiveTierError:
                print('The source object is not in the active tier')

    # One we have gone over all the image files of the bucket we upload the log file that has been created using upload_file function
    # We specify in log file that we have created, the bucket where we want to upload it, and in key the name for the uploaded file  
    s3.upload_file(Filename='transparent_pixel_img.log', Bucket=source,  Key=os.path.join(Path(files[0]).parent,'transparent_pixel_img.log'))
    # We use os.path.join() to upload the file in the same folder where they images(in case we have more folders that the image folder in that bucket)

if __name__ == "__main__":
   ejerc_2(args.source, args.destination)