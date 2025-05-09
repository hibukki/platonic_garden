import asyncio
import time
from animations.utils import set_face_color


async def animate(
        np: neopixel.NeoPixel,
        leds_per_face: int,
        num_faces: int,
        layers: tuple[tuple[int, ...], ...],
        stop_event: asyncio.Event) -> None:
    
    num_steps = 100
    layer_ratio = num_steps / len(layers)
    reverse_start_step = num_steps - 1
    minimum_intensity = 50
    frame_time_ms = 1000/30
    while True:
        for i in range(num_steps):
            if stop_event.is_set():
                return
            frame_start = time.time_ns()
            for j in range(len(layers)):
                layer_location = j * layer_ratio
                distance = int(abs(i - layer_location))
                intensity = max(minimum_intensity, 255 - distance*30)
                layer_color = (intensity, 0, intensity)
                for face in layers[j]:
                    set_face_color(np, leds_per_face, face, layer_color)
            np.write()
            await asyncio.sleep_ms(int(frame_time_ms - (time.time_ns() - frame_start)/1000000))
        for i in range(reverse_start_step, -1, -1):
            if stop_event.is_set():
                return
            frame_start = time.time_ns()
            for j in range(len(layers)):
                layer_location = j * layer_ratio
                distance = int(abs(i - layer_location))
                intensity = max(minimum_intensity, 255 - distance*30)
                layer_color = (intensity, 0, intensity)
                for face in layers[j]:
                    set_face_color(np, leds_per_face, face, layer_color)
            np.write()
            await asyncio.sleep_ms(int(frame_time_ms - (time.time_ns() - frame_start)/1000000))

