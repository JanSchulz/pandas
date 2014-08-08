## datetimelike delegation ##

import numpy as np
from pandas.core.base import PandasObject, DatetimeIndexOpsMixin
from pandas.core import common as com
from pandas import Series, DatetimeIndex, PeriodIndex
from pandas import lib, tslib

def is_datetimelike(data):
    """ return a boolean if we can be successfully converted to a datetimelike """
    try:
        maybe_to_datetimelike(data)
        return True
    except (Exception):
        pass
    return False

def maybe_to_datetimelike(data, copy=False):
    """
    Parameters
    ----------
    data : Series
    copy : boolean, default False
           copy the input data

    try to convert to a DatetimeIndex / PeriodIndex, and return it in a DelegatedClass

    raise a TypeError if this is not possible
    """

    if not isinstance(data, Series):
        raise TypeError("cannot convert an object of type {0} to a datetimelike index".format(type(data)))

    index = data.index
    if issubclass(data.dtype.type, np.datetime64):
        return DatetimeProperties(DatetimeIndex(data, copy=copy), index)
    else:

        if isinstance(data, PeriodIndex):
            return PeriodProperties(PeriodIndex(data, copy=copy), index)

        data = com._values_from_object(data)
        inferred = lib.infer_dtype(data)
        if inferred == 'period':
            return PeriodProperties(PeriodIndex(data), index)

    raise TypeError("cannot convert an object of type {0} to a datetimelike index".format(type(data)))

class Properties(PandasObject):
    """
    This is a delegator class that passes thru limit property access
    """

    def __init__(self, values, index):
        self.values = values
        self.index = index

    def _delegate_access(self, name):
        result = getattr(self.values,name)

        # maybe need to upcast (ints)
        if isinstance(result, np.ndarray):
            if com.is_integer_dtype(result):
                result = result.astype('int64')
        return Series(result, index=self.index)

class DatetimeProperties(Properties):
    """
    Manages a DatetimeIndex Delegate
    """
    pass
DatetimeProperties._add_delegate_accessors(delegate=DatetimeIndex,
                                           accessors=DatetimeIndex._datetimelike_ops,
                                           typ='property')

class PeriodProperties(Properties):
    """
    Manages a PeriodIndex Delegate
    """
PeriodProperties._add_delegate_accessors(delegate=PeriodIndex,
                                         accessors=PeriodIndex._datetimelike_ops,
                                         typ='property')
