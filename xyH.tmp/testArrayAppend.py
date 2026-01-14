#   ###############################################################################
#   a = [2, 5, 8]
#   b = [7, 4, 1]
#
#   a = a + b # Create a new list a+b and assign back to a.
#   print( a )
#   # [1, 2, 3, 10, 20]
#
#
#   # Equivalently:
#   a = [2, 5, 8]
#   b = [7, 4, 1]
#
#   a += b
#   print( a )
#   # [1, 2, 3, 10, 20]
#
#   e = sorted(list(a))
#
#
#   print( e )
#
#   result = []
#   result.append(a)
#   result.append(b)
#   print( result )
#   # [[1, 2, 3], [10, 20]]
#
#
#   A = ["2", "5", "8"]
#   B = ["7", "4", "1"]
#   C = ["10", "20"]
#
#   D = A + B + C
#   print(D)
#
#   E = sorted(list(D))
#
#   print( E )


###############################################################################
import re
import copy

###############################################################################
def retrive_marks(aLine, WELLKNOWN_PROTOCALs):
    PROTOCALs = copy.deepcopy(WELLKNOWN_PROTOCALs)
    # Preventing the confusion of inclusion
    pairs = [ ( "vmess://", "vmeEE://" ), ( "vless://", "vleEE://" ) ]
    for a, b in pairs:
        aLine = aLine.replace( a, b )
        PROTOCALs[ PROTOCALs.index( a ) ] = b

    all_marks=[]
    for item in PROTOCALs:
        idxs = re.finditer(item, aLine)
        if idxs:
            for idx in idxs:
                touple=(idx.start(),idx.end())
                all_marks.append(touple)

    if not all_marks:
        return None

    sorted_all_marks = sorted( all_marks, key=lambda index : index[0] )
    return sorted_all_marks

###############################################################################
def split_nodes(aLine, WELLKNOWN_PROTOCALs):
    all_marks = retrive_marks(aLine, WELLKNOWN_PROTOCALs)

    nodes=[]
    # https://www.geeksforgeeks.org/python/python-pair-iteration-in-list/
    idx_end = 0
    for x, y in zip(all_marks, all_marks[1:]):
        idx_begin = x[0]
        idx_end = y[0]
        nodes.append( aLine[idx_begin:idx_end] )
    nodes.append( aLine[idx_end:] )
    return nodes

###############################################################################
WELLKNOWN_PROTOCALs = [
    'vmess://'    ,
    'vless://'    ,
    'ss://'       ,
    'ssr://'      ,
    'trojan://'   ,
    'tuic://'     ,
    'hysteria://' ,
    'hy2://'      ,
    'socks5://'   ,
    'warp://'     ,
    'wireguard://',
    'snell://'    ,
    'tuic://'     ,
    'ssh://'      ,
    'mieru://'    ,
    'sudoku://'
]

s="vmess://aaaaaaaaaaaaaaaaaaaaaaaaaaaAss://bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbBvmess://cccccccccccccccccccccccccccccccccccccccccCvless://ddddddddddddddddddddddddddddddddddddD"
#s="vmess://aaaaaaaaaaaaaaaaaaaaaaaaaaaA"
#s="ss://aaaaaaaaaaaaaaaaaaaaaaaaaaaA"
Nodes = split_nodes(s,WELLKNOWN_PROTOCALs)
for a in Nodes:
    print(a)

################################## END ########################################
