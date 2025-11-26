from PIL import Image, ImageDraw
import math

def create_icon():
    # Dimensions
    size = 512
    center = size // 2
    
    # Colors
    bg_color = (10, 25, 47) # Dark Blue
    primary_color = (0, 255, 255) # Cyan
    secondary_color = (64, 224, 208) # Turquoise
    accent_color = (100, 149, 237) # Cornflower Blue
    
    # Create image
    img = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw central hub (Hexagon)
    radius = 80
    points = []
    for i in range(6):
        angle_deg = 60 * i
        angle_rad = math.radians(angle_deg)
        x = center + radius * math.cos(angle_rad)
        y = center + radius * math.sin(angle_rad)
        points.append((x, y))
    
    draw.polygon(points, outline=primary_color, width=8)
    
    # Draw inner circle
    draw.ellipse((center-30, center-30, center+30, center+30), fill=primary_color)
    
    # Draw nodes and connections
    node_radius = 120
    outer_points = []
    for i in range(6):
        angle_deg = 60 * i + 30 # Offset
        angle_rad = math.radians(angle_deg)
        x = center + 180 * math.cos(angle_rad)
        y = center + 180 * math.sin(angle_rad)
        outer_points.append((x, y))
        
        # Draw connection to center
        # Find closest hexagon point
        # Simple line to center for now
        draw.line((center, center, x, y), fill=accent_color, width=4)
        
        # Draw node
        r = 15
        draw.ellipse((x-r, y-r, x+r, y+r), fill=secondary_color)

    # Draw "F2X" text (Simulated with lines if no font)
    # Actually, let's just keep it abstract geometric for now to avoid font issues
    
    # Save
    output_path = "f2x_neurohub_icon.png"
    img.save(output_path)
    print(f"Icon saved to {output_path}")

if __name__ == "__main__":
    create_icon()
