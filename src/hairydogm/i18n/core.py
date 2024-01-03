# SPDX-License-Identifier: MIT
# Copyright (c) 2017-2023 Alex Root Junior <https://github.com/JrooTJunior>
# Copyright (c) 2023-present Hitalo M. <https://github.com/HitaloM>

import gettext
import os
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path

from babel.support import LazyProxy

from hairydogm.mixins import ContextInstanceMixin


class I18n(ContextInstanceMixin["I18n"]):
    """
    Internationalization class for managing translations.

    This class is responsible for managing translations for the bot and its
    extensions. It is used to load translations from the filesystem and to
    translate strings.

    Parameters
    ----------
    path : str or Path
        The path to the directory containing the translation files.
    default_locale : str, optional
        The default locale to use if no locale is specified. Default is "en".
    domain : str, optional
        The translation domain. Default is "bot".
    """

    def __init__(
        self,
        *,
        path: str | Path,
        default_locale: str = "en",
        domain: str = "bot",
    ) -> None:
        self.path = Path(path)
        self.default_locale = default_locale
        self.domain = domain
        self.ctx_locale = ContextVar("hydrogram_ctx_locale", default=default_locale)
        self.locales = self.find_locales()

    @property
    def current_locale(self) -> str:
        """
        Return the current locale.

        This method returns the current locale.

        Returns
        -------
        str
            The current locale.
        """
        return self.ctx_locale.get()

    @current_locale.setter
    def current_locale(self, value: str) -> None:
        """
        Set the current locale.

        This method sets the current locale to the provided value.

        Parameters
        ----------
        value : str
            The locale value to set.
        """
        self.ctx_locale.set(value)

    @contextmanager
    def use_locale(self, locale: str) -> Generator[None, None, None]:
        """
        Context manager for temporarily setting the locale.

        This method is used to create a context manager that allows temporarily
        setting the locale within a specific block of code. The locale is set
        using the `ctx_locale` attribute of the `self` object. After the block
        of code is executed, the locale is reset to its previous value.

        Parameters
        ----------
        locale : str
            The locale to be set.

        Yields
        ------
        Generator[None, None, None]
            A generator that yields None.
        """
        ctx_token = self.ctx_locale.set(locale)
        try:
            yield
        finally:
            self.ctx_locale.reset(ctx_token)

    @contextmanager
    def context(self) -> Generator["I18n", None, None]:
        """
        Context manager for using the I18n instance as the current instance.

        This method is used to create a context manager that allows accessing
        the current I18n instance within a `with` statement. The current
        instance is set as the context manager's target and is yielded to the
        caller. After the `with` statement block is executed, the current
        instance is reset to its previous value.

        Yields
        ------
        I18n
            The current I18n instance.
        """
        token = self.set_current(self)
        try:
            yield self
        finally:
            self.reset_current(token)

    def find_locales(self) -> dict[str, gettext.GNUTranslations]:
        """
        Find and load translations for all available locales.

        This method finds all available locales and loads their translations

        Returns
        -------
        dict[str, gettext.GNUTranslations]
            A dictionary mapping locale names to gettext.GNUTranslations objects.
        """
        translations: dict[str, gettext.GNUTranslations] = {}

        for name in os.listdir(self.path):
            locale_path = self.path / name
            if not locale_path.is_dir():
                continue

            mo_path = locale_path / "LC_MESSAGES" / f"{self.domain}.mo"
            if mo_path.exists():
                with mo_path.open("rb") as fp:
                    translations[name] = gettext.GNUTranslations(fp)
            elif mo_path.with_suffix(".po").exists():
                raise RuntimeError(f"Found locale '{name}' but this language is not compiled!")

        return translations

    def reload(self) -> None:
        """
        Reload the locales for the i18n core.

        This method updates the `locales` attribute of the i18n core by finding
        all available locales.
        """
        self.locales = self.find_locales()

    @property
    def available_locales(self) -> tuple[str, ...]:
        """
        Return a tuple of available locales.

        This method returns a tuple containing the available locales.

        Returns
        -------
        tuple[str, ...]
            A tuple containing the available locales.
        """
        return tuple(self.locales.keys())

    def gettext(
        self, singular: str, plural: str | None = None, n: int = 1, locale: str | None = None
    ) -> str:
        """
        Get the translated string based on the provided parameters.

        This method returns the translated string based on the provided parameters.

        Parameters
        ----------
        singular : str
            The singular form of the string to be translated.
        plural : str | None, optional
            The plural form of the string to be translated, if applicable. Defaults to None.
        n : int, optional
            The count of the string, used to determine the plural form. Defaults to 1.
        locale : str | None, optional
            The locale to be used for translation. Defaults to None.

        Returns
        -------
        str
            The translated string.
        """
        locale = locale or self.current_locale

        if locale in self.locales:
            translator = self.locales[locale]
            return (
                translator.ngettext(singular, plural, n)
                if plural
                else translator.gettext(singular)
            )

        return singular if n == 1 else plural or singular

    def lazy_gettext(
        self, singular: str, plural: str | None = None, n: int = 1, locale: str | None = None
    ) -> LazyProxy:
        """
        Return a lazy proxy for translating a message.

        This method returns a lazy proxy object that represents the translated message.

        Parameters
        ----------
        singular : str
            The singular form of the message to be translated.
        plural : str, optional
            The plural form of the message to be translated, by default None.
        n : int, optional
            The number used to determine the plural form, by default 1.
        locale : str, optional
            The locale to be used for translation, by default None.

        Returns
        -------
        LazyProxy
            A lazy proxy object that represents the translated message.
        """
        return LazyProxy(
            self.gettext, singular=singular, plural=plural, n=n, locale=locale, enable_cache=False
        )
