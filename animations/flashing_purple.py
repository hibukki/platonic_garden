import asyncio
from animations.utils import set_face_color


async def animate(
        np: neopixel.NeoPixel,
        leds_per_face: int,
        num_faces: int,
        layers: tuple[tuple[int, ...], ...],
        stop_event: asyncio.Event) -> None:
    
    layer_ratio = 100 / len(layers)
    thickness = 20
    while True:
        for i in range(100):
            for j in range(len(layers)):
                layer_location = j * layer_ratio
                if layer_location >= i and layer_location < i + thickness:
                    layer_color = (255, 0, 255)
                else:
                    layer_color = (0, 0, 0)
            np.write()
            await asyncio.sleep(0.5)

