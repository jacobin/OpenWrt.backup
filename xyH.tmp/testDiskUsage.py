# https://www.geeksforgeeks.org/python/python-shutil-disk_usage-method-2

# Python program to explain shutil.disk_usage() method

# importing os module
import os

# importing shutil module
import shutil

# path
path = '/tmp'

# Using shutil.disk_usage() method
memory = shutil.disk_usage(path)

# Print result
print(memory)

(total, used, free)=memory

print(free)

free =memory[2]

print(free)

free = shutil.disk_usage(path)[2]

print(free)