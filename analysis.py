import numpy as np
from data_ingestion import mat_data

TIMELINE = mat_data['time']


def _adjust_python_idx(idx):
    return idx - 1


class Signal:

    def __init__(self, values, timeline=TIMELINE, noise=None):
        self.values = values
        self.timeline = timeline
        self.noise = noise


class EEGSignal(Signal):

    def __init__(self, name, trial, block, timeline=TIMELINE, data=mat_data):
        self.name = name
        self.sub_id = np.argwhere(data['subjects'] == name).flatten()[0]
        self.trial = _adjust_python_idx(trial)
        self.block = _adjust_python_idx(block)
        self.values = data['s2'][self.sub_id, :, self.trial, self.block]
        super().__init__(self.values, timeline)


class ERPSignal:

    def __init__(self, name, trials, blocks, timeline=TIMELINE, data=mat_data):
        self.name = name
        self.sub_id = np.argwhere(data['subjects'] == name).flatten()[0]
        self.timeline = timeline
        # init trial-block range
        self.trial, self.block, self.trial_start, self.block_start, \
            self.trial_end, self.block_end, self.avg_over = tuple([None] * 7)
        self.data = self.__auto_set_data(trials, blocks, data)
        self.__signal = None
        self.__noise = None
        # self.desc = f"ERPSignal averaged over {self.avg_over}"

    def __unpack_range(self, pack, axis):
        if axis == "trials":
            if isinstance(pack, int):
                self.trial = _adjust_python_idx(pack)
            else:
                self.trial_start = _adjust_python_idx(pack[0])
                self.trial_end = _adjust_python_idx(pack[1])
        if axis == "blocks":
            if isinstance(pack, int):
                self.block = _adjust_python_idx(pack)
            else:
                self.block_start = _adjust_python_idx(pack[0])
                self.block_end = _adjust_python_idx(pack[1])

    def __auto_set_data(self, trials, blocks, data):
        self.__unpack_range(trials, "trials")
        self.__unpack_range(blocks, "blocks")
        if self.block is not None:
            if self.trial is not None:
                raise TypeError("A stochastic combination of trials and blocks"
                                "was passed. Please use EEGSignal(*args).")
            else:
                self.avg_over = "trial"
                return data['s2'][self.sub_id, :,
                       self.trial_start:self.trial_end+1, self.block]
        else:
            if self.trial is not None:
                self.avg_over = "block"
                return data['s2'][self.sub_id, :,
                       self.trial, self.block_start:self.block_end+1]
            else:
                return data['s2'][self.sub_id, :,
                       self.trial_start:self.trial_end+1,
                       self.block_start:self.block_end+1]

    def fit(self):
        if self.avg_over is None:
            self.__signal = np.nanmean(self.data, axis=(1, 2))
            self.__noise = np.nanstd(self.data, axis=(1, 2))
        else:  # trial or block are both will be on axis=1
            self.__signal = np.nanmean(self.data, axis=1)
            self.__noise = np.std(self.data, axis=1)

        return Signal(self.__signal, self.timeline, self.__noise)

    # def signal(self):
    #     if self.__signal is None:
    #         raise Exception("Use fit method in order to output ERP signal")
    #     else:
    #         return Signal(self.__signal, self.timeline, self.__noise)


class Component:
    def __init__(self, orientation, t1, t2, signal, baseline=0):
        self.orientation = orientation
        self.t1, self.t2 = t1, t2
        boundaries = self.__get_t_idx(signal.timeline, [self.t1, self.t2])
        self.timeline = signal.timeline[boundaries[0]:boundaries[1]]
        self.values = signal.values[boundaries[0]:boundaries[1]]
        self.baseline = baseline

    def __repr__(self):
        return f'Component {self.orientation}{self.t1}-{self.t2} post-onset'

    def __get_t_idx(self, timeline, t):
        vf = np.vectorize(lambda t: np.argmin(np.abs(timeline - t)))
        return vf(t)  # idx for corresponding t (same length)

    def sum(self, **kwargs):
        return np.nansum(self.values - self.baseline, **kwargs)

    def abs_sum(self):
        return np.nansum(np.abs(self.values - self.baseline))

    def rms(self, **kwargs):
        return np.sqrt(np.nanmean(self.values - self.baseline, **kwargs))

    def peak(self, **kwargs):
        if self.orientation == "N":
            return np.nanmin(self.values - self.baseline, **kwargs)
        if self.orientation == "P":
            return np.max(self.values - self.baseline, **kwargs)

    def auc(self, absolute_val=False, **kwargs):
        if absolute_val:
            y = np.abs(self.values - self.baseline)
        else:
            y = self.values - self.baseline
        return np.trapz(y=y, x=self.timeline, **kwargs)


def softmax(x):
    return np.exp(x) / np.nansum(np.exp(x))


# note assumes positive vector (consider N1)?
def zero_one_scaling(x):
    mini = np.nanmin(x)
    maxi = np.nanmax(x)
    return (x - mini) / (maxi - mini)
