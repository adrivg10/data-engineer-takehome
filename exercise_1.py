
from PIL import Image, ImageDraw
import cv2
import numpy as np 
import os
from pathlib import Path
import argparse

# We use argparse module to handle command-line interface
parser = argparse.ArgumentParser()
parser.add_argument("input_file", help="path of the image that is goign to be analysed",
                    type=str)
parser.add_argument("directory_path", help="Directory where you want to save the extracted faces",
                    type=str)
parser.add_argument("--extra", default=False, help='Make a copy of the image with the face detected ', type=bool)
args = parser.parse_args()

# We get the  Haar Cascade classifier from OpenCv
face_classifier = cv2.CascadeClassifier(
f"{cv2.data.haarcascades}haarcascade_frontalface_alt.xml")

def face_detector(input_path, output_directory, marked_faces=False):
     # We create a Image object from PIL
    img = Image.open(input_path)
    # We convert the image to greyscale ( to simplify calculations and remove redundancies) and apply the classifier
    gs_image = img.convert(mode='L')
    faces = face_classifier.detectMultiScale(np.array(gs_image), 1.35, 5)
    detected_faces = []  #. As we are going to need to count the faces detected we can reuse this list (it is to make the extra work, not needed for the task )
    # We use enumerate to get the number of the sace that has been detected altogether with the coordinates of the face detected
    for count, (x,y,w,h) in enumerate(faces): 
        # Not needed for this task we append the four coordinates of the face detected
        detected_faces.append([(x,y),(x+w, y+h)])
        # We crop the face detected from the original image
        cropped_img = img.crop((x,y,x+w,y+h))
        # We create the output file using os.path.join to join the output directory with the name of the output face(img.format will add the extension to the image)
        face_file = os.path.join(output_directory, f'{Path(input_path).stem}_face_{count+1}.{img.format.lower()}')
        # We check if the pathlife already exists and if it is the case we dont copy it again (we can decide to save it again if we want)
        if os.path.exists(face_file):
            # cropped_img.save(face_file) --> If we want to change the old one for a new one 
            pass
        else:
            # We create a folder if the output_directory doesn' t exist. Otherwise, nothing will happen
            os.makedirs(output_directory, exist_ok=True)
            # We save the cropped image 
            cropped_img.save(face_file)

    # Extra functionality: It will save a copy of the image with a rectangle in the faces that were detected 
    if args.extra:
        # We use the Imagedraw object from the original image
        img_2 = ImageDraw.Draw(img)
        # We draw rectangles iterating through all the images (we appended the 4 coordinates for each face detected during the previous loop) 
        list(img_2.rectangle(i) for i in detected_faces)
        # We save final image 
        img.save(os.path.join(output_directory, f'{Path(input_path).stem}_marked_faces.{img.format.lower()}')) 
    # We print the number of faces detected and return it in case we want to add the value to a variable 
    print(f'{len(detected_faces)} faces were detected')
    return len(detected_faces)

if __name__ == "__main__":
    face_detector(args.input_file, args.directory_path, args.extra)
