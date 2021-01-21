
from homie.constants import FLOAT
from homie.property import HomieProperty
from update_homie_node import UpdateHomieNode
# from homie.device import await_ready_state

# import uasyncio as asyncio
# from time import ticks_ms, ticks_add, ticks_diff


class BMP280Node(UpdateHomieNode):

    def __init__(
            self,
            id,
            name,
            bmp280,
            interval=60*5):
        super().__init__(id=id, name=name, type="sensor", interval=interval)

        # BMP280
        self.bmp280 = bmp280
        self.property_temerature = HomieProperty(
            id="temperature",
            name="Temperatur",
            datatype=FLOAT,
            unit="°C",
        )
        self.add_property(self.property_temerature)
        self.property_pressure = HomieProperty(
            id="pressure",
            name="Druck",
            datatype=FLOAT,
            unit="Pa",
        )
        self.add_property(self.property_pressure)

    def update_data(self):
        self.property_pressure.value = "{:1.0f}".format(
            self.bmp280.pressure * 100)  # hPa = 100 Pa
        self.property_temerature.value = "{:1.2f}".format(
            self.bmp280.temperature)
