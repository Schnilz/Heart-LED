import uasyncio as asyncio
from time import ticks_ms, ticks_add, ticks_diff

from homie.constants import BOOLEAN, TRUE, FALSE, FLOAT, ENUM, COLOR, RGB
from homie.property import HomieProperty
from homie.node import HomieNode
from machine import Pin
from primitives.pushbutton import Pushbutton

import gc
from led_anim import ANIMS


class LEDControlNode(HomieNode):

    button_names = ("up", "down")

    def __init__(self, id, name, pin_up, pin_down, leds):
        super().__init__(id=id, name=name, type="colorlight")
        pin_up.init(mode=Pin.IN, pull=Pin.PULL_UP)
        pin_down.init(mode=Pin.IN, pull=Pin.PULL_UP)
        button_up = Pushbutton(pin_up, suppress=True, sense=1)
        button_down = Pushbutton(pin_down, suppress=True, sense=1)
        self.buttons = (button_up, button_down)
        self.on_buttons_pressed = [None, None]
        self.on_buttons_released = [None, None]
        self.leds = leds

        self.properties_button_pressed = [None, None]
        for i, button_name in enumerate(self.button_names):
            self.properties_button_pressed[i] = HomieProperty(
                id="button_{0}_pressed".format(button_name),
                name="Knöpgen \"{0}\" gedrückt".format(button_name),
                settable=True,
                default=FALSE,
                on_message=self._on_button_pressed_msg,
                datatype=BOOLEAN,
            )
            self.add_property(self.properties_button_pressed[i])
            self.buttons[i].press_func(self._on_buttons_pressed, args=(i,))
            self.buttons[i].release_func(self._on_buttons_released, args=(i,))

        self._power = False
        self.property_power = HomieProperty(
            id="power",
            name="Power",
            settable=True,
            datatype=BOOLEAN,
            default=FALSE,
            on_message=self.on_power_msg,
        )
        self.add_property(self.property_power)

        self.brightness = 0.7
        self.property_brightness = HomieProperty(
            id="brightness",
            name="Helligkeit",
            settable=True,
            datatype=FLOAT,
            default=70,
            format="0:100",
            unit="%",
            on_message=self.on_brightness_msg,
        )
        self.add_property(self.property_brightness)

        self.anims = dict([(a.name, (a, i+1)) for i, a in enumerate(ANIMS)])
        self._animation_num = 0
        self._animation = None
        self.property_animation = HomieProperty(
            id="animation",
            name="Animation",
            settable=True,
            datatype=ENUM,
            format=",".join(["-"]+list(self.anims.keys())),
            default="-",
            on_message=self.on_change_anim_msg,
        )
        self.add_property(self.property_animation)

        self.color = (0, 0, 0)
        self.property_color = HomieProperty(
            id="color",
            name="Solide Farbe",
            settable=True,
            datatype=COLOR,
            format=RGB,
            default="0,0,0",
            on_message=self.on_change_color_msg,
        )
        self.add_property(self.property_color)

        self.change = False
        asyncio.create_task(self._update_data_async())

    def on_power_msg(self, topic, payload, retained):
        self.set_power(payload == TRUE)
        self.change = True

    def on_brightness_msg(self, topic, payload, retained):
        self.brightness = (float(payload)/100.0*251.0 + 4)/255
        self.change = True

    def on_change_anim_msg(self, topic, payload, retained):
        self.set_animation(payload)

    def _on_button_pressed_msg(self, topic,  payload, retained):
        button_topic_name = topic.split("/")[-1].split("_")[1]
        i = -1
        for b, n in enumerate(self.button_names):
            if n in button_topic_name:
                i = b
                break
        if {FALSE: False, TRUE: True}[payload] and \
                not self.buttons[i].rawstate():
            self._on_buttons_pressed(i)
            self._on_buttons_released(i)

    def _on_buttons_pressed(self, i):
        self.properties_button_pressed[i].value = TRUE

    def _on_buttons_released(self, i):
        self.properties_button_pressed[i].value = FALSE
        self.set_animation_num((1 if i == 0 else -1) + self._animation_num)

    async def _update_data_async(self):
        while True:
            if self._power:
                if self._animation:
                    wait_next = self._animation.render(
                        leds=self.leds, t=ticks_ms(),
                        brightness=self.brightness)
                if self.color != (0, 0, 0):
                    self.leds.fill(
                        tuple([int(self.brightness * float(i))
                               for i in self.color]))
                    self.leds.write()
                    wait_next = 10000
            else:
                wait_next = 10000
            now = ticks_ms()
            wait_till = ticks_add(now, wait_next)
            while ticks_diff(wait_till, now) > 0 and not self.change:
                await asyncio.sleep_ms(
                    min(100, ticks_diff(wait_till, now)))
                now = ticks_ms()
            self.change = False

    def set_power(self, p):
        self._power = p
        self.property_power.value = TRUE if p else FALSE
        if not p:
            self.leds.fill((0, 0, 0))
            self.leds.write()

    def set_animation_num(self, p):
        p = p % len(ANIMS)
        if p == 0:
            self.set_animation("")
        else:
            for a in self.anims.values():
                if a[1] == p:
                    self.set_animation(a[0])
                    break

    def on_change_color_msg(self, topic, payload, retained):
        self.set_animation(tuple([int(i) for i in payload.split(",")]))

    def set_animation(self, p):
        if p in ANIMS:
            self._animation = p
            for a in self.anims.values():
                if a[0] == self._animation:
                    self._animation = a[0](self.leds)
                    self._animation_num = a[1]
                    self.set_power(True)
                    break
        if type(p) == str:
            if p == "-" or p == "":
                self.set_power(False)
                self._animation_num = 0
                self._animation = None
            else:
                self.set_power(True)
                a = self.anims[p]
                self._animation = a[0](self.leds)
                self._animation_num = a[1]
        if type(p) == tuple:
            if max(p) == 0:
                self.set_power(False)
            else:
                self.set_power(True)
            self._animation_num = 0
            self._animation = None
            self.color = p
        if self._animation:
            self.color = (0, 0, 0)
        self.property_color.value = str(self.color)[1:-1]
        self.change = True
        self.property_animation.value = self._animation.name if self._animation else "-"
        gc.collect()
