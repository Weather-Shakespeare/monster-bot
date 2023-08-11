# -*- coding: utf-8 -*-
"""WeaHa_coco.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1a-R9FFqNDIbh_FJPxABBShE0_-iimrOu
"""

!pip install torchmetrics

from google.colab import drive
import torch

from torch.utils.data import Dataset, DataLoader,ConcatDataset,random_split
import torchvision
from PIL import Image
from pycocotools.coco import COCO

drive.mount('/content/drive')
if torch.cuda.is_available():  dev = "cuda"
else:  dev = "cpu"

import os
class ImgData_aluminium(Dataset):
    def __init__(self,root,alu_annotation,transforms=None):
        self.root_dir = root
        self.transforms = transforms
        self.coco = COCO(alu_annotation)
        self.ids = list(self.coco.imgs.keys())
        self.num_objs = 1
    def __len__(self):
        return len(self.ids)

    def __getitem__(self,index):
        coco = self.coco
        img_id = self.ids[index]
        ann_ids = coco.getAnnIds(imgIds=img_id)
        coco_annotation = coco.loadAnns(ann_ids)
        path = coco.loadImgs(img_id)[0]['file_name']
        path = path.replace("\\","")
        print(os.path.join(self.root_dir,path))
        img = Image.open(os.path.join(self.root_dir,path))
        boxes = []
        for i in range(self.num_objs):
            xmin = coco_annotation[i]['bbox'][0]
            ymin = coco_annotation[i]['bbox'][1]
            xmax = xmin + coco_annotation[i]['bbox'][2]
            ymax = ymin + coco_annotation[i]['bbox'][3]
            boxes.append(xmin)
            boxes.append(ymin)
            boxes.append(xmax)
            boxes.append(ymax)

        boxes = torch.as_tensor([boxes],dtype = torch.float32)
        labels = []
        for i in range(self.num_objs):
            labels.append(coco_annotation[i]['category_id'])
        labels = torch.as_tensor(labels,dtype=torch.int64)
        areas = []
        for i in range(self.num_objs):
            areas.append(coco_annotation[i]['area'])
        areas = torch.as_tensor(areas, dtype=torch.float32)

        # Annotation is in dictionary format
        my_annotation = {}
        my_annotation["image_id"] = torch.as_tensor(img_id)
        my_annotation["boxes"] = boxes
        #my_annotation["area"] = areas
        my_annotation["labels"] = labels

        if self.transforms is not None:
            img = self.transforms(img)

        return img, my_annotation

import json
import regex
class ImgData_bottle_cup(Dataset):
    def __init__(self,root,transform):
        self.root_dir = root
        print(self.root_dir)
        self.transforms = transform
        self.file_list = [os.path.splitext(filename)[0] for filename in os.listdir(self.root_dir)]
        self.categories = ['bottle','cup']
        pass
    def __getitem__(self,index):
        file_name = self.file_list[index]
        img_file_name = file_name + '.jpg'
        json_file_name = file_name + '.json'
        with open(os.path.join(self.root_dir,json_file_name), 'r') as j:
            annotation = json.loads(j.read())

        xmin = annotation[0]['bbox'][0]
        ymin = annotation[0]['bbox'][1]
        xmax = xmin + annotation[0]['bbox'][2]
        ymax = ymin + annotation[0]['bbox'][3]
        boxes = [xmin,ymin,xmax,ymax]
        boxes = torch.as_tensor([boxes],dtype=torch.float32)

        labels = torch.as_tensor([1 if annotation[0]['label'] == 'cup' else 2])
        #img_id = torch.as_tensor(annotation[''])
        area = torch.as_tensor([(annotation[0]['bbox'][2] - annotation[0]['bbox'][0]) * (annotation[0]['bbox'][3]-annotation[0]['bbox'][1])])
        my_annotation = {}

        my_annotation['image_id'] = torch.as_tensor(index)
        my_annotation['boxes'] = boxes
        #my_annotation['area'] = area
        my_annotation['labels'] = labels

        img = Image.open(os.path.join(self.root_dir,img_file_name))
        if self.transforms is not None:
            img = self.transforms(img)

        return img, my_annotation
    def __len__(self):
        return len(self.file_list)

root_dir = '/content/drive/MyDrive/WeaHa_dataset/'
alu_coco = '/content/drive/MyDrive/WeaHa_dataset/result.json'
aluminium_box = ImgData_aluminium(root_dir,alu_coco,torchvision.transforms.ToTensor())
bottle = ImgData_bottle_cup(os.path.join(root_dir+'bottle/'),torchvision.transforms.ToTensor())
cup = ImgData_bottle_cup(os.path.join(root_dir+'cup/'),torchvision.transforms.ToTensor())

dataset = ConcatDataset([aluminium_box,bottle,cup])
train_set,val_set = random_split(dataset,[0.8,0.2])

def collate_fn(batch):
    return tuple(zip(*batch))

train_data_loader = DataLoader(train_set,batch_size=6,num_workers=4,collate_fn=collate_fn)
val_data_loader = DataLoader(val_set,batch_size=6,num_workers=4,collate_fn=collate_fn)

for imgs, annotations in train_data_loader:
    imgs = list(img.to(dev) for img in imgs)
    annotations = [{k: v.to(dev) for k, v in t.items()} for t in annotations]
    print(annotations)

from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
import torchmetrics
from torchmetrics.detection.mean_ap import MeanAveragePrecision
mAP_metrics = MeanAveragePrecision()

def get_model_instance_segmentation(num_classes):
    # load an instance segmentation model pre-trained pre-trained on COCO
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=False)
    # get number of input features for the classifier
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    # replace the pre-trained head with a new one
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    return model

def validation_step():
    pass

# 2 classes; Only target class or background
num_classes = 3
num_epochs = 10
model = get_model_instance_segmentation(num_classes)

# move model to the right device
model.to(dev)

# parameters
params = [p for p in model.parameters() if p.requires_grad]
optimizer = torch.optim.SGD(params, lr=0.005, momentum=0.9, weight_decay=0.0005)

len_dataloader = len(train_data_loader)
train_loss_list = []
val_loss_list = []
val_mAP_list = []

for epoch in range(num_epochs):
    model.train()
    i = 0
    total_loss = 0
    for imgs, annotations in train_data_loader:
        i += 1
        imgs = list(img.to(dev) for img in imgs)
        annotations = [{k: v.to(dev) for k, v in t.items()} for t in annotations]
        loss_dict = model(imgs, annotations)
        losses = sum(loss for loss in loss_dict.values())
        total_loss += losses.item()
        optimizer.zero_grad()
        losses.backward()
        optimizer.step()
    print(loss_dict)

    train_loss = total_loss / len_dataloader
    train_loss_list.append(train_loss)
    model.eval()
    with torch.no_grad():
        val_mAP = 0.0
        val_total_loss = 0
        val_epoch_loss = []
        for val_imgs, val_annotations in val_data_loader:
            val_imgs = list(img.to(dev) for img in val_imgs)
            val_annotations = [{k: v.to(dev) for k, v in t.items()} for t in val_annotations]
            print('validation:',val_annotations)
            val_loss_dict = model(val_imgs, val_annotations)
            mAP_metrics.update(val_loss_dict,val_annotations)
        val_mAP = mAP_metrics.compute()
        #val_loss_list.append(val_mAP)
        val_mAP_list.append(val_mAP)
    #print(f'Epoch {epoch+1}/{num_epochs}, Training Loss: {train_loss}, Validation Loss: {val_loss}, Validation mAP: {val_mAP}')

import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot(train_loss_list)
plt.title('Training loss of model')

print(val_mAP_list)

mAP_score = []
for item in val_mAP_list:
    mAP_score.append(item['map'])
print(mAP_score)

import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot(mAP_score)
plt.title('validation mAP score of model')

from google.colab import drive
drive.mount('/content/drive')

torch.save(model,'/content/drive/MyDrive/WeaHa_dataset/model.pt')

torch.save(model.state_dict(),'/content/drive/MyDrive/WeaHa_dataset/model_state_dict.pt')