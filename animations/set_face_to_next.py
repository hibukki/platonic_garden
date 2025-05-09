import asyncio
import time
from animations.utils import set_face_color


async def animate(
        np: neopixel.NeoPixel,
        leds_per_face: int,
        num_faces: int,
        layers: tuple[tuple[int, ...], ...],
        stop_event: asyncio.Event) -> None:
    while True:
        a = time.time_ns()
        np.fill((0, 0, 0))
        print((time.time_ns() -a)/1000000)
        np.write()
        await asyncio.sleep(1)
        a = time.time_ns()
        np.fill((255, 255, 255))
        print((time.time_ns() -a)/1000000)
        np.write()
        await asyncio.sleep(1)