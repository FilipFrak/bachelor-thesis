import numpy as np
import os


class EEGDataLoader:
    def __init__(self, folderpath = r'../../data/binary'):
        self.folderpath = folderpath
        self.files = []
        for file in os.listdir(folderpath):
                    if file.endswith('.npy'):
                        try:
                            self.files.append(os.path.join(folderpath, file))
                        except FileNotFoundError as e:
                            print(file)
    
    def __getitem__(self, index) -> np.ndarray:
        filepath = self.files[index]
        data = np.load(file=filepath)

        return data

if __name__ == '__main__':
    pass
