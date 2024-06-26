import sys


__doc__ = """
    Wrapper around property builtin to restrict attribute to defined
    integer value range (throws ValueError).

    Intended to ensure that values packed with struct are in the
    correct range

    >>> class T(object):
    ...     a = range_property('a',-100,100)
    ...     b = B('b')
    ...     c = H('c')
    ...     d = I('d')
    ...     e = instance_property('e',(int,bool))
    >>> t = T()
    >>> for i in [0,100,-100]:
    ...     t.a = i
    ...     assert t.a == i
    >>> t.a = 101
    Traceback (most recent call last):
    ...
    ValueError: Attribute 'a' must be between -100-100 [101]
    >>> t.a = -101
    Traceback (most recent call last):
    ...
    ValueError: Attribute 'a' must be between -100-100 [-101]
    >>> t.a = 'blah'
    Traceback (most recent call last):
    ...
    ValueError: Attribute 'a' must be between -100-100 [blah]
    >>> t.e = 999
    >>> t.e = False
    >>> t.e = None
    Traceback (most recent call last):
    ...
    ValueError: Attribute 'e' must be instance of ...

    >>> check_range("test",123,0,255)
    >>> check_range("test",999,0,255)
    Traceback (most recent call last):
    ...
    ValueError: Attribute 'test' must be between 0-255 [999]

    >>> check_instance("test",123,int)
    >>> check_instance("test","xxx",int)
    Traceback (most recent call last):
    ...
    ValueError: Attribute 'test' must be instance of ...

"""


BYTE_TYPES = (bytes, bytearray)


def check_instance(name, val, types):
    if not isinstance(val, types):
        raise ValueError(
            "Attribute '%s' must be instance of %s [%s]" % (name, types, type(val)),
        )


def check_bytes(name, val):
    return check_instance(name, val, BYTE_TYPES)


def instance_property(attr, types):
    def getter(obj):
        return getattr(obj, "_%s" % attr)

    def setter(obj, val):
        if isinstance(val, types):
            setattr(obj, "_%s" % attr, val)
        else:
            raise ValueError(
                "Attribute '%s' must be instance of %s [%s]" % (attr, types, type(val)),
            )

    return property(getter, setter)


def bytes_property(attr):
    return instance_property(attr, BYTE_TYPES)


def check_range(name, val, min, max):
    if not (isinstance(val, int) and min <= val <= max):
        raise ValueError(
            "Attribute '%s' must be between %d-%d [%s]" % (name, min, max, val),
        )


def range_property(attr, min, max):
    def getter(obj):
        return getattr(obj, "_%s" % attr)

    def setter(obj, val):
        if isinstance(val, int) and min <= val <= max:
            setattr(obj, "_%s" % attr, val)
        else:
            raise ValueError(
                "Attribute '%s' must be between %d-%d [%s]" % (attr, min, max, val),
            )

    return property(getter, setter)


def B(attr):
    """Unsigned Byte"""
    return range_property(attr, 0, 255)


def H(attr):
    """Unsigned Short"""
    return range_property(attr, 0, 65535)


def I(attr):
    """Unsigned Long"""
    return range_property(attr, 0, 4294967295)


def ntuple_range(attr, n, min, max):
    f = lambda x: isinstance(x, int) and min <= x <= max

    def getter(obj):
        return getattr(obj, "_%s" % attr)

    def setter(obj, val):
        if len(val) != n:
            raise ValueError(
                "Attribute '%s' must be tuple with %d elements [%s]" % (attr, n, val),
            )
        if all(map(f, val)):
            setattr(obj, "_%s" % attr, val)
        else:
            raise ValueError(
                "Attribute '%s' elements must be between %d-%d [%s]"
                % (attr, min, max, val),
            )

    return property(getter, setter)


def ipv4(attr):
    return ntuple_range(attr, 4, 0, 255)


def ipv6(attr):
    return ntuple_range(attr, 16, 0, 255)
