# SPDX-License-Identifier: MIT
# Copyright (c) 2017-2024 Alex Root Junior <https://github.com/JrooTJunior>
# Copyright (c) 2024-present Hitalo M. <https://github.com/HitaloM>

from __future__ import annotations

import asyncio
import logging
import time
from asyncio import Event, Lock
from contextlib import suppress
from typing import TYPE_CHECKING, Any

from hydrogram.enums import ChatAction

if TYPE_CHECKING:
    from types import TracebackType

    from hydrogram import Client

logger = logging.getLogger(__name__)

DEFAULT_INTERVAL = 5.0
DEFAULT_INITIAL_SLEEP = 0.0


class ChatActionSender:
    def __init__(
        self,
        *,
        client: Client,
        chat_id: str | int,
        message_thread_id: int | None = None,
        action: ChatAction = ChatAction.TYPING,
        interval: float = DEFAULT_INTERVAL,
        initial_sleep: float = DEFAULT_INITIAL_SLEEP,
    ) -> None:
        self.chat_id = chat_id
        self.message_thread_id = message_thread_id
        self.action = action
        self.interval = interval
        self.initial_sleep = initial_sleep
        self.client = client

        self._lock = Lock()
        self._close_event = Event()
        self._closed_event = Event()
        self._task: asyncio.Task[Any] | None = None

    @property
    def running(self) -> bool:
        return bool(self._task)

    async def _wait(self, interval: float) -> None:
        with suppress(asyncio.TimeoutError):
            await asyncio.wait_for(self._close_event.wait(), interval)

    async def _worker(self) -> None:
        if not self.client.me:
            msg = "Bot is not started"
            raise RuntimeError(msg)

        logger.debug(
            "Started chat action %r sender in chat_id=%s via bot id=%d",
            self.action,
            self.chat_id,
            self.client.me.id,
        )
        try:
            counter = 0
            await self._wait(self.initial_sleep)
            while not self._close_event.is_set():
                start = time.monotonic()
                logger.debug(
                    "Sent chat action %r to chat_id=%s via bot %d (already sent actions %d)",
                    self.action,
                    self.chat_id,
                    self.client.me.id,
                    counter,
                )
                await self.client.send_chat_action(
                    chat_id=self.chat_id,
                    action=self.action,
                    message_thread_id=self.message_thread_id,
                )
                counter += 1

                interval = self.interval - (time.monotonic() - start)
                await self._wait(interval)
        finally:
            logger.debug(
                "Finished chat action %r sender in chat_id=%s via bot id=%d",
                self.action,
                self.chat_id,
                self.client.me.id,
            )
            self._closed_event.set()

    async def _run(self) -> None:
        async with self._lock:
            self._close_event.clear()
            self._closed_event.clear()
            if self.running:
                msg = "Already running"
                raise RuntimeError(msg)
            self._task = asyncio.create_task(self._worker())

    async def _stop(self) -> None:
        async with self._lock:
            if not self.running:
                return
            if not self._close_event.is_set():
                self._close_event.set()
                await self._closed_event.wait()
            self._task = None

    async def __aenter__(self) -> ChatActionSender:
        await self._run()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Any:
        await self._stop()

    @classmethod
    def typing(
        cls,
        chat_id: int | str,
        client: Client,
        message_thread_id: int | None = None,
        interval: float = DEFAULT_INTERVAL,
        initial_sleep: float = DEFAULT_INITIAL_SLEEP,
    ) -> ChatActionSender:
        return cls(
            client=client,
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            action=ChatAction.TYPING,
            interval=interval,
            initial_sleep=initial_sleep,
        )

    @classmethod
    def upload_photo(
        cls,
        chat_id: int | str,
        client: Client,
        message_thread_id: int | None = None,
        interval: float = DEFAULT_INTERVAL,
        initial_sleep: float = DEFAULT_INITIAL_SLEEP,
    ) -> ChatActionSender:
        return cls(
            client=client,
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            action=ChatAction.UPLOAD_PHOTO,
            interval=interval,
            initial_sleep=initial_sleep,
        )

    @classmethod
    def record_video(
        cls,
        chat_id: int | str,
        client: Client,
        message_thread_id: int | None = None,
        interval: float = DEFAULT_INTERVAL,
        initial_sleep: float = DEFAULT_INITIAL_SLEEP,
    ) -> ChatActionSender:
        return cls(
            client=client,
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            action=ChatAction.RECORD_VIDEO,
            interval=interval,
            initial_sleep=initial_sleep,
        )

    @classmethod
    def upload_video(
        cls,
        chat_id: int | str,
        client: Client,
        message_thread_id: int | None = None,
        interval: float = DEFAULT_INTERVAL,
        initial_sleep: float = DEFAULT_INITIAL_SLEEP,
    ) -> ChatActionSender:
        return cls(
            client=client,
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            action=ChatAction.UPLOAD_VIDEO,
            interval=interval,
            initial_sleep=initial_sleep,
        )

    @classmethod
    def record_audio(
        cls,
        chat_id: int | str,
        client: Client,
        message_thread_id: int | None = None,
        interval: float = DEFAULT_INTERVAL,
        initial_sleep: float = DEFAULT_INITIAL_SLEEP,
    ) -> ChatActionSender:
        return cls(
            client=client,
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            action=ChatAction.RECORD_AUDIO,
            interval=interval,
            initial_sleep=initial_sleep,
        )

    @classmethod
    def upload_audio(
        cls,
        chat_id: int | str,
        client: Client,
        message_thread_id: int | None = None,
        interval: float = DEFAULT_INTERVAL,
        initial_sleep: float = DEFAULT_INITIAL_SLEEP,
    ) -> ChatActionSender:
        return cls(
            client=client,
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            action=ChatAction.UPLOAD_AUDIO,
            interval=interval,
            initial_sleep=initial_sleep,
        )

    @classmethod
    def upload_document(
        cls,
        chat_id: int | str,
        client: Client,
        message_thread_id: int | None = None,
        interval: float = DEFAULT_INTERVAL,
        initial_sleep: float = DEFAULT_INITIAL_SLEEP,
    ) -> ChatActionSender:
        return cls(
            client=client,
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            action=ChatAction.UPLOAD_DOCUMENT,
            interval=interval,
            initial_sleep=initial_sleep,
        )

    @classmethod
    def choose_sticker(
        cls,
        chat_id: int | str,
        client: Client,
        message_thread_id: int | None = None,
        interval: float = DEFAULT_INTERVAL,
        initial_sleep: float = DEFAULT_INITIAL_SLEEP,
    ) -> ChatActionSender:
        return cls(
            client=client,
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            action=ChatAction.CHOOSE_STICKER,
            interval=interval,
            initial_sleep=initial_sleep,
        )

    @classmethod
    def find_location(
        cls,
        chat_id: int | str,
        client: Client,
        message_thread_id: int | None = None,
        interval: float = DEFAULT_INTERVAL,
        initial_sleep: float = DEFAULT_INITIAL_SLEEP,
    ) -> ChatActionSender:
        return cls(
            client=client,
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            action=ChatAction.FIND_LOCATION,
            interval=interval,
            initial_sleep=initial_sleep,
        )

    @classmethod
    def record_video_note(
        cls,
        chat_id: int | str,
        client: Client,
        message_thread_id: int | None = None,
        interval: float = DEFAULT_INTERVAL,
        initial_sleep: float = DEFAULT_INITIAL_SLEEP,
    ) -> ChatActionSender:
        return cls(
            client=client,
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            action=ChatAction.RECORD_VIDEO_NOTE,
            interval=interval,
            initial_sleep=initial_sleep,
        )

    @classmethod
    def upload_video_note(
        cls,
        chat_id: int | str,
        client: Client,
        message_thread_id: int | None = None,
        interval: float = DEFAULT_INTERVAL,
        initial_sleep: float = DEFAULT_INITIAL_SLEEP,
    ) -> ChatActionSender:
        return cls(
            client=client,
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            action=ChatAction.UPLOAD_VIDEO_NOTE,
            interval=interval,
            initial_sleep=initial_sleep,
        )
