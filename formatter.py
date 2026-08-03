"""Message formatting module.

Builds paginated, HTML-formatted text messages listing forum topics as
clickable links, respecting Telegram's message length limits and the
configured topics-per-page limit.
"""

from __future__ import annotations

from html import escape

from forum import Topic

TELEGRAM_MAX_MESSAGE_LENGTH = 4096


def _format_topic_line(index: int, topic: Topic) -> str:
    """Format a single numbered, clickable topic line.

    Args:
        index: The 1-based display number of the topic.
        topic: The topic to render.

    Returns:
        An HTML-formatted line, e.g. '1. <a href="...">Title</a>'.
    """
    safe_title = escape(topic.title)
    return f'{index}. <a href="{topic.link}">{safe_title}</a>'


def build_topic_pages(
    group_username: str,
    topics: list[Topic],
    topics_per_page: int = 100,
) -> list[str]:
    """Split topics into HTML-formatted pages ready to send as messages.

    Args:
        group_username: The group's public username, without "@".
        topics: The full, already-sorted list of topics.
        topics_per_page: Maximum number of topics per message.

    Returns:
        A list of complete message strings, one per page, each safe to
        send directly with HTML parse mode.
    """
    if not topics:
        return []

    total = len(topics)
    chunks = [
        topics[i:i + topics_per_page]
        for i in range(0, total, topics_per_page)
    ]
    total_pages = len(chunks)

    pages: list[str] = []
    for page_number, chunk in enumerate(chunks, start=1):
        header_lines = [f"📚 Guruh: @{escape(group_username)}", ""]
        if page_number == 1:
            header_lines.append(f"📊 Jami mavzular: {total}")
            header_lines.append("")
        header_lines.append(f"📄 Sahifa {page_number}/{total_pages}")
        header_lines.append("")

        start_index = (page_number - 1) * topics_per_page
        body_lines = [
            _format_topic_line(start_index + offset, topic)
            for offset, topic in enumerate(chunk, start=1)
        ]

        footer_lines = []
        if page_number < total_pages:
            footer_lines = ["", "Davomi keyingi xabarda..."]

        message = "\n".join(header_lines + body_lines + footer_lines)
        pages.append(message)

    return pages
