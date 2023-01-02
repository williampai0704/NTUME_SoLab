import numpy as np
import random 

# mu, sigma = 0, 0.1 # mean and standard deviation
# s = np.random.normal(mu, sigma, 1000)
# print(abs(mu - np.mean(s)))

for i in range(50):
    k = random.gauss(5,1)
    print(k)
