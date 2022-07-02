def rgb_to_hex(r, g, b):
    return '#%02x%02x%02x' % (r, g, b)

def parse(line, color):
    index = line.rfind(color)
    substring = line[index+3:]
    end = substring.find('"')
    value = int(float(substring[:end])*255)
    return value


with open('glm_colormap.txt', 'r') as f: data = f.readlines()
arr = []
for count, line in enumerate(data):
    red = parse(line, 'r')
    green = parse(line, 'g')
    blue = parse(line, 'b')
    rgb = rgb_to_hex(red, green, blue)
    arr.append(rgb)

print(arr)