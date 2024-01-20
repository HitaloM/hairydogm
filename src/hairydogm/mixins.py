# SPDX-License-Identifier: MIT
# Copyright (c) 2017-2023 Alex Root Junior <https://github.com/JrooTJunior>
# Copyright (c) 2023-present Hitalo M. <https://github.com/HitaloM>

import contextvars
from typing import Any, Generic, TypeVar

ContextInstance = TypeVar("ContextInstance")


class ContextInstanceMixin(Generic[ContextInstance]):
    """
    Mixin class for managing context instances.

    This mixin class is responsible for managing context instances.
    """

    __context_instance: contextvars.ContextVar[ContextInstance]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Initialize a subclass of the parent class.

        This method is automatically called when a subclass is created.
        It sets the `__context_instance` attribute of the subclass to a `ContextVar` instance.

        Parameters
        ----------
        **kwargs : typing.Any
            Keyword arguments.
        """
        super().__init_subclass__()
        cls.__context_instance = contextvars.ContextVar(f"instance_{cls.__name__}")

    @classmethod
    def get_current(cls, no_error: bool = True) -> ContextInstance | None:
        """
        Get the current context instance.

        This method returns the current context instance, or None if no context instance is found.

        Parameters
        ----------
        no_error : bool, optional
            If True, return None if no context instance is found. If False, raise an error.

        Returns
        -------
        ContextInstance | None
            The current context instance, or None if no context instance is found.

        Raises
        ------
        LookupError
            If no context instance is found and `no_error` is False.
        """
        try:
            return cls.__context_instance.get()
        except LookupError:
            if no_error:
                return None
            raise

    @classmethod
    def set_current(cls, value: ContextInstance) -> contextvars.Token[ContextInstance]:
        """
        Set the current context instance.

        This method sets the current context instance to the provided value.

        Parameters
        ----------
        value : ContextInstance
            The context instance to set.

        Returns
        -------
        contextvars.Token[ContextInstance]
            A token representing the context instance.

        Raises
        ------
        TypeError
            If the provided value is not an instance of the expected type.
        """
        if not isinstance(value, cls):
            raise TypeError(
                f"Value should be instance of {cls.__name__!r} not {type(value).__name__!r}"
            )
        return cls.__context_instance.set(value)  # type: ignore

    @classmethod
    def reset_current(cls, token: contextvars.Token[ContextInstance]) -> None:
        """
        Reset the current context instance.

        This method resets the current context instance using the provided token.

        Parameters
        ----------
        token : contextvars.Token[ContextInstance]
            A token representing the context instance to reset.
        """
        cls.__context_instance.reset(token)
