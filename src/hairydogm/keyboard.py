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
    """
    A builder class for creating inline keyboards.

    This class provides methods for creating and manipulating inline keyboards.
    It allows you to add buttons, adjust the size of rows, convert the keyboard to a markup object,
    and attach another keyboard builder to the current keyboard.

    Parameters
    ----------
    button_type : Type[ButtonType], optional
        The type of buttons to be used in the keyboard, by default InlineKeyboardButton.
    markup : List[List[ButtonType]] | None, optional
        The initial markup of the keyboard, by default None.
    """

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
        """
        A generator that yields all the buttons in the keyboard.

        This method returns a generator that iterates over all the
        buttons in the keyboard and yields each button.

        Yields
        ------
        ButtonType
            The buttons in the keyboard.
        """
        yield from chain.from_iterable(self.export())

    def _validate_button(self, button: ButtonType) -> None:
        """
        Validate if a button is of the correct type.

        This method validates if a button is of the correct type.
        If the button is not of the correct type, a ValueError is raised.

        Parameters
        ----------
        button : ButtonType
            The button to validate.

        Raises
        ------
        ValueError
            If the button is not of the correct type.
        """
        allowed = self._button_type
        if not isinstance(button, allowed):
            msg = f"{button!r} should be type {allowed.__name__!r} not {type(button).__name__!r}"
            raise ValueError(msg)

    def _validate_buttons(self, *buttons: ButtonType) -> bool:
        """
        Validate if a list of buttons are of the correct type.

        This method checks if a list of buttons are of the correct type.
        It iterates over each button in the list and calls the `_validate_button`
        method to validate its type. If all buttons are of the correct type, it returns True.
        Otherwise, it returns False.

        Parameters
        ----------
        *buttons : ButtonType
            The buttons to be validated.

        Returns
        -------
        bool
            True if all buttons are of the correct type, False otherwise.
        """
        return all(map(self._validate_button, buttons))

    def _validate_row(self, row: list[ButtonType]) -> None:
        """
        Validate if a row of buttons is of the correct type and length.

        This method validates if a row of buttons is of the correct type and length.
        If the row is not of the correct type or length, a ValueError is raised.

        Parameters
        ----------
        row : List[ButtonType]
            The row of buttons to validate.

        Raises
        ------
        ValueError
            If the row is not of the correct type or length.
        """
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
        """
        Validate if the markup of the keyboard is of the correct type and structure.

        This method validates if the markup of the keyboard is of the correct type and structure.
        If the markup is not of the correct type or structure, a ValueError is raised.

        Parameters
        ----------
        markup : List[List[ButtonType]]
            The markup of the keyboard to validate.

        Raises
        ------
        ValueError
            If the markup is not of the correct type or structure.
        """
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
        """
        Validate if a size is a valid row size.

        This method validates if a size is a valid row size.
        If the size is not a valid row size, a ValueError is raised.

        Parameters
        ----------
        size : typing.Any
            The size to validate.

        Raises
        ------
        ValueError
            If the size is not a valid row size.
        """
        if not isinstance(size, int):
            msg = "Only int sizes are allowed"
            raise ValueError(msg)
        if size not in range(self.min_width, self.max_width + 1):
            msg = f"Row size {size} is not allowed, range: [{self.min_width}, {self.max_width}]"
            raise ValueError(msg)

    def copy(self: InlineKeyboardBuilder[ButtonType]) -> InlineKeyboardBuilder[ButtonType]:
        """
        Create a copy of the current InlineKeyboardBuilder instance.

        This method creates a new instance of the InlineKeyboardBuilder class with the
        same button type and markup as the current instance.

        Returns
        -------
        InlineKeyboardBuilder[ButtonType]
            A new instance of the InlineKeyboardBuilder class.
        """
        return self.__class__(self._button_type, markup=self.export())

    @classmethod
    def from_markup(
        cls: type[InlineKeyboardBuilder[ButtonType]], markup: InlineKeyboardMarkup
    ) -> InlineKeyboardBuilder[ButtonType]:
        """
        Create an instance of InlineKeyboardBuilder from an existing markup.

        This method creates an instance of InlineKeyboardBuilder from an existing markup.
        It takes an InlineKeyboardMarkup object as input and returns a new instance of
        InlineKeyboardBuilder.

        Parameters
        ----------
        markup : InlineKeyboardMarkup
            The markup to create the builder from.

        Returns
        -------
        InlineKeyboardBuilder[ButtonType]
            The created instance of InlineKeyboardBuilder.
        """
        return cls(markup=markup.inline_keyboard)

    def export(self) -> list[list[ButtonType]]:
        """
        Export the current keyboard markup.

        This method exports the current markup of the keyboard as a list of lists.
        Each inner list represents a row of buttons on the keyboard.
        The exported markup can be used to save or transfer the keyboard configuration.

        Returns
        -------
        List[List[ButtonType]]
            The exported markup of the keyboard.
        """
        return deepcopy(self._markup)

    def add(self, *buttons: ButtonType) -> InlineKeyboardBuilder[ButtonType]:
        """
        Add buttons to the keyboard.

        The buttons are added in rows, with each row containing a maximum of `MAX_WIDTH` buttons.
        If the last row of the keyboard has space available, the buttons will be added to it.
        If the last row is full, a new row will be created.

        Parameters
        ----------
        *buttons : ButtonType
            The buttons to add.

        Returns
        -------
        InlineKeyboardBuilder[ButtonType]
            The updated instance of InlineKeyboardBuilder.
        """
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
        """
        Add a row of buttons to the keyboard.

        This method adds a row of buttons to the keyboard.

        Parameters
        ----------
        *buttons : ButtonType
            The buttons to be added.
        width : int, optional
            The width of the row, defaults to MAX_WIDTH.

        Returns
        -------
        InlineKeyboardBuilder[ButtonType]
            The updated instance of InlineKeyboardBuilder.
        """
        if width is None:
            width = self.max_width

        self._validate_size(width)
        self._validate_buttons(*buttons)
        self._markup.extend(
            list(buttons[pos : pos + width]) for pos in range(0, len(buttons), width)
        )
        return self

    def adjust(self, *sizes: int, repeat: bool = False) -> InlineKeyboardBuilder[ButtonType]:
        """
        Adjust the size of the rows in the keyboard.

        This method adjusts the size of the rows in the keyboard. It takes a variable number
        of sizes as input, which represent the desired sizes for each row. If the `repeat`
        parameter is set to True, the sizes will be repeated cyclically until all rows are
        assigned a size. If `repeat` is False, the last size will be used for any remaining rows.

        Parameters
        ----------
        *sizes : int
            The sizes to adjust the rows to.
        repeat : bool, optional
            Whether to repeat the sizes cyclically, by default False.

        Returns
        -------
        InlineKeyboardBuilder[ButtonType]
            The updated instance of InlineKeyboardBuilder.
        """
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
        """
        Add a button to the keyboard.

        This method adds a button to the keyboard. The button is created using the provided
        keyword arguments.

        Parameters
        ----------
        **kwargs : typing.Any
            The keyword arguments to create the button.

        Returns
        -------
        InlineKeyboardBuilder[ButtonType]
            The updated instance of InlineKeyboardBuilder.
        """
        if isinstance(callback_data := kwargs.get("callback_data", None), CallbackData):
            kwargs["callback_data"] = callback_data.pack()

        button = self._button_type(**kwargs)
        return self.add(button)

    def as_markup(self) -> InlineKeyboardMarkup:
        """
        Convert the keyboard to a markup object.

        This method converts the keyboard to a markup object.
        The markup object can be used to send the keyboard to a user.

        Returns
        -------
        InlineKeyboardMarkup | ReplyKeyboardMarkup
            The converted markup object.
        """
        inline_keyboard = cast(list[list[InlineKeyboardButton]], self.export())
        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    def attach(
        self, builder: InlineKeyboardBuilder[ButtonType]
    ) -> InlineKeyboardBuilder[ButtonType]:
        """
        Attach another keyboard builder to the current keyboard.

        By calling this method, you can add another keyboard builder to the
        current keyboard object.

        Parameters
        ----------
        builder : InlineKeyboardBuilder[ButtonType]
            The builder to attach.

        Returns
        -------
        InlineKeyboardBuilder[ButtonType]
            The updated instance of InlineKeyboardBuilder.

        Raises
        ------
        ValueError
            If the button types of the builders do not match.
        """
        if builder._button_type is not self._button_type:
            msg = (
                f"Only builders with same button type can be attached, "
                f"not {self._button_type.__name__} and {builder._button_type.__name__}"
            )
            raise ValueError(msg)
        self._markup.extend(builder.export())
        return self
