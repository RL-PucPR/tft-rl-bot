import asyncio


def wait(call, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(call(*args, **kwargs))


def get_board_position(position):
    return [int(position / 7), position % 7]
