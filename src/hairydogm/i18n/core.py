# SPDX-License-Identifier: MIT
# Copyright (c) 2017-2023 Alex Root Junior <https://github.com/JrooTJunior>
# Copyright (c) 2023-present Hitalo M. <https://github.com/HitaloM>

from __future__ import annotations

import gettext
import os
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import TYPE_CHECKING

from babel.support import LazyProxy

from hairydogm.mixins import ContextInstanceMixin

if TYPE_CHECKING:
    from collections.abc import Generator


class I18n(ContextInstanceMixin["I18n"]):
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
        return self.ctx_locale.get()

    @current_locale.setter
    def current_locale(self, value: str) -> None:
        self.ctx_locale.set(value)

    @contextmanager
    def use_locale(self, locale: str) -> Generator[None, None, None]:
        ctx_token = self.ctx_locale.set(locale)
        try:
            yield
        finally:
            self.ctx_locale.reset(ctx_token)

    @contextmanager
    def context(self) -> Generator[I18n, None, None]:
        token = self.set_current(self)
        try:
            yield self
        finally:
            self.reset_current(token)

    def find_locales(self) -> dict[str, gettext.GNUTranslations]:
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
                msg = f"Found locale '{name}' but this language is not compiled!"
                raise RuntimeError(msg)

        return translations

    def reload(self) -> None:
        self.locales = self.find_locales()

    @property
    def available_locales(self) -> tuple[str, ...]:
        return tuple(self.locales.keys())

    def gettext(
        self, singular: str, plural: str | None = None, n: int = 1, locale: str | None = None
    ) -> str:
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
        return LazyProxy(
            self.gettext, singular=singular, plural=plural, n=n, locale=locale, enable_cache=False
        )
