import math
from math import exp
import numpy as np
import matplotlib.pyplot as plt

def velocityProfile(currentP,idealV):
    return -idealV/2*((np.tanh(5*(currentP-0.6)))+1)+idealV

pList = [i/100 for i in range(101)]
v = []
for i in range(101):
    v.append(velocityProfile(i/100,60))

plt.plot(pList ,v)
plt.grid(True)
plt.show()