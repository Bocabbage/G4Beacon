import torch.nn as nn


class BasicGenerator(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(BasicGenerator, self).__init__()
        self.net_ = nn.Sequential(
            nn.Linear(input_dim, 1024),
            nn.ReLU(),
            nn.Linear(1024, 1024),
            nn.ReLU(),
            nn.Linear(1024, output_dim),
            nn.Tanh()
        )

    def forward(self, x):
        return self.net_(x)


class BasicDiscriminator(nn.Module):
    def __init__(self, input_dim):
        super(BasicDiscriminator, self).__init__()
        self.net_ = nn.Sequential(
            nn.Linear(input_dim, 1024),
            nn.LeakyReLU(0.2),
            nn.Linear(1024, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.net_(x)
