import os
import json
import h5py
import torch
import argparse
import numpy as np

from model import SentenceVAE
from utils import to_var, idx2word, interpolate


def main(args):

    with open(args.data_dir+'/ptb.vocab.json', 'r') as file:
        vocab = json.load(file)

    w2i, i2w = vocab['w2i'], vocab['i2w']

    model = SentenceVAE(
        vocab_size=len(w2i),
        sos_idx=w2i['<sos>'],
        eos_idx=w2i['<eos>'],
        pad_idx=w2i['<pad>'],
        unk_idx=w2i['<unk>'],
        max_sequence_length=args.max_sequence_length,
        embedding_size=args.embedding_size,
        rnn_type=args.rnn_type,
        hidden_size=args.hidden_size,
        word_dropout=args.word_dropout,
        embedding_dropout=args.embedding_dropout,
        latent_size=args.latent_size,
        num_layers=args.num_layers,
        bidirectional=args.bidirectional
        )

    if not os.path.exists(args.load_checkpoint):
        raise FileNotFoundError(args.load_checkpoint)

    model.load_state_dict(torch.load(args.load_checkpoint))
    print("Model loaded from %s"%(args.load_checkpoint))

    #if torch.cuda.is_available():
    #    model = model.cuda()

    h5f = h5py.File(args.mean_file)
    means = h5f['means'][:]
    h5f.close()

    steps = 7

    indices = []
    for d in range(means.shape[1]):
        indices.append(
            np.linspace(np.min(means[:,d]), np.max(means[:,d]), steps))

    coordinates = np.zeros((steps, steps, steps, steps, 4))
    outputs = open("test_points.txt", 'w')

    for i1 in range(steps):
        for i2 in range(steps):
            for i3 in range(steps):
                for i4 in range(steps):

                    coordinates[i1,i2,i3,i4,:] = [
                        indices[0][i1],
                        indices[1][i2],
                        indices[2][i3],
                        indices[3][i4]]

                    z = np.expand_dims(coordinates[i1,i2,i3,i4], axis=0) # 1 x 4
                    z = to_var(torch.from_numpy(z).float())
                    samples, _ = model.inference(z = z)

                    for sent in idx2word(samples, i2w=i2w,
                            pad_idx=w2i['<pad>']):
                        outputs.write(sent + '\n')
    outputs.close()

    h5f = h5py.File(args.coordinate_file, 'w')
    h5f.create_dataset("coordinates", data=coordinates)
    h5f.close()
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--load_checkpoint', type=str)
    parser.add_argument('-n', '--num_samples', type=int, default=10)

    parser.add_argument('-dd', '--data_dir', type=str, default='data')
    parser.add_argument('-ms', '--max_sequence_length', type=int, default=50)
    parser.add_argument('-eb', '--embedding_size', type=int, default=300)
    parser.add_argument('-rnn', '--rnn_type', type=str, default='gru')
    parser.add_argument('-hs', '--hidden_size', type=int, default=256)
    parser.add_argument('-wd', '--word_dropout', type=float, default=0)
    parser.add_argument('-ed', '--embedding_dropout', type=float, default=0.5)
    parser.add_argument('-ls', '--latent_size', type=int, default=16)
    parser.add_argument('-nl', '--num_layers', type=int, default=1)
    parser.add_argument('-bi', '--bidirectional', action='store_true')

    parser.add_argument('-cf', '--coordinate_file', type=str, action='store')
    parser.add_argument('-mf', '--mean_file', type=str, action='store')

    args = parser.parse_args()

    args.rnn_type = args.rnn_type.lower()

    assert args.rnn_type in ['rnn', 'lstm', 'gru']
    assert 0 <= args.word_dropout <= 1

    main(args)

