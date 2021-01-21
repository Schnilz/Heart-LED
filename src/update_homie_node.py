
from homie.constants import FLOAT
from homie.property import HomieProperty
from homie.node import HomieNode
from homie.device import await_ready_state

import uasyncio as asyncio
from time import ticks_ms, ticks_add, ticks_diff


class UpdateHomieNode(HomieNode):

    def __init__(
            self,
            id,
            name,
            type,
            interval=60*5,
            interval_short=0.1):
        super().__init__(id=id, name=name, type=type)

        self.interval_changed = False
        self.interval_short = interval_short
        # Update Interval
        self._interval = interval
        self.property_interval = HomieProperty(
            id="update_interval",
            name="Aktualisierungsrate",
            datatype=FLOAT,  # TODO ISO8601
            settable=True,
            on_message=self._set_interval,
            unit="s",
        )
        self.add_property(self.property_interval)

        asyncio.create_task(self._update_data_async())

    @await_ready_state
    async def _update_data_async(self):
        while True:

            # call child callback
            self.update_data()

            # TODO ISO8601
            # self.property_interval.value = "PT{:1.3f}S".format(self.interval)
            self.property_interval.value = "{:1.3f}".format(self.interval)

            # We don't simply wait the update interval, as it can change while waiting.
            last_update = ticks_ms()
            wait_till = ticks_add(last_update, int(self.interval * 1000.0))
            while ticks_diff(ticks_ms(), wait_till) < 0:
                if self.interval_changed:
                    self.interval_changed = False
                    wait_till = ticks_add(
                        last_update,
                        int(self.interval * 1000))
                sleep_for = min(int(self.interval_short * 1000.0),
                                ticks_diff(wait_till, ticks_ms()))
                await asyncio.sleep_ms(sleep_for)

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def setter_interval(self, i):
        self.set_interval(i)

    def set_interval(self, i):
        if i != self._interval:
            self.interval_changed = True
            self._interval = float(i)

    def _set_interval(self, topic, payload, retained):
        self.set_interval(float(payload))
