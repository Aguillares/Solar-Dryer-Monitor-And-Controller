import pandas as pd
import numpy as np
arrays = [["bar", "bar", "baz", "baz", "foo", "foo", "qux", "qux","foo"],
          ["doo", "doo", "bee", "bee", "bop", "bop", "bop", "bop","bar"],
          ["one", "two", "one", "two", "one", "two", "one", "two","two"],
          ]

index = pd.MultiIndex.from_arrays(arrays, names=["first", "second", "third"])
np.random.seed(0)
s = pd.Series(np.random.randn(9), index=index)
s['new'] = [1,1,1]
print(s.T)