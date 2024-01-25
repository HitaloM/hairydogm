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

from hydrogram import Client
from hydrogram.types import CallbackQuery
from magic_filter import MagicFilter
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from hairydogm.filters.base import BaseFilter

T = TypeVar("T", bound="CallbackData")

MAX_CALLBACK_LENGTH: int = 64


class CallbackData(BaseModel):
    """
    Base class for callback data wrapper.

    This class is used to create a wrapper for callback data.

    Attributes
    ----------
    __separator__ : ClassVar[str]
        Data separator (default is ':')
    __prefix__ : ClassVar[str]
        Callback prefix
    """

    __separator__: ClassVar[str]
    __prefix__: ClassVar[str]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if "prefix" not in kwargs:
            raise ValueError(
                f"prefix required, usage example: "
                f"`class {cls.__name__}(CallbackData, prefix='my_callback'): ...`"
            )
        separator = kwargs.get("sep", ":")
        prefix = kwargs.get("prefix")
        if separator in prefix:
            raise ValueError(
                f"Separator symbol {separator!r} can not be used " f"inside prefix {prefix!r}"
            )
        cls.__separator__ = kwargs.pop("sep", ":")
        cls.__prefix__ = kwargs.pop("prefix")
        super().__init_subclass__(**kwargs)

    def _encode_value(self, key: str, value: Any) -> str:
        """
        Encode the value to a string representation.

        This method is used to encode the value to a string representation.

        Parameters
        ----------
        key : str
            The key of the value.
        value : typing.Any
            The value to be encoded.

        Returns
        -------
        str
            The encoded value as a string.

        Raises
        ------
        ValueError
            If the value cannot be packed to callback data.
        """

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
        except KeyError:
            raise ValueError(
                f"Attribute {key}={value!r} of type {type(value).__name__!r}"
                f" can not be packed to callback data"
            )

    def pack(self) -> str:
        """
        Generate callback data string.

        This method is used to generate callback data string.

        Returns
        -------
        str
            The generated callback data string.

        Raises
        ------
        ValueError
            If the resulted callback data is too long.
        """

        result = [self.__prefix__]
        for key, value in self.model_dump(mode="json").items():
            encoded = self._encode_value(key, value)
            if self.__separator__ in encoded:
                raise ValueError(
                    f"Separator symbol {self.__separator__!r} can not be used "
                    f"in value {key}={encoded!r}"
                )
            result.append(encoded)
        callback_data = self.__separator__.join(result)
        if len(callback_data.encode()) > MAX_CALLBACK_LENGTH:
            raise ValueError(
                f"Resulted callback data is too long! "
                f"len({callback_data!r}.encode()) > {MAX_CALLBACK_LENGTH}"
            )
        return callback_data

    @classmethod
    def unpack(cls: type[T], value: str | bytes) -> T:
        """
        Parse callback data string.

        This method is used to parse callback data string.

        Parameters
        ----------
        value : str | bytes
            The value from Telegram.

        Returns
        -------
        T
            An instance of CallbackData.

        Raises
        ------
        TypeError
            If the number of arguments in the callback data does not match the number of fields in
            CallbackData.
        ValueError
            If the prefix in the callback data does not match the prefix in CallbackData.
        """

        prefix, *parts = str(value).split(cls.__separator__)
        names = cls.model_fields.keys()
        if len(parts) != len(names):
            raise TypeError(
                f"Callback data {cls.__name__!r} takes {len(names)} arguments "
                f"but {len(parts)} were given"
            )
        if prefix != cls.__prefix__:
            raise ValueError(f"Bad prefix ({prefix!r} != {cls.__prefix__!r})")

        nullable_fields = {
            k for k, field in cls.model_fields.items() if _check_field_is_nullable(field)
        }
        payload = {
            k: v if v != "" or k not in nullable_fields else None for k, v in zip(names, parts)
        }

        return cls(**payload)

    @classmethod
    def filter(cls, rule: MagicFilter | None = None) -> CallbackQueryFilter:
        """
        Generate a filter for callback query with rule.

        This method is used to generate a filter for callback query with rule.

        Parameters
        ----------
        rule : MagicFilter | None, optional
            The magic rule.

        Returns
        -------
        CallbackQueryFilter
            An instance of filter.
        """

        return CallbackQueryFilter(callback_data=cls, rule=rule)


class CallbackQueryFilter(BaseFilter):
    """
    This filter helps to handle callback query.

    Should not be used directly, you should create the instance of this filter
    via callback data instance

    Parameters
    ----------
    callback_data : type[CallbackData]
        Expected type of callback data.
    rule : MagicFilter or None, optional
        Magic rule.
    """

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

    def __str__(self) -> str:
        return self._signature_to_string(
            callback_data=self.callback_data,
            rule=self.rule,
        )

    async def __call__(
        self, client: Client, query: CallbackQuery
    ) -> Literal[False] | dict[str, Any]:
        """
        Execute the callback data filter.

        This method is used to execute the callback data filter.

        Parameters
        ----------
        client : Client
            The client instance.
        query : CallbackQuery
            The callback query object.

        Returns
        -------
        Literal[False] | dict[str, Any] :
            Returns False if the query is not a valid callback
            query or if the callback data cannot be unpacked. Otherwise, returns a dictionary
            containing the unpacked callback data.
        """
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
    """
    Check if the given field is nullable.

    This function is used to check if the field is nullable or not.

    Parameters
    ----------
    field : FieldInfo
        The field to be checked.

    Returns
    -------
    bool
        True if the field is nullable, False otherwise.
    """
    return not field.is_required() or (
        typing.get_origin(field.annotation) is typing.Union
        and None in typing.get_args(field.annotation)
    )
