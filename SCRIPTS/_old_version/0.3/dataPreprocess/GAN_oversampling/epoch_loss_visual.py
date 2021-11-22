import argparse
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')
parser = argparse.ArgumentParser()
parser.add_argument('--log', type=str, help="input training log.")
parser.add_argument('--out', type=str, help="output loss visualization pic path.")
args = parser.parse_args()


x_s = []
dloss_s = []
gloss_s = []

with open(args.log, 'r') as rfile:
    for idx, line in enumerate(rfile.readlines()):
        _, avg_dloss, avg_gloss = line.strip().split("\t")
        avg_dloss = float(avg_dloss.split(": ")[1])
        avg_gloss = float(avg_gloss.split(": ")[1])

        x_s.append(idx)
        dloss_s.append(avg_dloss)
        gloss_s.append(avg_gloss)

fig, ax = plt.subplots(figsize=(10, 10))
ax.plot(x_s, dloss_s, 'r-', label="D_loss")
ax.plot(x_s, gloss_s, 'b-', label="G_loss")
ax.set_xlabel("epoch")
ax.set_ylabel("training-loss")
ax.legend()
ax.set_title("Training Loss of D/G in GAN")

fig.savefig(args.out)
