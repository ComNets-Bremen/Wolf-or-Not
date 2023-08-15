#!/usr/bin/env python3

"""
Compare the distributions for the polling: Which one makes more sense?
"""
import random
import matplotlib.pyplot as plt

num_images  = 100
num_polls   = 300

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Helvetica"
})

def Triangular():
    return random.triangular(0,1,0)

def Beta_01_1():
    return random.betavariate(0.1, 1)

def Beta_04_1():
    return random.betavariate(0.4, 1)

def Beta_06_1():
    return random.betavariate(0.6, 1)

def Beta_08_1():
    return random.betavariate(0.8, 1)

def Uniform():
    return random.uniform(0, 1)

col_labels = ["Probability Density Function (Normalized)", f"Images with n polls after {num_polls} polls"]

dists = {
        "Triangular"       : Triangular,
        r"Beta\\ {\small $\alpha=0.1$, $\beta=1$}" : Beta_01_1,
        r"Beta\\ {\small $\alpha=0.4$, $\beta=1$}" : Beta_04_1,
        r"Beta\\ {\small $\alpha=0.6$, $\beta=1$}" : Beta_06_1,
        r"Beta\\ {\small $\alpha=0.8$, $\beta=1$}" : Beta_08_1,
        "Uniform"           :Uniform,
        }

fig, axes = plt.subplots(nrows=len(dists), ncols=2, figsize=(12,8))

for ax, col in zip(axes[0], col_labels):
    ax.set_title(col)

for ax, dist in zip(axes[:, 0], dists.keys()):
    ax.set_ylabel(dist)

for ax in axes[:, 1]:
    ax.set_ylabel(r"\# Images")

data = {}
max_bin = 0
for dist in dists:
    images = [0 for _ in range(num_images)]
    for _ in range(num_polls):
        images.sort()
        i = int(round(dists[dist]()*(len(images)-1)))
        images[i] += 1

    counts = {}
    for i in range(max(images)+1):
        counts[i] = images.count(i)# / num_polls

    max_bin = max(max_bin, max(counts.keys()))
    data[dist] = counts

for num, dist in enumerate(dists):
    print(dist)
    plt.subplot(len(dists), 2, (num*2)+1)
    plt.hist([dists[dist]() for i in range(100000)], bins = 100, density=True)
    plt.yticks([], []) # Disable y-axis for PDF

    plt.subplot(len(dists), 2, (num*2)+2)
    plot_dict = {k:0 for k in range(max_bin+1)}
    d = data[dist]
    plot_dict.update(d)
    plt.bar(plot_dict.keys(), plot_dict.values())
    plt.xticks([i for i in range(0, max_bin+1)], minor=False)

fig.suptitle(f"Comparison of different Distributions: {num_polls} polls on {num_images} images")
plt.tight_layout()
plt.savefig("dist_comparison.pdf")
plt.savefig("dist_comparison.png")
plt.show()
