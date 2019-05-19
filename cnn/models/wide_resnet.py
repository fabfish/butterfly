import torch
import torch.nn as nn
import torch.nn.init as init
import torch.nn.functional as F
from torch.autograd import Variable

import sys
import numpy as np

from cnn.models.butterfly_conv import ButterflyConv2d
from cnn.models.low_rank_conv import LowRankConv2d

def conv3x3(in_planes, out_planes, stride=1):
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride, padding=1, bias=True)

def conv_init(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        init.xavier_uniform(m.weight, gain=np.sqrt(2))
        init.constant(m.bias, 0)
    elif classname.find('BatchNorm') != -1:
        init.constant(m.weight, 1)
        init.constant(m.bias, 0)

class wide_basic(nn.Module):
    def __init__(self, in_planes, planes, dropout_rate, stride=1, structure_type=None, **kwargs):
        super(wide_basic, self).__init__()
        self.bn1 = nn.BatchNorm2d(in_planes)
        if structure_type == 'B':
            self.conv1 = ButterflyConv2d(in_planes, planes, kernel_size=3, stride=stride,
                                         padding=1, bias=True, ortho_init=True, **kwargs)
        elif structure_type == 'LR':
            # Low rank should match the number of parameters of butterfly
            rank = kwargs.get('rank', 1)
            self.conv1 = LowRankConv2d(in_planes, planes, kernel_size=3, stride=stride, padding=1, bias=True, rank=rank)
        else:
            self.conv1 = nn.Conv2d(in_planes, planes, kernel_size=3, padding=1, bias=True)
        self.dropout = nn.Dropout(p=dropout_rate)
        self.bn2 = nn.BatchNorm2d(planes)
        if structure_type == 'B':
            self.conv2 = ButterflyConv2d(planes, planes, kernel_size=3, stride=1, padding=1,
                                         bias=True, ortho_init=True, **kwargs)
        elif structure_type == 'LR':
            rank = kwargs.get('rank', 1)
            self.conv2 = LowRankConv2d(planes, planes, kernel_size=3, stride=1, padding=1, bias=False, rank=rank)
        else:
            self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=stride, padding=1, bias=True)

        self.shortcut = nn.Sequential()
        if stride != 1 or in_planes != planes:
            if structure_type == 'B':
                conv = ButterflyConv2d(in_planes, planes, kernel_size=1, stride=stride,
                                        bias=True, ortho_init=True, **kwargs)
            elif structure_type == 'LR':
                rank = kwargs.get('rank', 1)
                conv = LowRankConv2d(in_planes, planes, kernel_size=1, stride=stride, bias=False, rank=rank)
            else:
                conv = nn.Conv2d(in_planes, planes, kernel_size=1, stride=stride, bias=True)
            self.shortcut = nn.Sequential(
                conv
            )

    def forward(self, x):
        out = self.dropout(self.conv1(F.relu(self.bn1(x))))
        out = self.conv2(F.relu(self.bn2(out)))
        out += self.shortcut(x)

        return out

class Wide_ResNet(nn.Module):
    def __init__(self, depth, widen_factor, dropout_rate, num_classes, structure_type=None, **kwargs):
        super(Wide_ResNet, self).__init__()
        self.in_planes = 16

        assert ((depth-4)%6 ==0), 'Wide-resnet depth should be 6n+4'
        n = (depth-4)//6
        k = widen_factor

        # print('| Wide-Resnet %dx%d' %(depth, k))
        nStages = [16, 16*k, 32*k, 64*k]

        self.conv1 = conv3x3(3,nStages[0])
        self.layer1 = self._wide_layer(wide_basic, nStages[1], n, dropout_rate, stride=1)
        self.layer2 = self._wide_layer(wide_basic, nStages[2], n, dropout_rate, stride=2)
        self.layer3 = self._wide_layer(wide_basic, nStages[3], n, dropout_rate, stride=2, structure_type=structure_type, **kwargs)
        self.bn1 = nn.BatchNorm2d(nStages[3], momentum=0.9)
        self.linear = nn.Linear(nStages[3], num_classes)

    def _wide_layer(self, block, planes, num_blocks, dropout_rate, stride, structure_type=None, **kwargs):
        strides = [stride] + [1]*(num_blocks-1)
        layers = []

        for stride in strides:
            layers.append(block(self.in_planes, planes, dropout_rate, stride, structure_type, **kwargs))
            self.in_planes = planes

        return nn.Sequential(*layers)

    def forward(self, x):
        out = self.conv1(x)
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = F.relu(self.bn1(out))
        out = F.avg_pool2d(out, 8)
        out = out.view(out.size(0), -1)
        out = self.linear(out)

        return out

if __name__ == '__main__':
    net=Wide_ResNet(28, 8, 0.0, 10)
    y = net(Variable(torch.randn(1,3,32,32)))

    print(y.size())

def WideResNet28(structure_type='B', **kwargs):
    return Wide_ResNet(28, 2, 0.0, 10, structure_type=structure_type, **kwargs)
