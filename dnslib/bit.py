
__doc__ = """ Some basic bit manipulation utilities """


def get_bits(data: int, offset: int, bits: int = 1) -> int:
    """
    Get specified bits from integer

    >>> bin(get_bits(0b0011100,2))
    '0b1'
    >>> bin(get_bits(0b0011100,0,4))
    '0b1100'

    """
    return (data >> offset) & ((1 << bits) - 1)


def set_bits(data: int, value: int, offset: int, bits: int = 1) -> int:
    """
    Set specified bits in integer

    >>> bin(set_bits(0,0b1010,0,4))
    '0b1010'
    >>> bin(set_bits(0,0b1010,3,4))
    '0b1010000'
    """
    mask = ((1 << bits) - 1) << offset
    data &= ~mask
    data |= (value << offset) & mask
    return data
