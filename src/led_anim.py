from math import sin, pi


def hsv2rgb(h, s, v):
    if s == 0.0:
        v *= 255
        return (v, v, v)
    i = int(h*6.)  # XXX assume int() truncates!
    f = (h*6.)-i
    p, q, t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))
                                       ), int(255*(v*(1.-s*(1.-f))))
    v *= 255
    i %= 6
    v, t, p, q = int(v), int(t), int(p), int(q)
    if i == 0:
        return (v, t, p)
    if i == 1:
        return (q, v, p)
    if i == 2:
        return (p, v, t)
    if i == 3:
        return (p, q, v)
    if i == 4:
        return (t, p, v)
    if i == 5:
        return (v, p, q)


class AnimHeartbeat:
    name = "Heartbeat"

    def __init__(self, leds):
        pass

    def render(self, leds, t, brightness=1):
        t = t / 550.0
        brightness *= 1.0 + 4.0 * sin(t + 1.5) * sin(t)**43.0
        leds.fill((int(brightness * 255), 0, 0))
        leds.write()
        return 16


class AnimRegenbogen:
    name = "Regenbogen"

    def __init__(self, leds):
        pass

    def render(self, leds, t, brightness=1):
        t = t / 2400.0
        for i in range(leds.n):
            leds[i] = hsv2rgb(i / leds.n + t, 1, brightness)
        leds.write()
        return 16


class AnimGanzeFarben:
    name = "Ganze Farben"

    def __init__(self, leds):
        pass

    def render(self, leds, t, brightness=1):
        t = t / 40000.0
        leds.fill(hsv2rgb(t, 1, brightness))
        leds.write()
        return 16


class AnimFarbverlauf:
    name = "Farbverlauf"

    def __init__(self, leds):
        pass

    def render(self, leds, t, brightness=1):
        t = t / 1000.0
        for i in range(leds.n):
            leds[i] = hsv2rgb(t/60 + 0.3921 *
                              sin(i / leds.n * pi + t), 1, brightness)
        leds.write()
        return 16


class AnimHalbeHalbe:
    name = "Halbe-Halbe"

    def __init__(self, leds):
        pass

    def render(self, leds, t, brightness=1):
        for i in range(leds.n):
            offset = 0 if sin(float(i)/leds.n*pi*2-t/55234.0) > 0.0 else 0.5
            leds[i] = hsv2rgb((t/60000.0 + offset) % 1, 1, brightness)
        leds.write()
        return 16


class AnimKnightRider:
    name = "Knight Rider"

    def __init__(self, leds):
        pass

    def render(self, leds, t, brightness=1):
        t = t / 400.0
        leds.fill((10, 10, 10))
        leds[int(leds.n / 2 + sin(t) * leds.n / 3)] = (255, 0, 0)
        leds.write()
        return 90


class AnimStrobo:
    name = "Stroboskop"

    def __init__(self, leds):
        self.on = True
        pass

    def render(self, leds, t, brightness=1):
        leds.fill((255, 255, 255) if self.on else (0, 0, 0))
        self.on = not self.on
        leds.write()
        return 10 if self.on else 40


class AnimLeselicht:
    name = "Leselicht"

    def __init__(self, leds):
        self.on = True
        pass

    def render(self, leds, t, brightness=1):
        b = int(brightness * 255)
        leds.fill((b, b, b))
        leds.write()
        return 1000


ANIMS = [AnimHeartbeat,
         AnimRegenbogen,
         AnimGanzeFarben,
         AnimFarbverlauf,
         AnimHalbeHalbe,
         AnimKnightRider,
         AnimStrobo,
         AnimLeselicht]
