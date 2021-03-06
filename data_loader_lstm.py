import torch
import torch.utils.data as data
import os
import sys
import pickle
import random
import pdb
import numpy as np

class UTKinect(data.Dataset):
    """Load the preprocessed UTKInect Dataset."""
    def __init__(self, root, seq_len, lbl2id, is_val = False):
        self.root = root
        self.seq_len = seq_len
        self.is_val = is_val
        self.lbl2id, self.data = self.__loaddata(self.root, lbl2id)
    
    def __loaddata(self, root, lbl2id):
        dict_lbl2id = {}
        if lbl2id is not None:
            dict_lbl2id = lbl2id
        data = []
        for r, subdirs, fns in os.walk(root):
            for fn in fns:
                ffn = os.path.join(r, fn)
                lbl = fn.split('_')[0]
                if lbl not in dict_lbl2id:
                    dict_lbl2id[lbl] = len(dict_lbl2id)
                if ffn.endswith('npy'):
                    idata = np.load(ffn)
                    idata = np.reshape(idata, (idata.shape[0], idata.shape[1] * idata.shape[2]))
                else:
                    idata = np.loadtxt(ffn)
                    idata = np.stack(idata,0)
                data.append((dict_lbl2id[lbl], idata))
        return dict_lbl2id, data

    def __getitem__(self, index):
        idata = self.data[index]
        lbl = torch.Tensor([idata[0]]).long()
        data = idata[1]
        length = torch.LongTensor(1)

        if self.is_val:
            length[0] = data.size(0)
            return lbl, torch.from_numpy(data), length
        else:
            length[0] = self.seq_len

        if data.shape[0] < self.seq_len:
            # No need to sample
            ndata = np.zeros((self.seq_len, data.shape[1]))
            ndata[0:data.shape[0]] = data
            data = torch.from_numpy(ndata)
        elif data.shape[0] < 2 * self.seq_len:
            # less than 2 in each frame, just randomly select one.
            idx = range(data.shape[0])
            random.shuffle(idx)
            idx = idx[0:self.seq_len]
            sorted(idx)
            ndata = data[idx, :]
            data = torch.from_numpy(ndata)
        else:
            start_idx = list(range(0, data.shape[0], data.shape[0] // self.seq_len))
            if len(start_idx) > self.seq_len:
                start_idx = start_idx[0:self.seq_len] # the last one has more data.
            start_idx.append(data.shape[0])
            idx = []
            for i in range(self.seq_len):
                idx.append(random.randrange(start_idx[i], start_idx[i+1]))
            ndata = data[idx,:]
            data = torch.from_numpy(ndata)
        return lbl, data, length

    def __len__(self):
        return len(self.data)

class NTUDataset(data.Dataset):
    """Load the preprocessed UTKInect Dataset."""
    def __init__(self, root, seq_len, is_val = False):
        self.root = root
        self.seq_len = seq_len
        self.list_fns = self.__loaddata(self.root)
        self.is_val = is_val
    
    def __loaddata(self, root):
        list_fns = []
        for root, subdirs, fns in os.walk(root):
            for fn in fns:
                list_fns.append(os.path.join(root, fn))
        return list_fns

    def __getitem__(self, index):
        fn = self.list_fns[index]
        lbl = os.path.splitext(os.path.basename(fn))[0]
        lbl = int(lbl[lbl.index('A')+1:])  - 1
        data = np.load(fn)
        data = np.reshape(data, (data.shape[0], data.shape[1] * data.shape[2]))
        lbl = torch.Tensor([lbl]).long()
        length = torch.LongTensor(1)

        if self.is_val:
            length[0] = data.size(0)
            return lbl, torch.from_numpy(data), length
        else:
            length[0] = self.seq_len

        if data.shape[0] < self.seq_len:
            # No need to sample
            ndata = np.zeros((self.seq_len, data.shape[1]))
            ndata[0:data.shape[0],:] = data
            data = torch.from_numpy(ndata)
        elif data.shape[0] < 2 * self.seq_len:
            # less than 2 in each frame, just randomly select one.
            idx = range(data.shape[0])
            random.shuffle(idx)
            idx = idx[0:self.seq_len]
            sorted(idx)
            ndata = data[idx, :]
            data = torch.from_numpy(ndata)
        else:
            start_idx = list(range(0, data.shape[0], data.shape[0] // self.seq_len))
            if len(start_idx) > self.seq_len:
                start_idx = start_idx[0:self.seq_len] # the last one has more data.
            start_idx.append(data.shape[0])
            idx = []
            for i in range(self.seq_len):
                idx.append(random.randrange(start_idx[i], start_idx[i+1]))
            ndata = data[idx,:]
            data = torch.from_numpy(ndata)
        return lbl, data, length

    def __len__(self):
        return len(self.list_fns)

def collate_fn(data):
    lbl, dta, length= zip(*data)
    lbl = torch.stack(lbl, 0)
    dta = torch.stack(dta, 0).float()
    length = torch.stack(length, 0)
    return lbl, dta, length


def get_loader(root, seq_len, batch_size, shuffle, num_workers, ds = 'UTKinect', is_val = False, lbl2id = None):
    """Returns torch.utils.data.DataLoader for custom coco dataset."""
    if ds == 'UTKinect':
        ds_class = UTKinect(root,seq_len, lbl2id, is_val)
    elif ds == 'NTU':
        ds_class = NTUDataset(root,seq_len, is_val)

    data_loader = torch.utils.data.DataLoader(dataset=ds_class, 
                                              batch_size=batch_size,
                                              shuffle=shuffle,
                                              num_workers=num_workers,
                                              collate_fn=collate_fn)
    return data_loader, ds_class
