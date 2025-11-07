from aiohttp import web


async def health(request):
    return web.json_response(text='OK')


async def init_health() -> None:
    app = web.Application()
    app.router.add_get('/health', health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8081)
    await site.start()
