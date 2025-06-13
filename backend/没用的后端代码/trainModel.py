import torch
from torch.utils.data import Dataset, DataLoader
import json
import numpy as np
import cv2
from sklearn.preprocessing import LabelEncoder

#---------------------数据加载和预处理
# 数据集类
class PostureDataset(Dataset):
    def __init__(self, json_file, transform=None):
        with open(json_file, 'r') as f:
            self.data = json.load(f)

        self.transform = transform
        self.label_encoder = LabelEncoder()
        # 将标签转为数字
        self.labels = self.label_encoder.fit_transform([entry['label'] for entry in self.data])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        image_name = self.data[idx]['image']
        landmarks = np.array([landmark['x'] for landmark in self.data[idx]['landmarks']])
        pressure_data = np.array(self.data[idx]['pressure_data'])

        # 读取图像
        image = cv2.imread(f'path_to_images/{image_name}')
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (224, 224))  # 调整图像尺寸

        if self.transform:
            image = self.transform(image)

        label = self.labels[idx]

#-------------------多模态网络设计，landmards卷积神经网络cnn,压力cf

import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

class MultiModalFusionNetwork(nn.Module):
    def __init__(self, num_classes):
        super(MultiModalFusionNetwork, self).__init__()

        # 图像部分（CNN）
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(64 * 56 * 56, 128)  # 假设图片尺寸为224x224

        # 压力数据部分（全连接层）
        self.fc2 = nn.Linear(100, 64)  # 假设压力数据有100个值

        # 融合部分
        self.fc3 = nn.Linear(128 + 64, 64)
        self.fc4 = nn.Linear(64, num_classes)

    def forward(self, x_image, x_pressure):
        # 图像部分
        x_image = self.pool(F.relu(self.conv1(x_image)))
        x_image = self.pool(F.relu(self.conv2(x_image)))
        x_image = x_image.view(x_image.size(0), -1)  # 展平
        x_image = F.relu(self.fc1(x_image))

        # 压力数据部分
        x_pressure = F.relu(self.fc2(x_pressure))

        # 融合部分
        x = torch.cat((x_image, x_pressure), dim=1)  # 拼接
        x = F.relu(self.fc3(x))
        x = self.fc4(x)

        return x


