from homie.device import HomieDevice
from machine import Pin, I2C
import settings

# import uasyncio as asyncio
# from time import ticks_ms, ticks_add, ticks_diff

import bme280
from bmp280_node import BMP280Node
import neopixel
from led_control_node import LEDControlNode


def main():
    i2c = I2C(scl=Pin(16), sda=Pin(17))

    bmp280 = bme280.BME280(i2c=i2c)

    bmp280Node = BMP280Node(
        id="bmp280",
        name="Enviroment-Sensor",
        bmp280=bmp280)

    leds = neopixel.NeoPixel(Pin(23, Pin.OUT), 28)

    controlNode = LEDControlNode(
        id="leds1", name="LEDs",
        pin_up=Pin(18), pin_down=Pin(5), leds=leds)

    # Homie device setup
    homie = HomieDevice(settings)
    homie.add_node(bmp280Node)
    homie.add_node(controlNode)

    # run forever
    homie.run_forever()


if __name__ == "__main__":
    main()
