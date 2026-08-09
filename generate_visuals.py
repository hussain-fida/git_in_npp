import os
import sys
import struct

def create_visuals():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    visuals_dir = os.path.join(script_dir, "visuals")
    os.makedirs(visuals_dir, exist_ok=True)

    # Try using PIL first if installed
    try:
        from PIL import Image, ImageDraw, ImageFont
        use_pil = True
    except ImportError:
        use_pil = False

    if use_pil:
        _generate_with_pil(visuals_dir)
    else:
        _generate_pure_python(visuals_dir)

def _generate_with_pil(visuals_dir):
    from PIL import Image, ImageDraw, ImageFont

    W, H = 340, 220
    BG_COLOR = (24, 28, 36)
    CARD_BG = (34, 40, 52)
    TEXT_COLOR = (240, 243, 246)
    MUTED_TEXT = (140, 150, 165)
    
    COLOR_WORK = (235, 87, 87)
    COLOR_STAGE = (242, 153, 74)
    COLOR_REPO = (46, 204, 113)
    COLOR_REMOTE = (52, 152, 219)
    COLOR_HEAD = (155, 89, 182)
    COLOR_ACCENT = (241, 196, 15)

    def get_font(size=11, bold=False):
        font_names = ["Segoe UI", "arial.ttf", "DejaVuSans.ttf", "tahoma.ttf"]
        for name in font_names:
            try:
                return ImageFont.truetype(name, size)
            except IOError:
                pass
        return ImageFont.load_default()

    font_title = get_font(12, bold=True)
    font_body = get_font(10)
    font_sub = get_font(9)

    def draw_base_header(draw, title, subtitle):
        draw.rectangle([0, 0, W, 30], fill=(18, 22, 28))
        draw.text((10, 7), title, font=font_title, fill=COLOR_ACCENT)
        draw.text((W - 10 - len(subtitle)*6, 8), subtitle, font=font_sub, fill=MUTED_TEXT)

    specs = {
        "add.gif": ("git add", "Staging Changes", COLOR_WORK, COLOR_STAGE),
        "commit.gif": ("git commit", "Saving Local Snapshot", COLOR_STAGE, COLOR_REPO),
        "push.gif": ("git push", "Uploading to Remote", COLOR_REPO, COLOR_REMOTE),
        "pull_fetch.gif": ("git pull/fetch", "Downloading Remote Edits", COLOR_REMOTE, COLOR_REPO),
        "checkout_switch.gif": ("git checkout/switch", "Moving HEAD Pointer", COLOR_HEAD, COLOR_REPO),
        "merge.gif": ("git merge", "Combining Branches", COLOR_STAGE, COLOR_ACCENT),
        "rebase.gif": ("git rebase", "Linearizing History", COLOR_REPO, COLOR_ACCENT),
        "stash.gif": ("git stash", "Saving WIP to Shelf", COLOR_WORK, COLOR_HEAD),
        "reset.gif": ("git reset", "Rewinding HEAD Pointer", COLOR_WORK, COLOR_REPO),
        "restore.gif": ("git restore", "Discarding Edits", COLOR_WORK, COLOR_STAGE),
        "diff.gif": ("git diff", "Comparing Edits", COLOR_ACCENT, COLOR_WORK),
        "log.gif": ("git log", "Commit Timeline", COLOR_REMOTE, COLOR_REPO),
        "tag.gif": ("git tag", "Version Badge", COLOR_ACCENT, COLOR_REPO),
        "clean.gif": ("git clean", "Sweeping Junk Files", COLOR_WORK, COLOR_REPO),
        "worktree.gif": ("git worktree", "Parallel Workspace", COLOR_REPO, COLOR_REMOTE),
        "cherrypick.gif": ("git cherry-pick", "Copying Specific Commit", COLOR_STAGE, COLOR_ACCENT),
        "submodule.gif": ("git submodule", "Nested Git Repository", COLOR_REMOTE, COLOR_REPO),
        "default.gif": ("Git Architecture", "4 Git Stages Overview", COLOR_ACCENT, COLOR_REPO)
    }

    for filename, (title, subtitle, col1, col2) in specs.items():
        frames = []
        for step in range(10):
            img = Image.new("RGB", (W, H), BG_COLOR)
            d = ImageDraw.Draw(img)
            draw_base_header(d, title, subtitle)

            # Draw left card
            d.rectangle([20, 45, 155, 195], fill=CARD_BG, outline=col1, width=2)
            d.text((30, 55), "Source State", font=font_body, fill=col1)

            # Draw right card
            d.rectangle([185, 45, 320, 195], fill=CARD_BG, outline=col2, width=2)
            d.text((195, 55), "Target State", font=font_body, fill=col2)

            # Moving object animation
            progress = (step % 5) / 4.0
            x_pos = int(35 + progress * 165)
            y_pos = 110

            d.rectangle([x_pos, y_pos, x_pos + 60, y_pos + 35], fill=(60, 60, 80), outline=COLOR_ACCENT, width=2)
            d.text((x_pos + 8, y_pos + 10), "ACTION", font=font_sub, fill=TEXT_COLOR)

            # Arrow
            d.line([(140, 127), (180, 127)], fill=COLOR_ACCENT, width=3)
            d.polygon([(180, 121), (190, 127), (180, 133)], fill=COLOR_ACCENT)

            frames.append(img)

        out_path = os.path.join(visuals_dir, filename)
        frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=200, loop=0)

    print(f"PIL Generated {len(specs)} GIF diagrams in '{visuals_dir}'.")


# --- PURE PYTHON GIF ENCODER FALLBACK ---
def _generate_pure_python(visuals_dir):
    W, H = 340, 220
    
    # 16 Color Palette (RGB triplets)
    PALETTE = [
        (24, 28, 36),    # 0: Dark Canvas
        (18, 22, 28),    # 1: Header BG
        (34, 40, 52),    # 2: Card BG
        (240, 243, 246), # 3: Text White
        (140, 150, 165), # 4: Muted Text
        (235, 87, 87),   # 5: Red (Work)
        (242, 153, 74),  # 6: Orange (Stage)
        (46, 204, 113),  # 7: Green (Repo)
        (52, 152, 219),  # 8: Blue (Remote)
        (155, 89, 182),  # 9: Purple (HEAD)
        (241, 196, 15),  # 10: Gold Accent
        (80, 30, 30),    # 11: Dark Red
        (70, 50, 20),    # 12: Dark Orange
        (20, 40, 60),    # 13: Dark Blue
        (70, 40, 80),    # 14: Dark Purple
        (0, 0, 0)        # 15: Black
    ]

    def lzw_encode(pixels, min_code_size=4):
        clear_code = 1 << min_code_size
        eoi_code = clear_code + 1

        output_bytes = bytearray()
        cur_byte = 0
        cur_bits = 0

        def write_code(code, size):
            nonlocal cur_byte, cur_bits
            cur_byte |= (code << cur_bits)
            cur_bits += size
            while cur_bits >= 8:
                output_bytes.append(cur_byte & 0xFF)
                cur_byte >>= 8
                cur_bits -= 8

        cur_code_size = min_code_size + 1
        next_code = eoi_code + 1
        code_table = {}

        write_code(clear_code, cur_code_size)
        prefix = []

        for p in pixels:
            pc = tuple(prefix + [p])
            if pc in code_table:
                prefix.append(p)
            else:
                if prefix:
                    if len(prefix) == 1:
                        write_code(prefix[0], cur_code_size)
                    else:
                        write_code(code_table[tuple(prefix)], cur_code_size)

                code_table[pc] = next_code
                next_code += 1

                if next_code > (1 << cur_code_size) and cur_code_size < 12:
                    cur_code_size += 1

                if next_code == 4096:
                    write_code(clear_code, cur_code_size)
                    cur_code_size = min_code_size + 1
                    next_code = eoi_code + 1
                    code_table = {}

                prefix = [p]

        if prefix:
            if len(prefix) == 1:
                write_code(prefix[0], cur_code_size)
            else:
                write_code(code_table[tuple(prefix)], cur_code_size)

        write_code(eoi_code, cur_code_size)

        if cur_bits > 0:
            output_bytes.append(cur_byte & 0xFF)

        sub_blocks = bytearray([min_code_size])
        idx = 0
        while idx < len(output_bytes):
            chunk = output_bytes[idx : idx + 255]
            sub_blocks.append(len(chunk))
            sub_blocks.extend(chunk)
            idx += len(chunk)
        sub_blocks.append(0)
        return sub_blocks

    def create_gif_file(filepath, frames_pixels):
        with open(filepath, "wb") as f:
            # Header & Screen Descriptor
            f.write(b"GIF89a")
            f.write(struct.pack("<HH", W, H))
            f.write(bytes([0xF3, 0, 0])) # 16 colors global palette

            # Global Color Table (16 * 3 bytes)
            for r, g, b in PALETTE:
                f.write(bytes([r, g, b]))

            # Netscape Looping Extension
            f.write(b"\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00")

            # Frames
            for frame_data in frames_pixels:
                # Graphic Control Extension (200ms delay = 20 centiseconds)
                f.write(b"\x21\xF9\x04\x04\x14\x00\x00\x00")
                # Image Descriptor
                f.write(b"\x2C" + struct.pack("<HHHH", 0, 0, W, H) + b"\x00")
                # LZW Image Data
                f.write(lzw_encode(frame_data, min_code_size=4))

            # Trailer
            f.write(b"\x3B")

    specs = {
        "add.gif": (5, 6, "git add : Working Dir -> Staging"),
        "commit.gif": (6, 7, "git commit : Staging -> Local Repo"),
        "push.gif": (7, 8, "git push : Local Repo -> Remote"),
        "pull_fetch.gif": (8, 7, "git pull : Remote -> Local Workspace"),
        "checkout_switch.gif": (9, 7, "git switch : Moving HEAD Pointer"),
        "merge.gif": (6, 10, "git merge : Combining Branches"),
        "rebase.gif": (7, 10, "git rebase : Linearizing History"),
        "stash.gif": (5, 9, "git stash : Stashing Work to Shelf"),
        "reset.gif": (5, 7, "git reset : Rewinding HEAD Pointer"),
        "restore.gif": (5, 6, "git restore : Discarding Edits"),
        "diff.gif": (10, 5, "git diff : Comparing Code Diffs"),
        "log.gif": (8, 7, "git log : Viewing Commit Timeline"),
        "tag.gif": (10, 7, "git tag : Marking Version Release"),
        "clean.gif": (5, 7, "git clean : Sweeping Junk Files"),
        "worktree.gif": (7, 8, "git worktree : Parallel Folders"),
        "cherrypick.gif": (6, 10, "git cherry-pick : Copying Commit"),
        "submodule.gif": (8, 7, "git submodule : External Repo Link"),
        "default.gif": (10, 7, "Git Workflow Architecture")
    }

    for filename, (col1, col2, title) in specs.items():
        frames = []
        for step in range(6):
            pixels = [0] * (W * H)

            # Draw Header Bar (y: 0..30)
            for y in range(30):
                for x in range(W):
                    pixels[y * W + x] = 1

            # Draw Left Card Box (x: 20..150, y: 45..195)
            for y in range(45, 196):
                for x in range(20, 151):
                    if x in (20, 21, 149, 150) or y in (45, 46, 194, 195):
                        pixels[y * W + x] = col1
                    else:
                        pixels[y * W + x] = 2

            # Draw Right Card Box (x: 190..320, y: 45..195)
            for y in range(45, 196):
                for x in range(190, 321):
                    if x in (190, 191, 319, 320) or y in (45, 46, 194, 195):
                        pixels[y * W + x] = col2
                    else:
                        pixels[y * W + x] = 2

            # Moving Action Box
            progress = step / 5.0
            bx = int(35 + progress * 165)
            by = 110
            for y in range(by, by + 35):
                for x in range(bx, bx + 65):
                    if x in (bx, bx+1, bx+63, bx+64) or y in (by, by+1, by+33, by+34):
                        pixels[y * W + x] = 10
                    else:
                        pixels[y * W + x] = 14

            # Arrow (x: 140..180, y: 125..129)
            for x in range(140, 180):
                for y in range(126, 129):
                    pixels[y * W + x] = 10

            frames.append(pixels)

        out_path = os.path.join(visuals_dir, filename)
        create_gif_file(out_path, frames)

    print(f"Pure Python generated {len(specs)} GIF diagrams in '{visuals_dir}'.")


if __name__ == "__main__":
    create_visuals()
