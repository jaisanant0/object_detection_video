import sys
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
import numpy as np
import os
import argparse
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import cv2

parser = argparse.ArgumentParser()

parser.add_argument('model_name', help="COCO pretrained model to be used")
parser.add_argument('video_file', help ="path of video file")
parser.add_argument('save_output', help ="path of save the output file")
parser.add_argument('have_model', help ="Is the model present in directory (Y/N)", choices=['Y','N'])

args = parser.parse_args()


#sys.path.append("..")
cap = cv2.VideoCapture(args.video_file) #videocapture object
fps = 30
#fourcc = cv2.VideoWriter_fourcc(*'DIVX')
#fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(args.save_output,fourcc,fps,(int(cap.get(3)), int(cap.get(4))),True)
#success = out.open(output_video.avi',-1,fps,capSize,True)

MODEL_NAME = args.model_name
MODEL_FILE = MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABELS = os.path.join('object_detection/data', 'mscoco_label_map.pbtxt')


NUM_CLASSES = 90

if(args.have_model == 'N') :
        print("Retrieving the pretrained model " + MODEL_NAME + '.'*15)

        opener = urllib.request.URLopener()
        opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
        tar_file = tarfile.open(MODEL_FILE)

        print("Extracting the ta " + '.'*20)
        for file in tar_file.getmembers():
                file_name = os.path.basename(file.name)
                if 'frozen_inference_graph.pb' in file_name:
                        tar_file.extract(file, os.getcwd())



detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')


label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)


def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)


with detection_graph.as_default():
  with tf.Session(graph=detection_graph) as sess:
    while cap.isOpened(): #checking the initialization of capture
      ret, image_np = cap.read()
      if ret == True:
          image_np_expanded = np.expand_dims(image_np, axis=0)
          image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
          boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
          scores = detection_graph.get_tensor_by_name('detection_scores:0')
          classes = detection_graph.get_tensor_by_name('detection_classes:0')
          num_detections = detection_graph.get_tensor_by_name('num_detections:0')
          (boxes, scores, classes, num_detections) = sess.run(
              [boxes, scores, classes, num_detections],
              feed_dict={image_tensor: image_np_expanded})
          vis_util.visualize_boxes_and_labels_on_image_array(
              image_np,
              np.squeeze(boxes),
              np.squeeze(classes).astype(np.int32),
              np.squeeze(scores),
              category_index,
              use_normalized_coordinates=True,
              line_thickness=8)
          out.write(image_np)
          cv2.imshow('Output',image_np)
          if cv2.waitKey(1) & 0xFF == ord('q'): #keyboard binding function
              cv2.destroyAllWindows()
              break
      else:
          break
        
cap.release()
out.release()
cv2.destroyAllWindows()


