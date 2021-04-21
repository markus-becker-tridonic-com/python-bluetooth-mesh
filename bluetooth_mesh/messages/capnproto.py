from enum import Enum
from typing import Optional, Tuple, Union

from construct import (
    Adapter,
    BitsInteger,
    BytesInteger,
    Construct,
    FormatField,
    Renamed,
    Struct,
)


class CapNProtoPrimitiveTypes(Enum):
    UINT8 = "UInt8"
    UINT16 = "UInt16"
    UINT32 = "UInt32"
    UINT64 = "UInt64"
    INT8 = "Int8"
    INT16 = "Int16"
    INT32 = "Int32"
    INT64 = "Int64"
    FLOAT32 = "Float32"
    FLOAT64 = "Float64"
    VOID = "Void"
    BOOL = "Bool"
    DATA = "Data"
    TEXT = "Text"
    UNKNOWN = "UNKNOWN"


class CapNProtoTypeAdapter(Adapter):

    __capnproto_type__ = None

    def _decode(self, obj, content, path):
        return obj

    def _encode(self, obj, content, path):
        return obj

    @property
    def capnproto_type(self) -> str:
        return self.__capnproto_type__


class CapNProtoStruct(Struct):
    pass


def extract_renamed(
    subcon: Union[Construct, Renamed]
) -> Tuple[Optional[str], Construct]:
    if isinstance(subcon, Renamed):
        return subcon.name, subcon.subcon

    return None, subcon


def format_field_to_type(subcon: FormatField) -> str:
    __TYPE_MAP = dict(
        c=CapNProtoPrimitiveTypes.UINT8,
        b=CapNProtoPrimitiveTypes.INT8,
        B=CapNProtoPrimitiveTypes.UINT8,
        h=CapNProtoPrimitiveTypes.INT16,
        H=CapNProtoPrimitiveTypes.UINT16,
        i=CapNProtoPrimitiveTypes.INT32,
        I=CapNProtoPrimitiveTypes.UINT32,
        l=CapNProtoPrimitiveTypes.INT32,
        L=CapNProtoPrimitiveTypes.UINT32,
        q=CapNProtoPrimitiveTypes.INT64,
        Q=CapNProtoPrimitiveTypes.UINT64,
        f=CapNProtoPrimitiveTypes.FLOAT32,
        d=CapNProtoPrimitiveTypes.FLOAT64,
    )

    return __TYPE_MAP[subcon.fmtstr[1]].value


def bytes_integer_to_type(subcon: BytesInteger) -> str:
    length = subcon.length

    if length == 1:
        return CapNProtoPrimitiveTypes.INT8.value
    elif length == 2:
        return CapNProtoPrimitiveTypes.INT16.value
    elif length <= 4:
        return CapNProtoPrimitiveTypes.INT32.value
    elif length <= 8:
        return CapNProtoPrimitiveTypes.INT64.value
    else:
        raise ValueError(f"BytesInteger length: {length} is too high")


def bits_count_to_uint_type(bits_count: int) -> str:
    if bits_count <= 8:
        return CapNProtoPrimitiveTypes.UINT8.value
    elif bits_count <= 16:
        return CapNProtoPrimitiveTypes.UINT16.value
    elif bits_count <= 32:
        return CapNProtoPrimitiveTypes.UINT32.value
    elif bits_count <= 64:
        return CapNProtoPrimitiveTypes.UINT64.value
    else:
        raise ValueError(f"Bits count: {bits_count} is too high")


def bits_integer_to_type(subcon: BitsInteger) -> str:
    return bits_count_to_uint_type(subcon.length)
