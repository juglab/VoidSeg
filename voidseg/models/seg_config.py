import argparse

import keras.backend as K
import numpy as np
from csbdeep.utils import _raise, axes_check_and_normalize, axes_dict, backend_channels_last
from six import string_types


# This class is a adapted version of csbdeep.models.config.py.
class SegConfig(argparse.Namespace):
    """
    Default configuration for a trainable segmentation (Seg) model.
    This class is meant to be used with :class:`Seg`.

    Parameters
    ----------
    X      : array(float)
             The training data 'X', with dimensions 'SZYXC' or 'SYXC'
    kwargs : dict
             Overwrite (or add) configuration attributes (see below).

    Example
    -------
    >>> seg_config = SegConfig(X, unet_n_depth=3)

    Attributes
    ----------
    unet_n_depth : int
        Parameter `n_depth` of :func:`csbdeep.internals.nets.common_unet`. Default: ``4``
    unet_kern_size : int
        Parameter `kern_size` of :func:`csbdeep.internals.nets.common_unet`. Default: ``3 ``
    unet_n_first : int
        Parameter `n_first` of :func:`csbdeep.internals.nets.common_unet`. Default: ``32``
    batch_norm : bool
        Activate batch norm. Default: ``True```
    unet_last_activation : str
        Parameter `last_activation` of :func:`csbdeep.internals.nets.common_unet`. Default: ``linear``
    relative_weight : list(floats)
        Relative weights for background, foreground and border class for 3-class U-Net training. Default: ``[1.0,1.0,5.0]``
    train_epochs : int
        Number of training epochs. Default: ``200``
    train_steps_per_epoch : int
        Number of parameter update steps per epoch. Default: ``400``
    train_learning_rate : float
        Learning rate for training. Default: ``0.0004``
    train_batch_size : int
        Batch size for training. Default: ``128``
    train_tensorboard : bool
        Enable TensorBoard for monitoring training progress. Default: ``False``
    train_checkpoint : str
        Name of checkpoint file for model weights (only best are saved); set to ``None`` to disable. Default: ``weights_best.h5``
    train_reduce_lr : dict
        Parameter :class:`dict` of ReduceLROnPlateau_ callback; set to ``None`` to disable. Default: ``{'factor': 0.5, 'patience': 10}``

        .. _ReduceLROnPlateau: https://keras.io/callbacks/#reducelronplateau
    """

    def __init__(self, X, **kwargs):
        """See class docstring"""
        assert X.size != 0
        assert len(X.shape) == 4 or len(X.shape) == 5, "Only 'SZYXC' or 'SYXC' as dimensions is supported."

        n_dim = len(X.shape) - 2

        if n_dim == 2:
            axes = 'SYXC'
        elif n_dim == 3:
            axes = 'SZYXC'

        # parse and check axes
        axes = axes_check_and_normalize(axes)
        ax = axes_dict(axes)
        ax = {a: (ax[a] is not None) for a in ax}

        (ax['X'] and ax['Y']) or _raise(ValueError('lateral axes X and Y must be present.'))
        not (ax['Z'] and ax['T']) or _raise(ValueError('using Z and T axes together not supported.'))

        axes.startswith('S') or (not ax['S']) or _raise(ValueError('sample axis S must be first.'))
        axes = axes.replace('S', '')  # remove sample axis if it exists

        if backend_channels_last():
            if ax['C']:
                axes[-1] == 'C' or _raise(ValueError('channel axis must be last for backend (%s).' % K.backend()))
            else:
                axes += 'C'
        else:
            if ax['C']:
                axes[0] == 'C' or _raise(ValueError('channel axis must be first for backend (%s).' % K.backend()))
            else:
                axes = 'C' + axes

        assert X.shape[-1] == 1
        n_channel_in = 1
        n_channel_out = 3

        # directly set by parameters
        self.n_dim = n_dim
        self.axes = axes
        # fixed parameters
        self.n_channel_in = n_channel_in
        self.n_channel_out = n_channel_out
        self.train_loss = 'seg'

        # default config (can be overwritten by kwargs below)

        self.unet_n_depth = 4
        self.relative_weights = [1.0, 1.0, 5.0]
        self.unet_kern_size = 3
        self.unet_n_first = 32
        self.unet_last_activation = 'linear'
        self.probabilistic = False
        self.unet_residual = False
        if backend_channels_last():
            self.unet_input_shape = self.n_dim * (None,) + (self.n_channel_in,)
        else:
            self.unet_input_shape = (self.n_channel_in,) + self.n_dim * (None,)

        self.train_epochs = 200
        self.train_steps_per_epoch = 400
        self.train_learning_rate = 0.0004
        self.train_batch_size = 128
        self.train_tensorboard = False
        self.train_checkpoint = 'weights_best.h5'
        self.train_checkpoint_last  = 'weights_last.h5'
        self.train_checkpoint_epoch = 'weights_now.h5'
        self.train_reduce_lr = {'factor': 0.5, 'patience': 10}
        self.batch_norm = True

        # disallow setting 'n_dim' manually
        try:
            del kwargs['n_dim']
            # warnings.warn("ignoring parameter 'n_dim'")
        except:
            pass
        # disallow setting 'n_channel_in' manually
        try:
            del kwargs['n_channel_in']
            # warnings.warn("ignoring parameter 'n_dim'")
        except:
            pass
        # disallow setting 'n_channel_out' manually
        try:
            del kwargs['n_channel_out']
            # warnings.warn("ignoring parameter 'n_dim'")
        except:
            pass
        # disallow setting 'train_loss' manually
        try:
            del kwargs['train_loss']
            # warnings.warn("ignoring parameter 'n_dim'")
        except:
            pass
        # disallow setting 'probabilistic' manually
        try:
            del kwargs['probabilistic']
        except:
            pass
        # disallow setting 'unet_residual' manually
        try:
            del kwargs['unet_residual']
        except:
            pass

        for k in kwargs:
            setattr(self, k, kwargs[k])

    def is_valid(self, return_invalid=False):
        """Check if configuration is valid.

        Returns
        -------
        bool
            Flag that indicates whether the current configuration values are valid.
        """

        def _is_int(v, low=None, high=None):
            return (
                    isinstance(v, int) and
                    (True if low is None else low <= v) and
                    (True if high is None else v <= high)
            )

        ok = {}
        ok['n_dim'] = self.n_dim in (2, 3)
        try:
            axes_check_and_normalize(self.axes, self.n_dim + 1, disallowed='S')
            ok['axes'] = True
        except:
            ok['axes'] = False
        ok['n_channel_in'] = _is_int(self.n_channel_in, 1, 1)
        ok['n_channel_out'] = _is_int(self.n_channel_out, 3, 3)
        ok['train_loss'] = (
            (self.train_loss in ('seg'))
        )
        ok['unet_n_depth'] = _is_int(self.unet_n_depth, 1)
        ok['relative_weights'] = isinstance(self.relative_weights, list) and len(self.relative_weights) == 3 and all(
            x > 0 for x in self.relative_weights)
        ok['unet_kern_size'] = _is_int(self.unet_kern_size, 1)
        ok['unet_n_first'] = _is_int(self.unet_n_first, 1)
        ok['unet_last_activation'] = self.unet_last_activation in ('linear', 'relu')
        ok['probabilistic'] = isinstance(self.probabilistic, bool) and not self.probabilistic
        ok['unet_residual'] = isinstance(self.unet_residual, bool) and not self.unet_residual
        ok['unet_input_shape'] = (
                isinstance(self.unet_input_shape, (list, tuple)) and
                len(self.unet_input_shape) == self.n_dim + 1 and
                self.unet_input_shape[-1] == self.n_channel_in and
                all((d is None or (_is_int(d) and d % (2 ** self.unet_n_depth) == 0) for d in
                     self.unet_input_shape[:-1]))
        )
        ok['train_epochs'] = _is_int(self.train_epochs, 1)
        ok['train_steps_per_epoch'] = _is_int(self.train_steps_per_epoch, 1)
        ok['train_learning_rate'] = np.isscalar(self.train_learning_rate) and self.train_learning_rate > 0
        ok['train_batch_size'] = _is_int(self.train_batch_size, 1)
        ok['train_tensorboard'] = isinstance(self.train_tensorboard, bool)
        ok['train_checkpoint'] = self.train_checkpoint is None or isinstance(self.train_checkpoint, string_types)
        ok['train_reduce_lr'] = self.train_reduce_lr is None or isinstance(self.train_reduce_lr, dict)
        ok['batch_norm'] = isinstance(self.batch_norm, bool)

        if return_invalid:
            return all(ok.values()), tuple(k for (k, v) in ok.items() if not v)
        else:
            return all(ok.values())

    def update_parameters(self, allow_new=True, **kwargs):
        if not allow_new:
            attr_new = []
            for k in kwargs:
                try:
                    getattr(self, k)
                except AttributeError:
                    attr_new.append(k)
            if len(attr_new) > 0:
                raise AttributeError("Not allowed to add new parameters (%s)" % ', '.join(attr_new))
        for k in kwargs:
            setattr(self, k, kwargs[k])
