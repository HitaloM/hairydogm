# SPDX-License-Identifier: MIT
# Copyright (c) 2017-2023 Alex Root Junior <https://github.com/JrooTJunior>
# Copyright (c) 2023-present Hitalo M. <https://github.com/HitaloM>

from typing import Any

from babel.support import LazyProxy

from hairydogm.i18n.core import I18n


def get_i18n() -> I18n:
    if (i18n := I18n.get_current(no_error=True)) is None:
        msg = "I18n context is not set"
        raise LookupError(msg)
    return i18n


def gettext(*args: Any, **kwargs: Any) -> str:
    return get_i18n().gettext(*args, **kwargs)


def lazy_gettext(*args: Any, **kwargs: Any) -> LazyProxy:
    return LazyProxy(gettext, *args, **kwargs, enable_cache=False)


ngettext = gettext
lazy_ngettext = lazy_gettext
