import machine, neopixel
import time
import json
from pathlib import Path


COLORS = [
    (255, 0, 0),  # red
    (0, 255, 0),  # green
    (0, 0, 255),  # blue
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


def main():
    current = 0
    
    leds_per_face, num_faces, icosahedron_layers_map = get_shape(Path('shapes/icosahedron.json'))

    np = neopixel.NeoPixel(machine.Pin(18, machine.Pin.OUT), leds_per_face * num_faces)

    while True:
        for layer_face_ids in icosahedron_layers_map:
            for face_id in layer_face_ids:
                set_face_color(np, leds_per_face, face_id, COLORS[current])
            current = (current + 1) % len(COLORS)
            np.write()
        time.sleep(1)
        current = (current + 1) % len(COLORS)


if __name__ == '__main__':
    main()
