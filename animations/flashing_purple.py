import asyncio
from animations.utils import set_face_color
from main import SharedState

async def animate(
        np: neopixel.NeoPixel,
        leds_per_face: int,
        num_faces: int,
        layers: tuple[tuple[int, ...], ...],
        stop_event: asyncio.Event,
        state: SharedState) -> None:
    
    while True:
        distance = await state.get()
        if distance == {}:
            distance = 0
        else:
            distance = distance['distance']
        clamped_distance = max(0, min(distance, 1000))
        scaled_distance = int(clamped_distance * 255 / 1000)
        np.fill((0, 255 - scaled_distance, scaled_distance))
        np.write()
        await asyncio.sleep(0.01)
    
   