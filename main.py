import machine, neopixel
import time
import json
import asyncio
from typing import TypeVar, Generic, Callable, Optional, Dict, Any, TYPE_CHECKING
from copy import deepcopy
import sys

if TYPE_CHECKING:
    from types import ModuleType

from pathlib import Path


ANIMATIONS = [
    'flashing_purple',
    'rainbow'
]

def get_layers(shape_faces: list[dict]) -> tuple[tuple[int, ...], ...]:
    if not shape_faces:
        return tuple()
    max_layer = max(face['layer'] for face in shape_faces)
    layers = [[] for _ in range(max_layer + 1)]
    for face in shape_faces:
        layers[face['layer']].append((face['face_id'], face['index']))
    
    processed_layers = []
    for layer_list in layers:
        layer_list.sort(key=lambda x: x[1])
        processed_layers.append(tuple(item[0] for item in layer_list))
    return tuple(processed_layers)


def get_shape(file_path: Path) -> tuple[int, int, tuple[tuple[int, ...], ...]]:
    data = json.loads(file_path.read_text())
    
    leds_per_entity = data.get('led_per_side') or data.get('led_per_face')
    faces_data = data.get('faces')
    
    if leds_per_entity is None or faces_data is None:
        raise ValueError(f"Invalid shape data in {file_path}")

    num_faces = len(faces_data)
    layers_map = get_layers(faces_data)
    return leds_per_entity, num_faces, layers_map


def set_face_color(np, leds_per_face, face_index, color):
    face_offset = leds_per_face * face_index
    for i in range(leds_per_face):
        np[face_offset + i] = color


def get_animations() -> list['ModuleType']:
    return [getattr(__import__(f'animations.{name}'), name) for name in ANIMATIONS]


async def run_animations(np: neopixel.NeoPixel, leds_per_face: int, num_faces: int, layers: tuple[tuple[int, ...], ...]) -> None:
    while True:
        try:
            animations = get_animations()
            for animation in animations:
                stop_event = asyncio.Event()
                task = asyncio.create_task(animation.animate(np, leds_per_face, num_faces, layers, stop_event))
                await asyncio.sleep(10)
                stop_event.set()
                await asyncio.gather(task)
        except Exception as e:
            sys.print_exception(e)
            error_animation(np)


def error_animation(np: neopixel.NeoPixel) -> None:
    try:
        for i in range(3):
            np.fill((255, 0, 0))
            np.write()
            time.sleep(0.5)
            np.fill((0, 0, 0))
            np.write()
            time.sleep(0.5)
    except Exception as e:
        sys.print_exception(e)


def init_animation(np: neopixel.NeoPixel) -> None:
    for i in range(3):
        print(time.time_ns())
        color = [0, 0, 0]
        color[i] = 255
        np.fill(tuple(color))
        np.write()
        time.sleep(1)


class SharedState:
    def __init__(self, initial: Optional[Dict[Any, Any]] = None):
        self._data: Optional[Dict[Any, Any]] = deepcopy(initial) if initial is not None else None
        self._lock = asyncio.Lock()

    async def get(self) -> Optional[Dict[Any, Any]]:
        async with self._lock:
            return deepcopy(self._data)

    async def set(self, value: Dict[Any, Any]) -> None:
        async with self._lock:
            self._data = deepcopy(value)

    async def update(self, fn: Callable[[Optional[Dict[Any, Any]]], Dict[Any, Any]]) -> None:
        async with self._lock:
            # The function fn is expected to return a new dict or modify a copy.
            # If fn modifies its input, deepcopy self._data before passing it to fn.
            current_data_copy = deepcopy(self._data)
            self._data = fn(current_data_copy)


def main():
    current = 0
    
    leds_per_face, num_faces, layers = get_shape(Path('shapes/icosahedron.json'))

    np = neopixel.NeoPixel(machine.Pin(18, machine.Pin.OUT), leds_per_face * num_faces)

    init_animation(np)

    tasks = []
    tasks.append(run_animations(np, leds_per_face, num_faces, layers))

    asyncio.run(asyncio.gather(*tasks))

if __name__ == '__main__':
    main()
