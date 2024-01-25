# SPDX-License-Identifier: MIT
# Copyright (c) 2017-2023 Alex Root Junior <https://github.com/JrooTJunior>
# Copyright (c) 2023-present Hitalo M. <https://github.com/HitaloM>

from typing import Any

from babel.support import LazyProxy

from hairydogm.i18n.core import I18n


def get_i18n() -> I18n:
    """
    Get the current I18n context.

    This function returns the current I18n context.

    Returns
    -------
    I18n
        The current I18n context.

    Raises
    ------
    LookupError
        If the I18n context is not set.
    """
    if (i18n := I18n.get_current(no_error=True)) is None:
        raise LookupError("I18n context is not set")
    return i18n


def gettext(*args: Any, **kwargs: Any) -> str:
    """
    Get the translated string for the given message.

    This function returns the translated string for the given message.

    Parameters
    ----------
    *args : typing.Any
        Positional arguments for the message.
    **kwargs : typing.Any
        Keyword arguments for the message.

    Returns
    -------
    str
        The translated string.
    """
    return get_i18n().gettext(*args, **kwargs)


def lazy_gettext(*args: Any, **kwargs: Any) -> LazyProxy:
    """
    Return a lazy proxy object for translating text.

    This can be used, for example, to implement lazy translation functions that delay the actual
    translation until the string is actually used. The rationale for such behavior is that the
    locale of the user may not always be available. In web applications, you only know the locale
    when processing a request.

    Parameters
    ----------
    *args : typing.Any
        Positional arguments to be passed to the `gettext` function.
    **kwargs : typing.Any
        Keyword arguments to be passed to the `gettext` function.

    Returns
    -------
    LazyProxy
        A lazy proxy object that represents the translated text.
    """
    return LazyProxy(gettext, *args, **kwargs, enable_cache=False)


ngettext = gettext
lazy_ngettext = lazy_gettext
