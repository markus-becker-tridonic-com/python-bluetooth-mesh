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
from enum import IntEnum

from construct import Embedded, Int8ul, Int16sl, Int32sl, Select, Struct, Switch, this

from bluetooth_mesh.messages.capnproto import CapNProtoStruct
from bluetooth_mesh.messages.generics import (
    OptionalSetParameters,
    TransitionTime,
    TransitionTimeAdapter,
)
from bluetooth_mesh.messages.util import EnumAdapter, Opcode


class GenericLevelOpcode(IntEnum):
    GENERIC_LEVEL_GET = 0x8205
    GENERIC_LEVEL_SET = 0x8206
    GENERIC_LEVEL_SET_UNACKNOWLEDGED = 0x8207
    GENERIC_LEVEL_STATUS = 0x8208
    GENERIC_DELTA_SET = 0x8209
    GENERIC_DELTA_SET_UNACKNOWLEDGED = 0x820A
    GENERIC_MOVE_SET = 0x820B
    GENERIC_MOVE_SET_UNACKNOWLEDGED = 0x820C


# fmt: off
GenericLevelGet = CapNProtoStruct()

GenericLevelSetMinimal = CapNProtoStruct(
    "level" / Int16sl,
    "tid" / Int8ul
)

GenericLevelSetOptional = CapNProtoStruct(
    Embedded(GenericLevelSetMinimal),
    Embedded(OptionalSetParameters)
)

GenericLevelSet = Select(
    optional=GenericLevelSetOptional,
    minimal=GenericLevelSetMinimal
)

GenericDeltaSetMinimal = CapNProtoStruct(
    "delta_level" / Int32sl,
    "tid" / Int8ul
)

GenericDeltaSetOptional = CapNProtoStruct(
    Embedded(GenericDeltaSetMinimal),
    Embedded(OptionalSetParameters)
)

GenericDeltaSet = Select(
    optional=GenericDeltaSetOptional,
    minimal=GenericDeltaSetMinimal
)

GenericMoveSetMinimal = CapNProtoStruct(
    "delta_level" / Int16sl,
    "tid" / Int8ul
)

GenericMoveSetOptional = CapNProtoStruct(
    Embedded(GenericMoveSetMinimal),
    Embedded(OptionalSetParameters)
)

GenericMoveSet = Select(
    optional=GenericMoveSetOptional,
    minimal=GenericMoveSetMinimal
)

GenericLevelStatusMinimal = CapNProtoStruct(
    "present_level" / Int16sl
)

GenericLevelStatusOptional = CapNProtoStruct(
    Embedded(GenericLevelStatusMinimal),
    "target_level" / Int16sl,
    "remaining_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=True)
)

GenericLevelStatus = Select(
    optional=GenericLevelStatusOptional,
    minimal=GenericLevelStatusMinimal
)

GenericLevelDict = {
    GenericLevelOpcode.GENERIC_LEVEL_GET: GenericLevelGet,
    GenericLevelOpcode.GENERIC_LEVEL_SET: GenericLevelSet,
    GenericLevelOpcode.GENERIC_LEVEL_SET_UNACKNOWLEDGED: GenericLevelSet,
    GenericLevelOpcode.GENERIC_LEVEL_STATUS: GenericLevelStatus,
    GenericLevelOpcode.GENERIC_DELTA_SET: GenericDeltaSet,
    GenericLevelOpcode.GENERIC_DELTA_SET_UNACKNOWLEDGED: GenericDeltaSet,
    GenericLevelOpcode.GENERIC_MOVE_SET: GenericMoveSet,
    GenericLevelOpcode.GENERIC_MOVE_SET_UNACKNOWLEDGED: GenericMoveSet,
}

GenericLevelMessage = Struct(
    "opcode" / Opcode(GenericLevelOpcode),
    "params" / Switch(
        this.opcode,
        GenericLevelDict,
    )
)
# fmt: on
