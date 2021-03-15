""" Testing related utils for async logic """

async def wait_for_condition(condition):
    """ Adcquires lock, waits for a condition to be met, and releases lock """
    async with condition:
        await condition.wait()

async def notify_condition(condition):
    """ Adcquires lock, notifies 1 condition watcher, and releases lock """
    async with condition:
        condition.notify()
