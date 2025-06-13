import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from sklearn.model_selection import train_test_split

# 假设你的数据已经准备好
# landmarks_data: (N, 34) 其中 34 是 17 个关键点的 3 个坐标值
# pressure_data: (N, 100) 假设每个样本有 100 个压力传感器的值
# y: 标签数据，形状为 (N,) 例如健康与不健康分类，2 分类任务

N = 1000  # 假设有1000个样本
landmarks_data = np.random.rand(N, 34)  # 每个样本34个关键点坐标
pressure_data = np.random.rand(N, 100)  # 每个样本有100个压力传感器的数据
y = np.random.randint(2, size=N)  # 假设目标是二分类

# 合并数据：将 landmarks 和 pressure_data 拼接成一个大矩阵
X = np.concatenate([landmarks_data, pressure_data], axis=1)

# 将数据转换为 PyTorch 张量
X_tensor = torch.tensor(X, dtype=torch.float32)
y_tensor = torch.tensor(y, dtype=torch.long)  # 使用 long 类型表示分类标签

# 划分训练集与测试集
X_train, X_test, y_train, y_test = train_test_split(X_tensor, y_tensor, test_size=0.2, random_state=42)


# 自定义数据集
class PostureDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


# 创建训练和测试数据加载器
train_dataset = PostureDataset(X_train, y_train)
test_dataset = PostureDataset(X_test, y_test)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)


# 定义CNN模型
class PostureCNN(nn.Module):
    def __init__(self, input_size):
        super(PostureCNN, self).__init__()
        self.conv1 = nn.Conv1d(1, 32, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool1d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv1d(32, 64, kernel_size=3, stride=1, padding=1)
        self.fc1 = nn.Linear(64 * (input_size // 2 // 2), 128)  # 计算输出的维度
        self.fc2 = nn.Linear(128, 1)  # 输出层（用于二分类）

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = x.view(-1, 64 * (x.size(2)))  # 展平为一维向量
        x = torch.relu(self.fc1(x))
        x = torch.sigmoid(self.fc2(x))  # 输出概率
        return x


# 初始化模型
model = PostureCNN(input_size=X_train.shape[1])

# 损失函数与优化器
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 训练模型
num_epochs = 10
for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    for inputs, labels in train_loader:
        # 添加维度，使其适应 CNN
        inputs = inputs.unsqueeze(1)  # (batch_size, 1, feature_size)

        optimizer.zero_grad()

        outputs = model(inputs)
        loss = criterion(outputs.squeeze(), labels.float())
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

        # 计算准确率
        predicted = (outputs > 0.5).long()  # 通过0.5来判断预测为1还是0
        correct += (predicted.squeeze() == labels).sum().item()
        total += labels.size(0)

    epoch_loss = running_loss / len(train_loader)
    epoch_acc = correct / total
    print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {epoch_loss:.4f}, Accuracy: {epoch_acc:.4f}")

# 保存训练好的模型
torch.save(model.state_dict(), 'posture_model.pth')

