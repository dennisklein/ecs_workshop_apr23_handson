"""
Demo EPICS client - ImTUI - MQTT publisher
"""


from amqtt.client import MQTTClient
import asyncio
from asyncio.exceptions import CancelledError
from caproto.asyncio.client import Context
import curses
from datetime import datetime
import json


async def run_epics_readout(data, mqtt_send_queue):
    """Monitor the PV 'randomwalk:x' and record timeseries in memory"""
    async with Context() as ctx:
        x = (await ctx.get_pvs('random_walk:x'))[0]
        async with x.subscribe(data_type='time') as sub:
            async for value in sub:
                data.append((value.metadata.timestamp, value.data[0]))
                mqtt_send_queue.put_nowait((value.metadata.timestamp, value.data[0]))



async def run_imtui(data, fps=30):
    """Immediate Mode Text User Interface with given frames per second refresh rate"""
    # TODO: Refactor init/cleanup code into an asynchronous context manager
    try:
        # initialize TUI
        screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        screen.keypad(True)
        title = 'ECS Workshop Apr23'
        title_min_width = len(title) + 4
        curses.curs_set(0)

        while True:
            screen.clear()
            y, x = screen.getmaxyx()
            if y > 5 and x > len(title):
                screen.addstr(1, 2, title)
            value = None
            text = f'waiting for data'
            if data:
                value = data[-1]
                timestamp = datetime.fromtimestamp(value[0]).strftime("%m/%d/%Y, %H:%M:%S.%f")
                text = f'{timestamp}: {value[1]: >.3f}'
            screen.addstr(int(y/2), max(int((x-len(text))/2),0), text)

            screen.refresh()
            await asyncio.sleep(1./fps)
    finally:
        # restore terminal
        curses.nocbreak()
        screen.keypad(False)
        curses.echo()
        curses.endwin()


async def run_mqtt_sender(send_queue, topic, min_wait=5):
    """Publish data via MQTT, but not more often than 'min_wait' seconds"""
    # TODO: Implement an asynchronous context manager for the client
    client = MQTTClient()
    try:
        await client.connect('mqtt://127.0.0.1:1883/')

        while True:
            msg = []  # Batch all pending data points into one MQTT msg
            msg.append(await send_queue.get())
            while not send_queue.empty():
                msg.append(send_queue.get_nowait())

            await client.publish(topic, json.dumps(msg).encode())

            await asyncio.sleep(min_wait)
    finally:
        await client.disconnect()


async def main():
    """Main program"""
    data = []  # TODO: Fix unbound growth
    mqtt_send_queue = asyncio.Queue()

    epics = asyncio.create_task(run_epics_readout(data, mqtt_send_queue))
    imtui = asyncio.create_task(run_imtui(data))
    mqtt = asyncio.create_task(run_mqtt_sender(mqtt_send_queue, '/ecsws/random_walk:x'))

    try:
        # TODO: Rewrite using https://docs.python.org/3/library/asyncio-task.html#asyncio.wait
        await epics
        await imtui
        await mqtt
    except CancelledError:
        pass


if __name__ == '__main__':
    asyncio.run(main())
