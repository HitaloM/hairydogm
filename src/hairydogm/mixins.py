# SPDX-License-Identifier: MIT
# Copyright (c) 2017-2023 Alex Root Junior <https://github.com/JrooTJunior>
# Copyright (c) 2023-present Hitalo M. <https://github.com/HitaloM>

import contextvars
from typing import Any, Generic, TypeVar

ContextInstance = TypeVar("ContextInstance")


class ContextInstanceMixin(Generic[ContextInstance]):
    __context_instance: contextvars.ContextVar[ContextInstance]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__()
        cls.__context_instance = contextvars.ContextVar(f"instance_{cls.__name__}")

    @classmethod
    def get_current(cls, no_error: bool = True) -> ContextInstance | None:
        try:
            return cls.__context_instance.get()
        except LookupError:
            if no_error:
                return None
            raise

    @classmethod
    def set_current(cls, value: ContextInstance) -> contextvars.Token[ContextInstance]:
        if not isinstance(value, cls):
            msg = f"Value should be instance of {cls.__name__!r} not {type(value).__name__!r}"
            raise TypeError(msg)
        return cls.__context_instance.set(value)  # type: ignore

    @classmethod
    def reset_current(cls, token: contextvars.Token[ContextInstance]) -> None:
        cls.__context_instance.reset(token)
