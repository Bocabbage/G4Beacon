#! /usr/bin python
# -*- coding: utf-8 -*-
# Update date: 2021/10/23
# Author: Zhuofan Zhang
import os
import json
import argparse
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import transforms
from dataset import g4SeqEnv
from model import BasicGenerator, BasicDiscriminator

# def join_path(firstpath, secondpath):
#     try:
#         path = os.path.join(firstpath, secondpath)
#     except TypeError:
#         path = None
#     return path


#### Loss function ####
def d_loss_function(inputs, targets):
    return nn.BCELoss()(inputs, targets)


def g_loss_function(inputs):
    targets = torch.ones(inputs.shape[0], 1).to(device)
    return nn.BCELoss()(inputs, targets)


plt.switch_backend('agg')
parser = argparse.ArgumentParser()
parser.add_argument('--json', type=str, help="Training config json.")
args = parser.parse_args()

with open(args.json, 'r') as json_file:
    json_data = json.load(json_file)

# seed = json_data['seed']
# torch.manual_seed(seed)

#### GPU setting ####
device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

#### Model ####
ginput_size = json_data['ginput_size']
goutput_size = json_data['gouput_size']
generator = BasicGenerator(ginput_size, goutput_size).to(device)
discriminator = BasicDiscriminator(goutput_size).to(device)


#### Load data ####
vg4seq = json_data['vg4seq']
vg4atac = json_data['vg4atac']
vg4bs = json_data['vg4bs']

# Load Data
g4_dataset = g4SeqEnv(
    vg4seq,
    vg4atac,
    vg4bs,
    None
)

for config in json_data['config_list']:
    #### Utils setting ####
    output_dir = config["checkpoint_save_dir"]
    if os.path.isdir(output_dir) is not True:
        os.makedirs(output_dir)
    log_file = open(config["log_file"], 'w+')

    #### Hyper-paramaters config ####
    epochs = config['epochs']
    batch_size = config['batch_size']
    lr = config['lr']

    #### Data Loader ####
    train_loader = DataLoader(g4_dataset, batch_size=batch_size, shuffle=True)

    #### Optimizer ####
    if config['g_optim'] == 'Adam':
        g_optim = optim.Adam(generator.parameters(), lr=lr)
    if config['d_optim'] == 'Adam':
        d_optim = optim.Adam(discriminator.parameters(), lr=lr)

    #### Training ####
    train_loader_len = len(train_loader)
    for epoch in range(1, epochs + 1):
        g_loss_epoch = []
        d_loss_epoch = []
        for batch_idx, data in enumerate(train_loader):
            # True training-samples for D
            real_inputs = data[0].to(device)
            real_inputs = real_inputs.view(-1, goutput_size)
            real_outputs = discriminator(real_inputs)
            real_labels = torch.ones(real_inputs.shape[0], 1).to(device)

            # Fake training-samples for D
            noise_inputs = (torch.rand(real_inputs.shape[0], ginput_size))
            noise_inputs = noise_inputs.to(device)
            fake_inputs = generator(noise_inputs)
            fake_outputs = discriminator(fake_inputs)
            fake_labels = torch.zeros(fake_inputs.shape[0], 1).to(device)

            outputs = torch.cat([real_outputs, fake_outputs], 0)
            labels = torch.cat([real_labels, fake_labels], 0)

            # Step1: Train the Discriminator
            d_optim.zero_grad()
            d_loss = d_loss_function(outputs, labels)
            d_loss.backward()
            d_optim.step()

            # Step2: Train the Generator
            noise_inputs = (torch.rand(real_inputs.shape[0], ginput_size))
            noise_inputs = noise_inputs.to(device)
            fake_inputs = generator(noise_inputs)
            fake_outputs = discriminator(fake_inputs)
            g_optim.zero_grad()
            g_loss = g_loss_function(fake_outputs)
            g_loss.backward()
            g_optim.step()

            d_loss_epoch.append(d_loss)
            g_loss_epoch.append(g_loss)

        log_file.write((
            f"[{epoch}/{epochs}]\t"
            f"avg_D_loss: {torch.mean(torch.FloatTensor(d_loss_epoch)):.3f}\t"
            f"avg_G_loss: {torch.mean(torch.FloatTensor(g_loss_epoch)):.3f}\n"
        ))

        if epoch % 10 == 0:
            output_path = os.path.join(output_dir, f"generator_epoch{epoch}.pth")
            torch.save(generator, output_path)

    log_file.close()
