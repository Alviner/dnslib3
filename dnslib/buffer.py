import binascii
import struct
from threading import RLock
from typing import Any, Tuple


__doc__ = """ Buffer - simple data buffer """


class Buffer:
    __slots__ = ("data", "offset", "lock")

    """
    A simple data buffer - supports packing/unpacking in struct format

    # Needed for Python 2/3 doctest compatibility
    >>> def p(s):
    ...     if not isinstance(s, str):
    ...         return s.decode()
    ...     return s

    >>> b = Buffer()
    >>> b.pack("!BHI", 1, 2, 3)
    >>> b.offset
    7
    >>> b.append(b"0123456789")
    >>> b.offset
    17
    >>> p(b.hex())
    '0100020000000330313233343536373839'
    >>> b.offset = 0
    >>> b.unpack("!BHI")
    (1, 2, 3)
    >>> bytearray(b.get(5))
    bytearray(b'01234')
    >>> bytearray(b.get(5))
    bytearray(b'56789')
    >>> b.update(7, "2s", b"xx")
    >>> b.offset = 7
    >>> bytearray(b.get(5))
    bytearray(b'xx234')
    """

    def __init__(self, data: bytes = b"") -> None:
        """
        Initialise Buffer from data
        """
        self.data = bytearray(data)
        self.offset = 0
        self.lock = RLock()

    def remaining(self) -> int:
        """
        Return bytes remaining
        """
        return len(self.data) - self.offset

    def get(self, length: int) -> bytes:
        """
        Get len bytes at current offset (& increment offset)
        """
        with self.lock:
            if length > self.remaining():
                raise BufferError(
                    "Not enough bytes [offset=%d,remaining=%d,requested=%d]" % (self.offset, self.remaining(), length),
                )
            start = self.offset
            end = self.offset + length
            self.offset += length
            return bytes(self.data[start:end])

    def hex(self) -> str:
        """
        Return data as hex string
        """
        return binascii.hexlify(self.data).decode()

    def pack(self, fmt: str, *args: Any) -> None:
        """
        Pack data at end of data according to fmt (from struct) & increment
        offset
        """
        with self.lock:
            self.offset += struct.calcsize(fmt)
            self.data += struct.pack(fmt, *args)

    def append(self, s: bytes) -> None:
        """
        Append s to end of data & increment offset
        """
        with self.lock:
            self.offset += len(s)
            self.data += s

    def update(self, ptr: int, fmt: str, *args: Any) -> None:
        """
        Modify data at offset `ptr`
        """
        with self.lock:
            s = struct.pack(fmt, *args)
            self.data[ptr : ptr + len(s)] = s

    def unpack(self, fmt: str) -> Tuple[Any, ...]:
        """
        Unpack data at current offset according to fmt (from struct)
        """
        data = self.get(struct.calcsize(fmt))

        try:
            return struct.unpack(fmt, data)
        except struct.error as e:
            raise BufferError(
                "Error unpacking struct '%s' <%s>" % (fmt, binascii.hexlify(data).decode()),
            )

    def __len__(self) -> int:
        return len(self.data)
