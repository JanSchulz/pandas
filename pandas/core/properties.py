"""
Properties and method delegator
"""

from pandas.core.base import PandasObject
from pandas import Series
import pandas.core.common as com
import numpy as np

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

    @classmethod
    def _add_delegate_accessors(cls, delegate, accessors, typ):
        """
        add accessors to cls from the delegate class

        Parameters
        ----------
        cls : the class to add the methods/properties to
        delegate : the class to get methods/properties & doc-strings
        acccessors : string list of accessors to add
        typ : 'property' or 'method'

        """

        def _create_delegator(name):

            def f(self):
                return self._delegate_access(name)

            f.__name__ = name
            f.__doc__ = getattr(delegate,name).__doc__

            return f

        for name in accessors:

            f = _create_delegator(name)
            if typ == 'property':
                f = property(f)
            setattr(cls,name,f)
