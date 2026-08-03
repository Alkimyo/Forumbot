"""Forum topic retrieval module.

Wraps Telethon (MTProto) calls needed to resolve a group, verify it is a
forum, and fetch all of its topics.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from telethon import TelegramClient
from telethon.errors import (
    ChannelPrivateError,
    FloodWaitError,
    UsernameInvalidError,
    UsernameNotOccupiedError,
)
from telethon.tl.functions.channels import GetForumTopicsRequest
from telethon.tl.types import Channel

from sorter import sort_by_uzbek_alphabet


class ForumError(Exception):
    """Base class for forum-related errors."""


class GroupNotFoundError(ForumError):
    """Raised when the given username does not resolve to a group."""


class NotAForumError(ForumError):
    """Raised when the resolved group is not a forum."""


class UserbotNotMemberError(ForumError):
    """Raised when the userbot has no access to the group's contents."""


@dataclass(frozen=True)
class Topic:
    """Represents a single forum topic.

    Attributes:
        topic_id: The unique identifier of the topic within the group.
        title: The display name of the topic.
        message_id: The id of the topic's opening (root) message.
        link: A direct t.me link to the topic.
    """

    topic_id: int
    title: str
    message_id: int
    link: str


def _build_topic_link(group_username: str, topic_id: int) -> str:
    """Construct a t.me deep link pointing directly at a forum topic.

    Args:
        group_username: The group's public username, without "@".
        topic_id: The topic's identifier.

    Returns:
        A clickable https://t.me link that opens the topic directly.
    """
    return f"https://t.me/{group_username}/{topic_id}"


async def resolve_group(client: TelegramClient, username: str) -> Channel:
    """Resolve a username into a Telegram channel/supergroup entity.

    Args:
        client: An active, connected Telethon client.
        username: The group's public username (with or without "@").

    Returns:
        The resolved Channel entity.

    Raises:
        GroupNotFoundError: If the username does not exist or is invalid.
        UserbotNotMemberError: If the userbot cannot access the group.
    """
    clean_username = username.lstrip("@").strip()

    try:
        entity = await client.get_entity(clean_username)
    except (UsernameNotOccupiedError, UsernameInvalidError, ValueError) as exc:
        raise GroupNotFoundError(f"Group '@{clean_username}' was not found.") from exc
    except ChannelPrivateError as exc:
        raise UserbotNotMemberError(
            f"Userbot has no access to '@{clean_username}'."
        ) from exc

    if not isinstance(entity, Channel):
        raise GroupNotFoundError(f"'@{clean_username}' is not a group.")

    return entity


def _ensure_is_forum(channel: Channel) -> None:
    """Verify that a resolved channel has forum mode enabled.

    Args:
        channel: The resolved channel entity.

    Raises:
        NotAForumError: If the channel is not a forum.
    """
    if not getattr(channel, "forum", False):
        raise NotAForumError(f"'@{channel.username}' is not a forum.")


async def _fetch_raw_topics(
    client: TelegramClient,
    channel: Channel,
    limit: int = 100,
) -> list:
    """Fetch all raw forum topic objects from Telegram, handling pagination.

    Args:
        client: An active, connected Telethon client.
        channel: The forum's channel entity.
        limit: Number of topics to request per API call.

    Returns:
        A list of raw ForumTopic objects as returned by Telethon.

    Raises:
        UserbotNotMemberError: If the userbot cannot access the group.
    """
    all_topics = []
    offset_date = 0
    offset_id = 0
    offset_topic = 0

    while True:
        try:
            result = await client(
                GetForumTopicsRequest(
                    channel=channel,
                    offset_date=offset_date,
                    offset_id=offset_id,
                    offset_topic=offset_topic,
                    limit=limit,
                )
            )
        except FloodWaitError as exc:
            await asyncio.sleep(exc.seconds)
            continue
        except ChannelPrivateError as exc:
            raise UserbotNotMemberError(
                "Userbot has no access to this group's topics."
            ) from exc

        batch = result.topics
        if not batch:
            break

        all_topics.extend(batch)

        if len(batch) < limit:
            break

        last = batch[-1]
        offset_topic = last.id
        offset_id = last.top_message
        offset_date = last.date

    return all_topics


async def get_forum_topics(client: TelegramClient, username: str) -> list[Topic]:
    """Fetch, validate, and Uzbek-sort every topic in a forum group.

    Args:
        client: An active, connected Telethon client.
        username: The group's public username (with or without "@").

    Returns:
        A list of Topic objects sorted by Uzbek alphabetical order.

    Raises:
        GroupNotFoundError: If the username does not resolve to a group.
        NotAForumError: If the group is not a forum.
        UserbotNotMemberError: If the userbot lacks access to the group.
    """
    channel = await resolve_group(client, username)
    _ensure_is_forum(channel)

    raw_topics = await _fetch_raw_topics(client, channel)
    clean_username = username.lstrip("@").strip()

    topics = [
        Topic(
            topic_id=raw.id,
            title=raw.title,
            message_id=raw.top_message,
            link=_build_topic_link(clean_username, raw.id),
        )
        for raw in raw_topics
    ]

    return sort_by_uzbek_alphabet(topics, key=lambda topic: topic.title)
