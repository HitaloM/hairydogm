# SPDX-License-Identifier: MIT
# Copyright (c) 2017-2023 Alex Root Junior <https://github.com/JrooTJunior>
# Copyright (c) 2023-present Hitalo M. <https://github.com/HitaloM>

from typing import Any

from hydrogram.filters import Filter


class BaseFilter(Filter):
    def _signature_to_string(self, *args: Any, **kwargs: Any) -> str:
        """
        Convert the signature to a string representation.

        This method takes the arguments and keyword arguments passed to the filter and
        converts them into a string representation.

        Parameters
        ----------
        *args :
            Variable length arguments.
        **kwargs :
            Keyword arguments.

        Returns
        -------
        str
            A string representation of the filter signature.
        """
        items = [repr(arg) for arg in args]
        items.extend([f"{k}={v!r}" for k, v in kwargs.items() if v is not None])

        return f"{type(self).__name__}({', '.join(items)})"
