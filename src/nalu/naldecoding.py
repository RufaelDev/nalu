import math
from bitstring import BitArray
import pdb


def read_u(BitStream, BitStreamPointer, n):
    # pdb.set_trace()
    tempbits = BitArray()
    tempbits = BitStream[BitStreamPointer:(BitStreamPointer + n)]  # pecular to BitArray
    BitStreamPointer += n
    value = tempbits.uint
    return value, BitStreamPointer

def find_num_leading_zeros(in_byte):
    leadingZeroBits = -1
    b = 0
    i = 0
    mask = 0x80
    while ((b == 0) and (i < 8)):
        b = in_byte & (mask >> i)
        leadingZeroBits += 1
        i += 1

    if ((b==0) and (i ==8)):
        leadingZeroBits +=1

    return leadingZeroBits

def decode_ue(bitstream, bitstream_pointer):
    #pointer points to the current position and will be moved to read the next bit
    BitStreamPointer = bitstream_pointer
    BitValue = bitstream[BitStreamPointer]
    BitStreamPointer += 1
    NumLeadZeros = 0
    RequiredBits = BitArray('0x0')
    while BitValue == 0:
        NumLeadZeros += 1
        BitValue = bitstream[BitStreamPointer]
        BitStreamPointer += 1
    if NumLeadZeros > 0:
        #RequiredBits = bitstream[(BitStreamPointer-1):(BitStreamPointer + NumLeadZeros -1)]
        RequiredBits = bitstream[(BitStreamPointer):(BitStreamPointer + NumLeadZeros)]
        #BitStreamPointer += (NumLeadZeros -1)  # pointing to the next bit
        BitStreamPointer += NumLeadZeros   # pointing to the next bit
        #pdb.set_trace()
        CodeNum = (2 ** NumLeadZeros) - 1 + RequiredBits.uint
    else:
        CodeNum = 0
    #pdb.set_trace()
    return CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits

def get_se(CodeNum):
    se_value = (-1**(CodeNum+1)) * math.ceil(CodeNum/2)
    #pdb.set_trace()
    return se_value

def byte_aligned(BitStreamPointer):
    if BitStreamPointer%8:
        return False
    else:
        return True
