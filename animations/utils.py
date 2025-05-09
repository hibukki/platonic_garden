def set_face_color(np, leds_per_face, face_index, color):
    face_offset = leds_per_face * face_index
    for i in range(leds_per_face):
        np[face_offset + i] = color
