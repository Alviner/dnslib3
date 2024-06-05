
__doc__ = """ Some basic bit manipulation utilities """

# Global tuple for ASCII characters, where i < 32 or i > 127 are replaced by '.'
ASCII_CHARS = tuple((i < 32 or i > 127) and 46 or i for i in range(256))


def hexdump(src, length=16, prefix=""):
    """
    Print hexdump of string

    >>> print(hexdump(b"abcd" * 4))
    0000  61 62 63 64 61 62 63 64  61 62 63 64 61 62 63 64  abcdabcd abcdabcd

    >>> print(hexdump(bytearray(range(48))))
    0000  00 01 02 03 04 05 06 07  08 09 0a 0b 0c 0d 0e 0f  ........ ........
    0010  10 11 12 13 14 15 16 17  18 19 1a 1b 1c 1d 1e 1f  ........ ........
    0020  20 21 22 23 24 25 26 27  28 29 2a 2b 2c 2d 2e 2f   !"#$%&' ()*+,-./

    """

    result = []
    src = bytearray(src)
    hex_template = " ".join(["{:02X}"] * 8) + "  " + " ".join(["{:02X}"] * 8)
    ascii_template = "".join(["{}"] * (length // 2)) + " " + "".join(["{}"] * (length // 2))

    for i in range(0, len(src), length):
        chunk = src[i:i + length]
        hex_chunk = [f"{b:02X}" for b in chunk]
        ascii_chunk = [chr(ASCII_CHARS[b]) for b in chunk]

        # Fill the rest if chunk size is less than length
        if len(chunk) < length:
            hex_chunk += ['  '] * (length - len(chunk))
            ascii_chunk += [' '] * (length - len(chunk))

        result.append(
            f"{prefix}{i:04X}  "
            f"{hex_template.format(*[int(h, 16) for h in hex_chunk]).lower()}  "
            f"{ascii_template.format(*ascii_chunk)}"
        )

    return "\n".join(result)


def get_bits(data, offset, bits=1):
    """
    Get specified bits from integer

    >>> bin(get_bits(0b0011100,2))
    '0b1'
    >>> bin(get_bits(0b0011100,0,4))
    '0b1100'

    """
    return (data >> offset) & ((1 << bits) - 1)


def set_bits(data, value, offset, bits=1):
    """
    Set specified bits in integer

    >>> bin(set_bits(0,0b1010,0,4))
    '0b1010'
    >>> bin(set_bits(0,0b1010,3,4))
    '0b1010000'
    """
    mask = ((1 << bits) - 1) << offset
    clear = 0xFFFF ^ mask
    data = (data & clear) | ((value << offset) & mask)
    return data


def binary(n, count=16, reverse=False):
    """
    Display n in binary (only difference from built-in `bin` is
    that this function returns a fixed width string and can
    optionally be reversed

    >>> binary(6789)
    '0001101010000101'
    >>> binary(6789, 8)
    '10000101'
    >>> binary(6789, reverse=True)
    '1010000101011000'

    """
    bits = [str((n >> y) & 1) for y in range(count - 1, -1, -1)]
    if reverse:
        bits.reverse()
    return "".join(bits)
