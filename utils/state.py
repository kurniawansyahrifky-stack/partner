import asyncio

task_queue = asyncio.Queue()

manual_setup = {}
stop_flag = {}
manual_messages = {}

auto_data = {}
custom_buttons = {}

recent_messages = set()
rate_limit = {}
last_activity = {}
