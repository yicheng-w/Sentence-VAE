import os
import json
import torch
import random
import argparse

def main(args):
    with open(os.path.join(args.output_dir, "ptb.valid.txt"), "w") as out_file:
        pos_dir = os.path.join(args.sentiment_dir, "pos")
        neg_dir = os.path.join(args.sentiment_dir, "neg")

        for file in os.listdir(pos_dir):
            if random.random() > args.percentage:
                continue
            out_file.write(
                open(os.path.join(pos_dir, file)).read().replace("\n", " ") + "\n")
        for file in os.listdir(neg_dir):
            if random.random() > args.percentage:
                continue
            out_file.write(
                open(os.path.join(neg_dir, file)).read().replace("\n", " ") + "\n")

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--sentiment_dir", type=str)
    parser.add_argument("--output_dir", type=str)
    parser.add_argument("--percentage",  type=float, default=0.1)
    args = parser.parse_args()

    main(args)


