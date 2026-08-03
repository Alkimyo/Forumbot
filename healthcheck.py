"""HTTP health-check server module.

The bot itself communicates with Telegram via outbound long polling and
MTProto connections — it never needs to listen on a port. However,
hosting platforms like Render's "Web Service" tier require a process to
bind to a port and respond to HTTP requests, or they consider the
deployment unhealthy.

This module runs a minimal aiohttp server whose only job is to answer
health checks, so the bot can be deployed as a Web Service without
switching to a Background Worker plan.
"""

from __future__ import annotations

import logging
import os

from aiohttp import web

logger = logging.getLogger(__name__)


async def _handle_health(request: web.Request) -> web.Response:
    """Respond to any health-check request with a simple 200 OK.

    Args:
        request: The incoming HTTP request (unused, but required by
            aiohttp's handler signature).

    Returns:
        A plain-text 200 OK response.
    """
    return web.Response(text="OK")


async def start_health_check_server() -> None:
    """Start a background HTTP server bound to the platform-provided port.

    Reads the port from the PORT environment variable (set automatically
    by Render and similar platforms), defaulting to 8000 for local runs.
    The server runs forever alongside the bot's polling loop.
    """
    port = int(os.getenv("PORT", "8000"))

    app = web.Application()
    app.router.add_get("/", _handle_health)
    app.router.add_get("/health", _handle_health)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()

    logger.info("Health-check server %s portda ishga tushdi.", port)
