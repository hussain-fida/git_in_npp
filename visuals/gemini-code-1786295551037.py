import os
from PIL import Image, ImageDraw, ImageFont

def create_git_add_gif(output_path="add_animated.gif"):
    frames = []
    width, height = 400, 250
    
    # Generate 15 animation frames showing a file moving to Staging
    for i in range(15):
        img = Image.new("RGB", (width, height), "#1e1e2e")
        draw = ImageDraw.Draw(img)
        
        # Draw Working Directory Box
        draw.rectangle([20, 50, 180, 200], outline="#f38ba8", width=2)
        draw.text((30, 25), "Working Directory", fill="#f38ba8")
        
        # Draw Staging Area Box
        draw.rectangle([220, 50, 380, 200], outline="#a6e3a1", width=2)
        draw.text((250, 25), "Staging Area", fill="#a6e3a1")
        
        # Animate file movement from left to right
        x_pos = 40 + (i * 12)
        draw.rectangle([x_pos, 90, x_pos + 80, 150], fill="#fab387", outline="#ffffff")
        draw.text((x_pos + 10, 110), "file.txt", fill="#11111b")
        
        frames.append(img)
        
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0
    )

def create_git_commit_gif(output_path="commit_animated.gif"):
    frames = []
    width, height = 400, 250
    
    # Generate animation showing Staging Area creating a new Commit Node
    for i in range(15):
        img = Image.new("RGB", (width, height), "#1e1e2e")
        draw = ImageDraw.Draw(img)
        
        # Draw Staging Area Box
        draw.rectangle([20, 50, 160, 200], outline="#a6e3a1", width=2)
        draw.text((35, 25), "Staging Area", fill="#a6e3a1")
        
        # Draw Local Repo Tree Box
        draw.rectangle([200, 50, 380, 200], outline="#89b4fa", width=2)
        draw.text((240, 25), "Local Commit Tree", fill="#89b4fa")
        
        # Draw existing commit node C1
        draw.ellipse([230, 105, 270, 145], fill="#89b4fa")
        draw.text((242, 120), "C1", fill="#11111b")
        
        # Animate new commit C2 popping up
        if i > 5:
            radius = min((i - 5) * 4, 20)
            draw.line([(270, 125), (310, 125)], fill="#ffffff", width=2)
            draw.ellipse([310 - radius, 125 - radius, 310 + radius, 125 + radius], fill="#a6e3a1")
            if radius == 20:
                draw.text((302, 120), "C2", fill="#11111b")
        
        frames.append(img)
        
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0
    )

if __name__ == "__main__":
    create_git_add_gif()
    create_git_commit_gif()
    print("Generated distinct animated GIFs: add_animated.gif, commit_animated.gif")