import wfdb
import random
import psutil
import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.preprocessing import LabelEncoder


def load_data(prepared_df: pd.DataFrame, path: str, sampling_rate=500) -> np.array:
    if os.path.exists(f"{path}data.npy"):
        result = np.load(f"{path}data.npy")
    else:
        memory = psutil.virtual_memory()
        if memory.available < prepared_df.shape[0] * 5000 * 12:
            return
        result = np.empty((prepared_df.shape[0], 5000, 12))
        if sampling_rate == 500:
            for i, caption in tqdm(enumerate(prepared_df.filename_hr), total=len(prepared_df.filename_hr)):
                result[i] = wfdb.rdrecord(path + caption).p_signal
        else:
            for i, caption in tqdm(enumerate(prepared_df.filename_lr), total=len(prepared_df.filename_lr)):
                result[i] = wfdb.rdrecord(path + caption).p_signal
        np.save(path + "data.npy", result)
    return result


def train_test_split_by_captions(prepared_df: pd.DataFrame, y: pd.DataFrame, test_size=0.2, sampling_rate=500):
    label_encoder = LabelEncoder()
    format_name = 'filename_hr' if sampling_rate == 500 else 'filename_lr'
    train_captions = prepared_df[format_name].sample(n=int(prepared_df.shape[0] * (1 - test_size)), replace=False)
    y_train = []
    for train_caption in tqdm(train_captions):
        name = int(train_caption[-8:-3])
        y_train.append(y.loc[name])
    test_captions = prepared_df.drop(train_captions.index)[format_name]
    y_test = []
    for test_caption in tqdm(test_captions):
        name = int(test_caption[-8:-3])
        y_test.append(y.loc[name])
    return train_captions.tolist(), test_captions.tolist(), label_encoder.fit_transform(
        np.array(y_train)), label_encoder.fit_transform(np.array(y_test))


def train_test_split_dataset(X: np.array, y: np.array, test_size=0.2, sampling_rate=500):
    format_name = 'filename_hr' if sampling_rate == 500 else 'filename_lr'
    test_indeces = random.sample(range(21712), int(21712 * test_size))
    train_indeces = list(set(range(21712)) - set(test_indeces))
    return X[train_indeces], X[test_indeces], y[train_indeces], y[test_indeces]
