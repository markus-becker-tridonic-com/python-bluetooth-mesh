#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2019  SILVAIR sp. z o.o.
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#
import enum
import json
import logging
import re
import sys
from datetime import datetime
from tempfile import NamedTemporaryFile

import construct
import pytest

from bluetooth_mesh.messages import AccessMessage
from bluetooth_mesh.messages.util import Opcode

if sys.version_info >= (3, 7):
    import capnp

    from bluetooth_mesh.messages.capnproto import generate

valid = [
    # config
    bytes.fromhex("02003601CE00FECAEFBE0BB000000000"),
    bytes.fromhex("8002000b00010000012100"),
    bytes.fromhex("8039010203040506070809"),
    # ctl
    bytes.fromhex("826522223333ff323c"),
    # nds
    bytes.fromhex("FD3601011234AAAA82031000"),
    bytes.fromhex("FD3601011234AAAA820310000300"),
    # sensor
    bytes.fromhex("8230"),
    bytes.fromhex("82300400"),
    bytes.fromhex("8231"),
    bytes.fromhex("82310700"),
    bytes.fromhex("510c00000000040b0c"),
    bytes.fromhex("511900"),
    bytes.fromhex("510c00000000020b0c1f00efcdab071b1c"),
    bytes.fromhex("52e20ac800"),
    bytes.fromhex("52220b2003"),
    bytes.fromhex("52440da244ff"),
    ##vendor sensor
    # bytes.fromhex("52099040a244ff0000"),
    bytes.fromhex("52440da244ff220b2003"),
    bytes.fromhex("583000010004000900"),
    bytes.fromhex("583000"),
    bytes.fromhex("5957005700c800"),
    bytes.fromhex("5b5700570001c800"),
    bytes.fromhex("5b5700020001c80039"),
    bytes.fromhex("5957005700c800"),
    bytes.fromhex("5957000200c80039"),
    bytes.fromhex("5905000500200354"),
    bytes.fromhex("5957000200c80000"),
    bytes.fromhex("59590059000003"),
    bytes.fromhex("5942004d0001"),
    bytes.fromhex("594200420050"),
    bytes.fromhex("590a003600b80b00"),
    bytes.fromhex("596d006d000a0000"),
    ##no value
    # bytes.fromhex("596d006d00ffffff"),
    bytes.fromhex("59550055001a2700"),
    bytes.fromhex("594c004c001b1a"),
    bytes.fromhex("596c006c00ff1b1a"),
    ##no value
    # bytes.fromhex("596c006c00ffffff"),
    bytes.fromhex("59680068000500"),
    bytes.fromhex("5967006700050001007040"),
    bytes.fromhex("590e000e006162636465666768"),
    bytes.fromhex("590e000e006162636465660000"),
    bytes.fromhex(
        "5911001100616263646566676861626364656667686162636465666768616263646566676861626364"
    ),
    bytes.fromhex("596a006a00a244ff"),
    bytes.fromhex("592e002e0044ff"),
    bytes.fromhex("593200320044ff0000"),
    bytes.fromhex("5952005200a08601"),
    bytes.fromhex("5916001600e80300d007000f2700"),
    bytes.fromhex("594f004f001f"),
    bytes.fromhex("594f004f00e1"),
    bytes.fromhex("5954005400e620"),
    bytes.fromhex("59450045003102dc6e71"),
    bytes.fromhex("591400140092096400f8f8204e71"),
    bytes.fromhex("5913001300dc6e"),
    bytes.fromhex("5901000100186da2"),
    bytes.fromhex("5960006000a244ff6da2"),
    bytes.fromhex("592a002a00690140000000f0ff54"),
    bytes.fromhex("594900490000000006f0ff"),
    bytes.fromhex("59470047009709640000007d1571"),
    bytes.fromhex("594600460000007d15"),
    bytes.fromhex("5921002100000001007d15"),
    bytes.fromhex("5970007000020000"),
    bytes.fromhex("59060006000020"),
    bytes.fromhex("5940004000020000"),
    bytes.fromhex("591f001f00d007"),
    bytes.fromhex("5941004100e803d007"),
    bytes.fromhex("593e003e00d407"),
    bytes.fromhex("590f000f00ffeeddccbbaa"),
    bytes.fromhex("590700070064"),
    bytes.fromhex("595e005e009227"),
    bytes.fromhex("5951005100b80b"),
    bytes.fromhex("590a000a0004f0"),
    bytes.fromhex("590b000b002a00"),
    bytes.fromhex("590c000c00de4600"),
    bytes.fromhex("5950005000ee00cdab"),
    bytes.fromhex("590800080064"),
    bytes.fromhex("59080008009c"),
    bytes.fromhex("596100610088aa00bbbb"),
    bytes.fromhex("5962006200881a27001a2700"),
    bytes.fromhex("596400640088ffffe620"),
    bytes.fromhex("5965006500880000cdab"),
    bytes.fromhex("59660066008820032003"),
    # light
    bytes.fromhex("824b"),
    bytes.fromhex("824cbbaa22"),
    bytes.fromhex("824c010022"),
    bytes.fromhex("824c000031323c"),
    bytes.fromhex("824d000031323c"),
    bytes.fromhex("824e4400"),
    bytes.fromhex("824e000031c80f"),
    bytes.fromhex("824f"),
    bytes.fromhex("8250bbaa01"),
    bytes.fromhex("8250010022"),
    bytes.fromhex("8250000031321b"),
    bytes.fromhex("8251ff0031323c"),
    bytes.fromhex("82520000ddbb4c"),
    bytes.fromhex("8253"),
    bytes.fromhex("82540000"),
    bytes.fromhex("8255"),
    bytes.fromhex("82560000"),
    bytes.fromhex("8257"),
    bytes.fromhex("82580011118888"),
    # scene
    bytes.fromhex("8241"),
    bytes.fromhex("824201001e"),
    bytes.fromhex("824301001e"),
    bytes.fromhex("824201001ef23c"),
    bytes.fromhex("824301001ef23c"),
    bytes.fromhex("5e000100"),
    bytes.fromhex("5e0001000200f2"),
    bytes.fromhex("8244"),
    bytes.fromhex("824500010001000200") + 14 * bytes.fromhex("0000"),
    bytes.fromhex("82460100"),
    bytes.fromhex("82470100"),
    bytes.fromhex("829e0100"),
    bytes.fromhex("829f0100"),
    # onoff
    bytes.fromhex("8201"),
    bytes.fromhex("82020122"),
    bytes.fromhex("82020122"),
    bytes.fromhex("82020031323c"),
    bytes.fromhex("82020031f23c"),
    bytes.fromhex("820400"),
    bytes.fromhex("820400014a"),
    bytes.fromhex("82040001ff"),
    # level
    bytes.fromhex("8205"),
    bytes.fromhex("8206ff7f22"),
    bytes.fromhex("8206008022"),
    bytes.fromhex("8206010022"),
    bytes.fromhex("8206000031323c"),
    bytes.fromhex("8207000031323c"),
    bytes.fromhex("8208ff7f"),
    bytes.fromhex("82080080"),
    bytes.fromhex("82080000ff004a"),
    bytes.fromhex("820800000100ff"),
    bytes.fromhex("8209ffffff7f22"),
    bytes.fromhex("82090000008022"),
    bytes.fromhex("82090100000022"),
    bytes.fromhex("82090000000031323c"),
    bytes.fromhex("820a0000000031323c"),
    bytes.fromhex("820bff7f22"),
    bytes.fromhex("820b008022"),
    bytes.fromhex("820b010022"),
    bytes.fromhex("820b000031323c"),
    bytes.fromhex("820c000031323c"),
]


@pytest.fixture(scope="session")
def capnproto():
    with NamedTemporaryFile("w", suffix=".capnp") as f:
        generate(0xD988DA1AAFBE9E47, f)
        f.flush()
        return capnp.load(f.name)


class CaseConverter:
    @staticmethod
    def _camelcase(field_name):
        head, *tail = str(field_name).lower().replace(" ", "_").split("_")
        return "".join([head, *(i.title() for i in tail)])

    @staticmethod
    def _snakecase(field_name):
        pattern = re.compile(r"(?<!^)(?=[A-Z])")
        return pattern.sub("_", field_name).lower()

    @classmethod
    def to_camelcase(cls, value):
        if isinstance(value, construct.Container):
            name = getattr(value, "_name", None)
            container = {
                cls._camelcase(k): cls.to_camelcase(v)
                for k, v in value.items()
                if not k.startswith("_")
            }

            return {name: container} if name else container

        if isinstance(value, (set, construct.ListContainer)):
            return [cls.to_camelcase(i) for i in value]

        if isinstance(value, enum.Enum):
            return value.value

        if isinstance(value, bytes):
            return value

        if isinstance(value, datetime):
            return (value - datetime(1970, 1, 1)).days

        return value

    @classmethod
    def to_snakecase(cls, value):
        if isinstance(value, dict):
            container = {
                cls._snakecase(k): cls.to_snakecase(v)
                for k, v in value.items()
                if not k.startswith("_")
            }

            return container

        if isinstance(value, list):
            return [cls.to_snakecase(i) for i in value]

        return value


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires Python3.7")
@pytest.mark.parametrize("encoded", [pytest.param(i, id=i.hex()) for i in valid])
def test_parse_capnproto(encoded, capnproto):
    logging.info("MESH[%i] %s", len(encoded), encoded.hex())

    decoded = AccessMessage.parse(encoded)
    logging.info("CONSTRUCT %r", decoded)

    params = CaseConverter.to_camelcase(decoded)
    logging.info("CAPNP INPUT[%i] %s", len(json.dumps(params)), json.dumps(params))

    message = capnproto.AccessMessage.new_message(**params)
    logging.info("CAPNP %r", message)

    packed = message.to_bytes_packed()
    logging.info("PACKED[%i] %s", len(packed), packed.hex())

    unpacked = capnproto.AccessMessage.from_bytes_packed(packed)
    logging.info("UNPACKED %r", unpacked)

    params = CaseConverter.to_snakecase(unpacked.to_dict())
    logging.info("CONSTRUCT INPUT %s", params)

    assert AccessMessage.build(params) == encoded
