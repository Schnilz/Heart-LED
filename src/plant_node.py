from homie.constants import BOOLEAN, FALSE, TRUE, FLOAT
from homie.property import HomieProperty
from update_homie_node import UpdateHomieNode
# from homie.device import await_ready_state
from machine import Pin, ADC
import uasyncio as asyncio
import gc


class PlantNode(UpdateHomieNode):

    def __init__(
            self,
            id,
            name,
            watering_motor,
            moisture_sensor,
            pin_water_tank,
            waterlevel_sensor,
            interval=60*5,
            interval_watering=0.2):
        super().__init__(
            id=id, name=name, type="watering",
            interval=interval,
            interval_short=interval_watering)

        # Update Interval
        self.interval_normal = interval
        self.interval_watering = interval_watering

        # WaterLevelSensor
        self.waterlevel_sensor = waterlevel_sensor
        self.property_waterlevel = HomieProperty(
            id="waterlevel",
            name="Wassertankstand",
            datatype=FLOAT,
            unit="L",
        )
        self.add_property(self.property_waterlevel)
        self.property_waterlevel_percent = HomieProperty(
            id="waterlevel_percent",
            name="Wassertankstand [%]",
            datatype=FLOAT,
            format="0.00:100.00",
            unit="%",
        )
        self.add_property(self.property_waterlevel_percent)

        self.property_waterlevel_volume_liter = HomieProperty(
            id="waterlevel_volume_max",
            name="Wassertankgröße",
            settable=True,
            datatype=FLOAT,
            unit="L",
            on_message=self._set_waterlevel_volume
        )
        self.add_property(self.property_waterlevel_volume_liter)

        # Moisture
        self.moisture_sensor = moisture_sensor
        self.property_moisture = HomieProperty(
            id="moisture",
            name="Feuchte",
            datatype=FLOAT,
            format="0.00:100.00",
            unit="%",
        )
        self.add_property(self.property_moisture)

        # Watering Motor
        self.watering_motor = watering_motor
        self.watering_motor.add_motor_stop_callback(
            self.on_watering_motor_stop)
        self.watering_motor.add_motor_start_callback(
            self.on_watering_motor_start)
        self.property_watering_power = HomieProperty(
            id="power",
            name="Bewässerung",
            settable=True,
            datatype=BOOLEAN,
            default=FALSE,
            on_message=self.toggle_motor,
        )
        self.add_property(self.property_watering_power)

        self.property_watering_max_duration = HomieProperty(
            id="watering_duration",
            name="Bewässerungszeit",
            settable=True,
            datatype=FLOAT,
            default=3,
            on_message=lambda t, p, r:
                self.watering_motor.set_watering_duration(float(p)),
            unit="s",
        )
        self.add_property(self.property_watering_max_duration)

    def update_data(self):
        self.property_moisture.value = "{:1.2f}".format(
            self.moisture_sensor.value * 100)

        self.property_waterlevel_percent.value = "{:1.0f}".format(
            self.waterlevel_sensor.level_percent)
        self.property_waterlevel.value = "{:1.2f}".format(
            self.waterlevel_sensor.level)
        self.property_waterlevel_volume_liter.value = "{:1.4f}".format(
            self.waterlevel_sensor.volume)

        self.property_watering_max_duration.value = \
            str(self.watering_motor.watering_duration)

        self.property_watering_power.value = \
            TRUE if self.watering_motor.is_watering() else FALSE

        if self.watering_motor.is_watering():
            if self._interval != self.interval_watering:
                self.interval_normal = self._interval
                self.set_interval(self.interval_watering)
        else:
            self.set_interval(self.interval_normal)
        gc.collect()

    def toggle_motor(self, topic, payload, retained):
        ONOFF = {FALSE: False, TRUE: True}
        v = ONOFF[payload]
        if v:
            self.watering_motor.start()
        else:
            self.watering_motor.stop()

    def on_watering_motor_stop(self):
        self.set_interval(self.interval_normal)
        self.property_watering_power.value = FALSE

    def on_watering_motor_start(self):
        if self._interval != self.interval_watering:
            self.interval_normal = self._interval
            self.set_interval(self.interval_watering)

    def _set_waterlevel_min_value(self, topic, payload, retained):
        self.waterlevel_sensor.value_min = float(payload)

    def _set_waterlevel_max_value(self, topic, payload, retained):
        self.waterlevel_sensor.value_max = float(payload)

    def _set_waterlevel_volume(self, topic, payload, retained):
        self.waterlevel_sensor.volume = float(payload)
