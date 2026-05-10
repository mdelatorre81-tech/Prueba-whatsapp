#!/usr/bin/env python3
"""Generate PWA icons as PNG using only stdlib (no pillow needed)."""
import struct, zlib, base64, os

def png_from_svg_data(size):
    """Create a simple green WhatsApp-style icon as PNG bytes."""
    # We'll create a minimal valid PNG manually
    # Green background with white chat bubble
    
    def make_png(size):
        width = height = size
        # RGBA pixels
        pixels = []
        cx, cy = size // 2, size // 2
        r = size // 2
        
        for y in range(height):
            row = []
            for x in range(width):
                dx, dy = x - cx, y - cy
                dist = (dx*dx + dy*dy) ** 0.5
                
                # Circle mask
                if dist > r - 1:
                    row += [0, 0, 0, 0]  # transparent
                elif dist > r - 2:
                    # anti-alias edge
                    alpha = int((r - dist) * 255)
                    row += [37, 211, 102, alpha]
                else:
                    # Green background
                    R, G, B, A = 37, 211, 102, 255
                    
                    # White chat bubble (simplified)
                    bx = x - cx
                    by = y - cy
                    
                    # Main bubble circle
                    br = int(r * 0.52)
                    bubble_dist = (bx*bx + by*by) ** 0.5
                    
                    # Inner white area
                    inner_r = int(r * 0.42)
                    
                    if bubble_dist < inner_r:
                        # Check for phone icon shape (simplified white phone)
                        # Phone body
                        pw = int(r * 0.22)
                        ph = int(r * 0.35)
                        px1, px2 = cx - pw, cx + pw
                        py1, py2 = cy - ph, cy + ph
                        
                        in_phone = (px1 <= x <= px2 and py1 <= y <= py2)
                        
                        if in_phone:
                            R, G, B = 255, 255, 255
                        else:
                            R, G, B = 37, 211, 102
                    
                    row += [R, G, B, A]
            pixels.append(bytes(row))
        
        # Build PNG
        def make_chunk(chunk_type, data):
            c = chunk_type + data
            return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
        
        signature = b'\x89PNG\r\n\x1a\n'
        
        # IHDR
        ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
        ihdr = make_chunk(b'IHDR', ihdr_data)
        
        # IDAT
        raw = b''.join(b'\x00' + row for row in pixels)
        compressed = zlib.compress(raw, 9)
        idat = make_chunk(b'IDAT', compressed)
        
        # IEND
        iend = make_chunk(b'IEND', b'')
        
        return signature + ihdr + idat + iend
    
    return make_png(size)


out_dir = os.path.dirname(os.path.abspath(__file__))

for size in [192, 512]:
    data = png_from_svg_data(size)
    path = os.path.join(out_dir, f'icon-{size}.png')
    with open(path, 'wb') as f:
        f.write(data)
    print(f'Created {path} ({len(data)} bytes)')

print('Icons generated!')
