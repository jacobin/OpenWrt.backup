#https://stackoverflow.com/questions/22496657/how-can-i-access-each-element-of-a-pair-in-a-pair-list
from collections import namedtuple

Pair = namedtuple("Pair", ["first", "second"])

pairs = [Pair("a", 1), Pair("b", 2), Pair("c", 3)]

for pair in pairs:
    print("First = {}, second = {}".format(pair.first, pair.second))