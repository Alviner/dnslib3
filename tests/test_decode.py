import argparse
import binascii
import code
import glob
import os
import os.path
import pathlib
from subprocess import getoutput

import pytest

from dnslib.digparser import DigParser
from dnslib.dns import EDNS0, DNSRecord


TESTS_ROOT = pathlib.Path(__file__).parent
TEST_DATA = TESTS_ROOT / "testdata"
TEST_FILES = (file for file in TEST_DATA.glob("*") if file.is_file())


def fname(val: pathlib.Path):
    return val.name


@pytest.mark.parametrize("fixture", list(TEST_FILES), ids=fname)
def test_decode(fixture: pathlib.Path):
    errors = check_decode(fixture)
    print_errors(errors)
    assert len(errors) == 0


def check_decode(f):
    errors = []

    # Parse the q/a records
    with open(f) as x:
        q, r = DigParser(x)

    # Grab the hex data
    with open(f, "rb") as x:
        for l in x.readlines():
            if l.startswith(b";; QUERY:"):
                qdata = binascii.unhexlify(l.split()[-1])
            elif l.startswith(b";; RESPONSE:"):
                rdata = binascii.unhexlify(l.split()[-1])

    # Parse the hex data
    qparse = DNSRecord.parse(qdata)
    rparse = DNSRecord.parse(rdata)

    # Check records generated from DiG input matches
    # records parsed from packet data
    if q != qparse:
        errors.append(("Question", q.diff(qparse)))
    if r != rparse:
        errors.append(("Reply", r.diff(rparse)))

    # Repack the data
    qpack = qparse.pack()
    rpack = rparse.pack()

    # Check if repacked question data matches original
    # We occasionally get issues where original packet did not
    # compress all labels - in this case we reparse packed
    # record, repack this and compare with the packed data
    if qpack != qdata:
        if len(qpack) < len(qdata):
            # Shorter - possibly compression difference
            if DNSRecord.parse(qpack).pack() != qpack:
                errors.append(("Question Pack", (qdata, qpack)))
        else:
            errors.append(("Question Pack", (qdata, qpack)))
    if rpack != rdata:
        if len(rpack) < len(rdata):
            if DNSRecord.parse(rpack).pack() != rpack:
                errors.append(("Reply Pack", (rdata, rpack)))
        else:
            errors.append(("Reply Pack", (rdata, rpack)))

    return errors


def print_errors(errors):
    for err, err_data in errors:
        if err == "Question":
            print("Question error:")
            for d1, d2 in err_data:
                if d1:
                    print(";; - %s" % d1)
                if d2:
                    print(";; + %s" % d2)
        elif err == "Reply":
            print("Reply error:")
            for d1, d2 in err_data:
                if d1:
                    print(";; - %s" % d1)
                if d2:
                    print(";; + %s" % d2)
        elif err == "Question Pack":
            print("Question pack error")
            print("QDATA:", binascii.hexlify(err_data[0]))
            print(DNSRecord.parse(err_data[0]))
            print("QPACK:", binascii.hexlify(err_data[1]))
            print(DNSRecord.parse(err_data[1]))
        elif err == "Reply Pack":
            print("Response pack error")
            print("RDATA:", binascii.hexlify(err_data[0]))
            print(DNSRecord.parse(err_data[0]))
            print("RPACK:", binascii.hexlify(err_data[1]))
            print(DNSRecord.parse(err_data[1]))
