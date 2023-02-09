#!/usr/bin/env python3
import sys
import pickle
import matplotlib.pyplot as plt

def main():
  
  if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]}  <pickled-results> <output.png>")
    sys.exit(-1)
  doplot(sys.argv[1], sys.argv[2])

def doplot(results, output):
  
  data = []  
  with open(results, "rb") as f:
    data.append(pickle.load(f))
  
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2)
  
    ax1.boxplot(data[0])
    ax2.violinplot(data[0], showmeans=True)
    plt.savefig(output)
    plt.show()
    print(max(data[0]))

if __name__ == "__main__":
  main()
