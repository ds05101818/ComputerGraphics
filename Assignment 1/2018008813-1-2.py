import numpy as np

m = np.arange(2,27,1)

print(m)

m = m.reshape(5,5)

print(m)

m[:,0]=0

print(m)

m = m @ m

print(m)

print(np.sqrt(m[0,:]@m[0,:]))

