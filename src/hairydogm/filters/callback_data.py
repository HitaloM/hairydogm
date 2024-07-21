# SPDX-License-Identifier: MIT
# Copyright (c) 2017-2023 Alex Root Junior <https://github.com/JrooTJunior>
# Copyright (c) 2023-present Hitalo M. <https://github.com/HitaloM>

from __future__ import annotations

import typing
from decimal import Decimal
from enum import Enum
from fractions import Fraction
from typing import (
    Any,
    ClassVar,
    Literal,
    TypeVar,
)
from uuid import UUID

from hydrogram.filters import Filter
from hydrogram.types import CallbackQuery
from pydantic import BaseModel

if typing.TYPE_CHECKING:
    from hydrogram import Client
    from magic_filter import MagicFilter
    from pydantic.fields import FieldInfo

T = TypeVar("T", bound="CallbackData")

MAX_CALLBACK_LENGTH: int = 64


class CallbackData(BaseModel):
    __separator__: ClassVar[str]
    __prefix__: ClassVar[str]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if "prefix" not in kwargs:
            msg = (
                f"prefix required, usage example: "
                f"`class {cls.__name__}(CallbackData, prefix='my_callback'): ...`"
            )
            raise ValueError(msg)
        separator = kwargs.get("sep", ":")
        prefix = kwargs.get("prefix")
        if separator in prefix:
            msg = f"Separator symbol {separator!r} can not be used " f"inside prefix {prefix!r}"
            raise ValueError(msg)
        cls.__separator__ = kwargs.pop("sep", ":")
        cls.__prefix__ = kwargs.pop("prefix")
        super().__init_subclass__(**kwargs)

    @staticmethod
    def _encode_value(key: str, value: Any) -> str:
        if value is None:
            return ""

        type_to_str = {
            Enum: lambda v: str(v.value),
            UUID: lambda v: v.hex,
            bool: lambda v: str(int(v)),
            int: str,
            str: str,
            float: str,
            Decimal: str,
            Fraction: str,
        }

        try:
            return type_to_str[type(value)](value)
        except KeyError as err:
            msg = (
                f"Attribute {key}={value!r} of type {type(value).__name__!r}"
                f" can not be packed to callback data"
            )
            raise ValueError(msg) from err

    def pack(self) -> str:
        result = [self.__prefix__]
        for key, value in self.model_dump(mode="json").items():
            encoded = self._encode_value(key, value)
            if self.__separator__ in encoded:
                msg = (
                    f"Separator symbol {self.__separator__!r} can not be used "
                    f"in value {key}={encoded!r}"
                )
                raise ValueError(msg)
            result.append(encoded)
        callback_data = self.__separator__.join(result)
        if len(callback_data.encode()) > MAX_CALLBACK_LENGTH:
            msg = (
                f"Resulted callback data is too long! "
                f"len({callback_data!r}.encode()) > {MAX_CALLBACK_LENGTH}"
            )
            raise ValueError(msg)
        return callback_data

    @classmethod
    def unpack(cls: type[T], value: str | bytes) -> T:
        prefix, *parts = str(value).split(cls.__separator__)
        names = cls.model_fields.keys()
        if len(parts) != len(names):
            msg = (
                f"Callback data {cls.__name__!r} takes {len(names)} arguments "
                f"but {len(parts)} were given"
            )
            raise TypeError(msg)
        if prefix != cls.__prefix__:
            msg = f"Bad prefix ({prefix!r} != {cls.__prefix__!r})"
            raise ValueError(msg)

        nullable_fields = {
            k for k, field in cls.model_fields.items() if _check_field_is_nullable(field)
        }
        payload = {
            k: v if v or k not in nullable_fields else None
            for k, v in zip(names, parts, strict=False)
        }

        return cls(**payload)

    @classmethod
    def filter(cls, rule: MagicFilter | None = None) -> CallbackQueryFilter:
        return CallbackQueryFilter(callback_data=cls, rule=rule)


class CallbackQueryFilter(Filter):
    __slots__ = (
        "callback_data",
        "rule",
    )

    def __init__(
        self,
        *,
        callback_data: type[CallbackData],
        rule: MagicFilter | None = None,
    ):
        self.callback_data = callback_data
        self.rule = rule

    async def __call__(
        self, client: Client, query: CallbackQuery
    ) -> Literal[False] | dict[str, Any]:
        if not isinstance(query, CallbackQuery) or not query.data:
            return False
        try:
            callback_data = self.callback_data.unpack(query.data)
        except (TypeError, ValueError):
            return False

        if self.rule is None or self.rule.resolve(callback_data):
            return {"callback_data": callback_data}
        return False


def _check_field_is_nullable(field: FieldInfo) -> bool:
    return not field.is_required() or (
        typing.get_origin(field.annotation) is typing.Union
        and None in typing.get_args(field.annotation)
    )
