# SPDX-License-Identifier: MIT
# Copyright (c) 2017-2023 Alex Root Junior <https://github.com/JrooTJunior>
# Copyright (c) 2023-present Hitalo M. <https://github.com/HitaloM>

from .context import get_i18n, gettext, lazy_gettext, lazy_ngettext, ngettext
from .core import I18n

__all__ = (
    "get_i18n",
    "gettext",
    "lazy_gettext",
    "lazy_ngettext",
    "ngettext",
    "I18n",
)
