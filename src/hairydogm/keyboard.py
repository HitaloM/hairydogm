# SPDX-License-Identifier: MIT
# Copyright (c) 2017-2023 Alex Root Junior <https://github.com/JrooTJunior>
# Copyright (c) 2023-present Hitalo M. <https://github.com/HitaloM>

from __future__ import annotations

from copy import deepcopy
from itertools import chain, cycle
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    TypeVar,
    cast,
)

from hydrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from hairydogm.filters.callback_data import CallbackData

if TYPE_CHECKING:
    from collections.abc import Generator

ButtonType = TypeVar("ButtonType", bound=InlineKeyboardButton)
T = TypeVar("T")


class InlineKeyboardBuilder(Generic[ButtonType]):
    max_width: int = 8
    min_width: int = 1
    max_buttons: int = 100

    def __init__(
        self,
        button_type: type[ButtonType] = InlineKeyboardButton,
        markup: list[list[ButtonType]] | None = None,
    ) -> None:
        self._button_type: type[ButtonType] = button_type
        self._markup: list[list[ButtonType]] = markup or []
        if markup:
            self._validate_markup(markup)

    @property
    def buttons(self) -> Generator[ButtonType, None, None]:
        yield from chain.from_iterable(self.export())

    def _validate_button(self, button: ButtonType) -> None:
        allowed = self._button_type
        if not isinstance(button, allowed):
            msg = f"{button!r} should be type {allowed.__name__!r} not {type(button).__name__!r}"
            raise ValueError(msg)

    def _validate_buttons(self, *buttons: ButtonType) -> bool:
        return all(map(self._validate_button, buttons))

    def _validate_row(self, row: list[ButtonType]) -> None:
        if not isinstance(row, list):
            msg = (
                f"Row {row!r} should be type 'List[{self._button_type.__name__}]' "
                f"not type {type(row).__name__}"
            )
            raise ValueError(msg)
        if len(row) > self.max_width:
            msg = f"Row {row!r} is too long (max width: {self.max_width})"
            raise ValueError(msg)
        self._validate_buttons(*row)

    def _validate_markup(self, markup: list[list[ButtonType]]) -> None:
        if not isinstance(markup, list):
            msg = (
                f"Markup should be type 'List[List[{self._button_type.__name__}]]' "
                f"not type {type(markup).__name__!r}"
            )
            raise ValueError(msg)
        count = sum(len(row) for row in markup)
        if count > self.max_buttons:
            msg = f"Too much buttons detected Max allowed count - {self.max_buttons}"
            raise ValueError(msg)
        for row in markup:
            self._validate_row(row)

    def _validate_size(self, size: Any) -> None:
        if not isinstance(size, int):
            msg = "Only int sizes are allowed"
            raise ValueError(msg)
        if size not in range(self.min_width, self.max_width + 1):
            msg = f"Row size {size} is not allowed, range: [{self.min_width}, {self.max_width}]"
            raise ValueError(msg)

    def copy(self: InlineKeyboardBuilder[ButtonType]) -> InlineKeyboardBuilder[ButtonType]:
        return self.__class__(self._button_type, markup=self.export())

    @classmethod
    def from_markup(
        cls: type[InlineKeyboardBuilder[ButtonType]], markup: InlineKeyboardMarkup
    ) -> InlineKeyboardBuilder[InlineKeyboardButton]:
        return cls(markup=markup.inline_keyboard)

    def export(self) -> list[list[ButtonType]]:
        return deepcopy(self._markup)

    def add(self, *buttons: ButtonType) -> InlineKeyboardBuilder[ButtonType]:
        markup = self.export()

        if markup and len(markup[-1]) < self.max_width:
            last_row = markup[-1]
            pos = self.max_width - len(last_row)
            head, buttons = buttons[:pos], buttons[pos:]
            last_row.extend(head)

        while buttons:
            row, buttons = buttons[: self.max_width], buttons[self.max_width :]
            markup.append(list(row))

        self._markup = markup
        return self

    def row(
        self, *buttons: ButtonType, width: int | None = None
    ) -> InlineKeyboardBuilder[ButtonType]:
        if width is None:
            width = self.max_width

        self._validate_size(width)
        self._validate_buttons(*buttons)
        self._markup.extend(
            list(buttons[pos : pos + width]) for pos in range(0, len(buttons), width)
        )
        return self

    def adjust(self, *sizes: int, repeat: bool = False) -> InlineKeyboardBuilder[ButtonType]:
        sizes = sizes or (self.max_width,)
        sizes_iter = cycle(sizes) if repeat else chain(sizes, cycle([sizes[-1]]))
        markup = []
        row = []

        for button in self.buttons:
            if len(row) >= next(sizes_iter):
                markup.append(row)
                row = []
            row.append(button)

        if row:
            markup.append(row)

        self._markup = markup
        return self

    def button(self, **kwargs: Any) -> InlineKeyboardBuilder[ButtonType]:
        if isinstance(callback_data := kwargs.get("callback_data", None), CallbackData):
            kwargs["callback_data"] = callback_data.pack()

        button = self._button_type(**kwargs)
        return self.add(button)

    def as_markup(self) -> InlineKeyboardMarkup:
        inline_keyboard = cast(list[list[InlineKeyboardButton]], self.export())
        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    def attach(
        self, builder: InlineKeyboardBuilder[ButtonType]
    ) -> InlineKeyboardBuilder[ButtonType]:
        if builder._button_type is not self._button_type:
            msg = (
                f"Only builders with same button type can be attached, "
                f"not {self._button_type.__name__} and {builder._button_type.__name__}"
            )
            raise ValueError(msg)
        self._markup.extend(builder.export())
        return self
