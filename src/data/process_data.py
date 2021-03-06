from tqdm import tqdm
from typing import *
from mne.preprocessing import ICA
import numpy as np
import numpy.typing as npt
import pymatreader
import mne
import os
import warnings

warnings.filterwarnings('ignore')

#TODO: add specgram representation of signal
class EEGpreprocessing:
    """Processes raw signal.

    Takes eeglab files, performs filtering, Independent Component
    Analysis(ICA), grabs events and then saves binary .npy files.

    NOTE: If you work with cloned repo there is no need to
    pass directory to data.
    """

    def __init__(self, path=r'../../data/raw'):
        self.files = []
        self.file_name = []
        for file in tqdm(os.listdir(path)):
            if file.endswith('.set'):
                try:
                    self.files.append(os.path.join(path, file))
                    self.file_name.append(file[:-4])

                except FileNotFoundError as e:
                    print(file)

    def _filtering(self, signal: npt.ArrayLike) -> np.ndarray:
        """
        Performs filtering by applying butterworth and
        notch filer.

        Args:
            signal ArrayLike: Raw EEG signal.

        Returns:
            np.ndarray: Filtered signal.
        """
        
        sf = signal.copy().filter(
            l_freq=0.1,
            h_freq=45.0,
            picks=None,
            filter_length='auto',
            l_trans_bandwidth='auto',
            h_trans_bandwidth='auto',
            n_jobs=1, method='iir',
            iir_params={'order':2, 'ftype':'butter'},
            skip_by_annotation=('edge', 'bad_acq_skip'),
            pad='reflect_limited',
            verbose=False
            )

        sfilt = sf.copy().notch_filter(
            freqs = 50.0,
            picks=None, 
            filter_length='auto', 
            notch_widths=None, 
            trans_bandwidth=1.0, 
            n_jobs=1, 
            method='iir', 
            iir_params=None, 
            mt_bandwidth=None, 
            p_value=0.05, 
            pad='reflect_limited', 
            verbose=False
            )   

        return sfilt
        
    def _ica(self, signal: npt.ArrayLike) -> npt.ArrayLike:
        """Applies fastICA to signal.

        Filter out EOG artefacts from the signal.

        Args:
            signal ArrayLike: Filtered signal.

        Returns:
            ArrayLike: Post ICA signal with deleted Diod and EOG channel.
        """
        signal.drop_channels('Diode')
        ica = ICA(n_components=19, method='fastica')
        ica.fit(signal, decim=None, reject={'eeg':10e-4}, verbose=False)
        ica.exclude = []
        eog_indices, eog_scores  = ica.find_bads_eog(
                                                    signal.copy(),
                                                    ch_name='EOG'
                                                    )
        ica.exclude = eog_indices
        eeg_ica  = ica.apply(signal.copy(), exclude = eog_indices)
        eeg_ica.drop_channels('EOG')

        return eeg_ica
    
    def _setthreshold(self, signal:np.ndarray, threshold: float) -> np.ndarray:
        """Sets threshold and deletes outliers.

        Args:
            signal (np.ndarray): 3 dimentional signal with 0th dim as events. 

        Returns:
            np.ndarray: Returns EEG signal with deleted events. 
        """
        idx = []
        for i in range(len(signal)):
            if np.max(np.abs(signal[i,:,:])) > threshold:
                idx.append(i)
        new_signal = np.delete(signal, idx, axis=0)
                
        return new_signal, idx
    
    def _read_tag_type(fname):
        from mne.utils._bunch import Bunch
        eeg = pymatreader.read_mat(fname, uint16_codec=None)
        eeg = eeg.get('EEG', eeg)
        eeg = Bunch(**eeg)
        tags_type = eeg.event['tag_type']

        return tags_type

    def prepare(self):
        """Gets events from preprocessed signal.
        
        Combines all processing methods and outputs binary files.

        """

        for (file,name) in zip(self.files[:1], self.file_name[:1]):
            raw = mne.io.read_raw_eeglab(file, eog='auto')
            Fs=raw.info['sfreq']
            Fs_int = int(Fs)

            raw.load_data()
            sf = self._filtering(signal=raw)
            s_ica = self._ica(signal=sf)
            n_chan = s_ica.info['nchan']

            eventstarts = mne.events_from_annotations(raw.copy())[0]
            eventstarts = eventstarts[np.where(eventstarts[:,2] == 1)][:,0]
            events = np.zeros((len(eventstarts), n_chan, Fs_int))
            for i, start in enumerate(eventstarts):

                crop_data = s_ica.copy().crop(
                                        tmin=(start/Fs)-0.2,
                                        tmax=(start/Fs)+0.8, 
                                        include_tmax=False
                                        )  
                crop_data_values = crop_data.get_data(units='uV')
                init_mean = crop_data_values[:,:int(0.2 * Fs_int)].mean(axis=1)
                events[i,:,:] = crop_data_values - np.expand_dims(init_mean,axis=1)
            
            clean_signal = self._setthreshold(signal=events, threshold = 75.0)
            np.save(file=f'../../data/binary/{name}.npy', arr=clean_signal)


if __name__ == "__main__":

    data = EEGpreprocessing()
    data.prepare()