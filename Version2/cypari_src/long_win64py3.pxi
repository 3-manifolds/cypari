ctypedef long long pari_longword
ctypedef unsigned long long pari_ulongword
cdef pari_ulongword pos_max = 0x7fffffff
cdef pari_ulongword neg_max = 0x80000000
cdef pari_longword_to_int(pari_longword x):
    return int(x)