import random

def generate_camo_svg(filename):
    width, height = 400, 400
    pixel_size = 20
    
    # EMR (Digital Flora) colors approx
    colors = [
        "#3a4a35", # dark olive
        "#5d6f46", # light olive
        "#4a3c2e", # brown
        "#1a1c18", # black/dark grey
        "#2f3b2b"  # base background
    ]
    
    rects = []
    
    # Base fill
    rects.append(f'<rect width="{width}" height="{height}" fill="{colors[4]}" />')
    
    # Random pixels
    for y in range(0, height, pixel_size):
        for x in range(0, width, pixel_size):
            if random.random() > 0.3: # 70% chance to draw a pixel on top
                color = random.choice(colors[:4])
                rects.append(f'<rect x="{x}" y="{y}" width="{pixel_size}" height="{pixel_size}" fill="{color}" />')

    svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">{"".join(rects)}</svg>'

    with open(filename, 'w') as f:
        f.write(svg_content)
    print(f"Generated {filename}")

if __name__ == "__main__":
    generate_camo_svg('camo.svg')
