# -*- coding: utf-8 -*-
"""medleaf_test.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18hsQhn873mcrlw9Y7-yn3LrJJKKt7pFu

# **Medical Leaf Classification**
This is notebook for medical leaf image classification. For "Tumbuhin" app.
<br>
This classification used TensorFlow-Lite Model Maker
<br>
<br>
for more detail about TFLite Model Maker, click link below:
<br>
https://www.tensorflow.org/lite/guide/model_maker
<br>
<br>
*NB: Please try this notebook on Google Colab*
<br>
<br>
### **1). Install TensorFlow-Lite Model Maker**
Run cell below to ensure your machine have installed tflite-model-maker library
"""

!pip install tflite-model-maker

"""### **2). Import Required Libraries**
Import tflite-model-maker below for image processing preparation
"""

import matplotlib.pyplot as plt
import numpy as np

import os

import seaborn as sn
from sklearn.metrics import confusion_matrix

import tensorflow as tf
assert tf.__version__.startswith('2')

from tflite_model_maker import model_spec
from tflite_model_maker import image_classifier
from tflite_model_maker.config import ExportFormat
from tflite_model_maker.config import QuantizationConfig
from tflite_model_maker.image_classifier import DataLoader

"""### **3). Locate the Datasets**
Here, you must locate the datasets location/directory.
"""

image_path = "/content/drive/MyDrive/Datasets"

"""### **4). Load the Datasets**
Load datasets using DataLoader
"""

data = DataLoader.from_folder(image_path)

"""### **5). Distribute/split the Datasets**
Split the datasets into train-test-validation

Train 80% per class/labels

Test 10% per class/labels

Validation 10% per class/labels
"""

train_data, rest_data = data.split(0.8) # 80% for training
validation_data, test_data = rest_data.split(0.5) # 10% for testing, 10% for validation

"""### **6). Display Random Images**
Display random images from datasets before continue
"""

plt.figure(figsize=(15, 15))
for i, (image, label) in enumerate(
    data.gen_dataset().unbatch().take(25)):
  plt.subplot(5, 5, i+1)
  plt.xticks([])
  plt.yticks([])
  plt.grid(False)
  plt.imshow(image.numpy(), cmap=plt.cm.gray)
  plt.xlabel(data.index_to_label[label.numpy()])

plt.show()

"""### **7). Use Pre-trained Model**
Here, we use EfficientNet Lite1 as a base model for image classification and build custom tflite model

More info, click here:
<br>
https://blog.tensorflow.org/2020/03/higher-accuracy-on-vision-models-with-efficientnet-lite.html
"""

efficientnet_model = model_spec.get("efficientnet_lite1")

"""### **8). Training and Creating**
Here, we begin train the entire datasets and also create custom model based on pre-trained model
"""

model = image_classifier.create(train_data,
                                epochs=10,
                                validation_data=validation_data,
                                use_augmentation=True,
                                shuffle=True,
                                model_spec=efficientnet_model)

"""### **9). Display Model Summary**"""

model.summary()

"""### **10). Display Model Training-Validation Loss and Accuracy**"""

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline

#Loss graph
plt.figure(figsize=(8, 6))
plt.plot(model.history.history["loss"])
plt.plot(model.history.history["val_loss"])
plt.title("Loss")
plt.ylabel("Losses")
plt.xlabel("Epochs")
plt.grid(True)
plt.legend(["training", "validation"], loc="upper left")
plt.show()

#Accuracy graph
plt.figure(figsize=(8, 6))
plt.plot(model.history.history["accuracy"])
plt.plot(model.history.history["val_accuracy"])
plt.title("Accuracy")
plt.ylabel("Accuracies")
plt.xlabel("Epochs")
plt.grid(True)
plt.legend(["training", "validation"], loc="upper left")
plt.show()

"""### **11). Evaluate the Model**
Evaluate the model using test data
"""

model.evaluate(test_data)

"""### **12). Display Random Predicted Images**
Display info about predicted image, we can see if the image was predicted correctly or not
"""

def get_label_color(predict_label, actual_label):
  if predict_label == actual_label:
    return "black"
  else:
    return "red"

plt.figure(figsize=(20, 20))
predicts = model.predict_top_k(test_data)
for i, (image, label) in enumerate(
    test_data.gen_dataset().unbatch().take(100)):
  ax = plt.subplot(10, 10, i+1)
  plt.xticks([])
  plt.yticks([])
  plt.grid(False)
  plt.imshow(image.numpy(), cmap="Greys")

  predict_label = predicts[i][0][0]
  color = get_label_color(predict_label,
                          test_data.index_to_label[label.numpy()])
  ax.xaxis.label.set_color(color)
  plt.xlabel("Predicted:\n{}".format(predict_label))

plt.show()

"""### **13). Display the Confusion Matrix**
Display info about prediction result in confusion matrix
"""

labels = os.listdir(os.path.join(image_path))
labels.sort()

label_dicts = {}

for i in range(len(labels)):
  label_dicts[labels[i]] = i

predicts = model.predict_top_k(test_data)
predict_labels = [ label_dicts[predicts[i][0][0]]
                  for i, (image, label) in enumerate(test_data.gen_dataset().unbatch()) ]

actual_labels = [ label.numpy()
                  for i, (image, label) in enumerate(test_data.gen_dataset().unbatch()) ]

plt.figure(figsize=(15, 10))
medleaf_cm = confusion_matrix(y_true=actual_labels, y_pred=predict_labels)
medleaf_cm = medleaf_cm / medleaf_cm.sum(axis=1) # To display conf. matrix in percetage %

sn.heatmap(medleaf_cm, annot=True, cmap="Greens")

"""### **14). Deployment**
Export/deploy into TFLite Model File. Use for Android "Tumbuhin" app
"""

model.export(export_dir=".")

"""For exporting labels only"""

model.export(export_dir=".", export_format=ExportFormat.LABEL)

"""### **15). Evaluate The TFLite Model**
Evaluate the TFLite Model with test data (again)
"""

model.evaluate_tflite("model.tflite", test_data)

"""### **16). Post Training/Model Quantization (Optional)**
Post-training quantization is a conversion technique that can reduce model size and inference latency, while also improving CPU and hardware accelerator latency, with little degradation in model accuracy. Thus, it's widely used to optimize the model.
<br>
<br>
More info about post training/quantization, click link below:
<br>
https://www.tensorflow.org/lite/performance/post_training_quantization
"""

quantizer = QuantizationConfig.for_int8(representative_data=test_data)

model.export(export_dir=".", quantization_config=quantizer)

model.evaluate_tflite("model.tflite", test_data)