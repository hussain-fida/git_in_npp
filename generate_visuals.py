import os
import sys
import struct

def create_visuals():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    visuals_dir = os.path.join(script_dir, "visuals")
    os.makedirs(visuals_dir, exist_ok=True)

    try:
        from PIL import Image, ImageDraw, ImageFont
        use_pil = True
    except ImportError:
        use_pil = False

    if use_pil:
        _generate_with_pil(visuals_dir)
    else:
        _generate_pure_python(visuals_dir)


# --- PIL HIGH QUALITY DIAGRAM GENERATOR ---
def _generate_with_pil(visuals_dir):
    from PIL import Image, ImageDraw, ImageFont

    W, H = 340, 220
    BG = (24, 28, 36)
    CARD_BG = (34, 40, 52)
    TEXT_WHITE = (240, 243, 246)
    MUTED = (140, 150, 165)
    
    C_WORK = (235, 87, 87)    # Red
    C_STAGE = (242, 153, 74)  # Orange
    C_REPO = (46, 204, 113)   # Green
    C_REMOTE = (52, 152, 219) # Blue
    C_HEAD = (155, 89, 182)   # Purple
    C_GOLD = (241, 196, 15)   # Gold

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

    def draw_header(draw, title, subtitle):
        draw.rectangle([0, 0, W, 30], fill=(18, 22, 28))
        draw.text((10, 7), title, font=font_title, fill=C_GOLD)
        draw.text((W - 10 - len(subtitle)*6, 8), subtitle, font=font_sub, fill=MUTED)

    # 1. ADD (Working Dir -> Staging)
    def render_add(step):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        draw_header(d, "git add", "Staging Files (Working -> Staging)")

        d.rectangle([15, 45, 110, 195], fill=CARD_BG, outline=C_WORK, width=2)
        d.text((25, 52), "Working Dir", font=font_body, fill=C_WORK)

        d.rectangle([125, 45, 220, 195], fill=CARD_BG, outline=C_STAGE, width=2)
        d.text((135, 52), "Staging Area", font=font_body, fill=C_STAGE)

        d.rectangle([235, 45, 325, 195], fill=CARD_BG, outline=C_REPO, width=1)
        d.text((245, 52), "Local Repo", font=font_sub, fill=MUTED)

        # Unstaged file
        d.rectangle([25, 80, 100, 110], fill=(70, 30, 30), outline=C_WORK)
        d.text((32, 90), "file.txt [M]", font=font_sub, fill=C_WORK)

        # Animated moving file
        prog = min(step / 8.0, 1.0)
        fx = int(25 + prog * 110)
        col = C_WORK if prog < 0.5 else C_STAGE
        d.rectangle([fx, 135, fx + 75, 170], fill=(70, 50, 20), outline=col, width=2)
        d.text((fx + 8, 147), "index.html", font=font_sub, fill=col)

        d.line([(105, 152), (130, 152)], fill=C_STAGE, width=2)
        d.polygon([(130, 147), (138, 152), (130, 157)], fill=C_STAGE)

        return img

    # 2. COMMIT (Staging -> Local Repo)
    def render_commit(step):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        draw_header(d, "git commit", "Saving Snapshot to Local Repo")

        d.rectangle([15, 45, 110, 195], fill=CARD_BG, outline=C_STAGE, width=2)
        d.text((23, 52), "Staging Area", font=font_body, fill=C_STAGE)

        d.rectangle([125, 45, 325, 195], fill=CARD_BG, outline=C_REPO, width=2)
        d.text((135, 52), "Local Repository History", font=font_body, fill=C_REPO)

        d.rectangle([25, 90, 100, 120], fill=(70, 50, 20), outline=C_STAGE)
        d.text((32, 100), "staged files", font=font_sub, fill=C_STAGE)

        # Commit nodes
        d.line([(140, 125), (310, 125)], fill=MUTED, width=2)
        
        d.ellipse([145, 110, 175, 140], fill=C_REPO)
        d.text((153, 120), "C1", font=font_sub, fill=(0,0,0))

        d.ellipse([215, 110, 245, 140], fill=C_REPO)
        d.text((223, 120), "C2", font=font_sub, fill=(0,0,0))

        prog = min(step / 8.0, 1.0)
        if prog > 0.2:
            node_col = C_GOLD if prog < 0.9 else C_REPO
            d.ellipse([285, 110, 315, 140], fill=node_col)
            d.text((293, 120), "C3", font=font_sub, fill=(0,0,0))
            d.text((280, 150), "[HEAD]", font=font_sub, fill=C_HEAD)

        return img

    # 3. PUSH (Local Repo -> Remote)
    def render_push(step):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        draw_header(d, "git push", "Uploading Commits to Remote (GitHub)")

        d.rectangle([15, 45, 155, 195], fill=CARD_BG, outline=C_REPO, width=2)
        d.text((25, 52), "Local Repository", font=font_body, fill=C_REPO)

        d.rectangle([185, 45, 325, 195], fill=CARD_BG, outline=C_REMOTE, width=2)
        d.text((195, 52), "Remote (GitHub)", font=font_body, fill=C_REMOTE)

        d.ellipse([35, 110, 65, 140], fill=C_REPO)
        d.text((43, 120), "C1", font=font_sub, fill=(0,0,0))
        d.ellipse([95, 110, 125, 140], fill=C_REPO)
        d.text((103, 120), "C2", font=font_sub, fill=(0,0,0))

        prog = min(step / 8.0, 1.0)
        px = int(100 + prog * 130)
        d.ellipse([px, 110, px + 30, 140], fill=C_GOLD)
        d.text((px + 8, 120), "C2", font=font_sub, fill=(0,0,0))

        d.line([(155, 80), (185, 80)], fill=C_REMOTE, width=3)
        d.polygon([(185, 74), (195, 80), (185, 86)], fill=C_REMOTE)

        return img

    # 4. PULL / FETCH (Remote -> Local)
    def render_pull(step):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        draw_header(d, "git pull / fetch", "Downloading Remote Commits")

        d.rectangle([15, 45, 155, 195], fill=CARD_BG, outline=C_REMOTE, width=2)
        d.text((25, 52), "Remote (GitHub)", font=font_body, fill=C_REMOTE)

        d.rectangle([185, 45, 325, 195], fill=CARD_BG, outline=C_REPO, width=2)
        d.text((195, 52), "Local Workspace", font=font_body, fill=C_REPO)

        prog = min(step / 8.0, 1.0)
        px = int(240 - prog * 130)
        d.ellipse([px, 110, px + 30, 140], fill=C_REMOTE)
        d.text((px + 8, 120), "C3", font=font_sub, fill=TEXT_WHITE)

        d.line([(185, 125), (155, 125)], fill=C_GOLD, width=3)
        d.polygon([(155, 119), (145, 125), (155, 131)], fill=C_GOLD)

        return img

    # 5. CHECKOUT / SWITCH (Switch HEAD Pointer)
    def render_checkout(step):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        draw_header(d, "git checkout / switch", "Switching Active HEAD Pointer")

        d.line([(40, 75), (280, 75)], fill=MUTED, width=3)
        d.ellipse([50, 60, 80, 90], fill=C_REPO)
        d.text((58, 68), "C1", font=font_sub, fill=(0,0,0))
        d.ellipse([160, 60, 190, 90], fill=C_REPO)
        d.text((168, 68), "C2", font=font_sub, fill=(0,0,0))
        d.text((210, 67), "[main]", font=font_body, fill=C_REPO)

        d.line([(175, 75), (250, 145)], fill=MUTED, width=3)
        d.ellipse([235, 130, 265, 160], fill=C_STAGE)
        d.text((243, 138), "F1", font=font_sub, fill=(0,0,0))
        d.text((210, 170), "[feature]", font=font_body, fill=C_STAGE)

        prog = min(step / 8.0, 1.0)
        is_feature = prog > 0.4
        head_pos = (210, 185) if is_feature else (210, 42)
        label = "HEAD -> feature" if is_feature else "HEAD -> main"
        d.text(head_pos, label, font=font_body, fill=C_HEAD)

        return img

    # 6. MERGE (Combining Branches)
    def render_merge(step):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        draw_header(d, "git merge", "Integrating Feature Branch into Main")

        d.line([(30, 85), (290, 85)], fill=C_REPO, width=3)
        d.ellipse([40, 70, 70, 100], fill=C_REPO)
        d.text((48, 78), "C1", font=font_sub, fill=(0,0,0))

        d.line([(55, 85), (140, 140)], fill=C_STAGE, width=3)
        d.line([(140, 140), (210, 140)], fill=C_STAGE, width=3)
        d.ellipse([140, 125, 170, 155], fill=C_STAGE)
        d.text((148, 133), "F1", font=font_sub, fill=(0,0,0))

        d.line([(170, 140), (250, 85)], fill=C_STAGE, width=3)

        prog = min(step / 8.0, 1.0)
        if prog > 0.3:
            d.ellipse([240, 70, 270, 100], fill=C_GOLD)
            d.text((246, 78), "M1", font=font_sub, fill=(0,0,0))
            d.text((225, 105), "Merge Commit", font=font_sub, fill=C_GOLD)

        return img

    # 7. REBASE (Linearizing History)
    def render_rebase(step):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        draw_header(d, "git rebase", "Re-applying Commits on New Base")

        d.line([(30, 80), (290, 80)], fill=C_REPO, width=3)
        d.ellipse([40, 65, 70, 95], fill=C_REPO)
        d.text((48, 73), "C1", font=font_sub, fill=(0,0,0))
        d.ellipse([150, 65, 180, 95], fill=C_REPO)
        d.text((158, 73), "C2", font=font_sub, fill=(0,0,0))

        prog = min(step / 8.0, 1.0)
        fx = int(170 + prog * 70)
        fy = int(140 - prog * 60)

        d.ellipse([fx, fy, fx + 30, fy + 30], fill=C_GOLD)
        d.text((fx + 7, fy + 8), "F1'", font=font_sub, fill=(0,0,0))

        return img

    # 8. STASH (Temporary Storage)
    def render_stash(step):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        draw_header(d, "git stash", "Saving WIP to Temporary Shelf")

        d.rectangle([15, 45, 155, 195], fill=CARD_BG, outline=C_WORK, width=2)
        d.text((25, 52), "Working Directory", font=font_body, fill=C_WORK)

        d.rectangle([185, 45, 325, 195], fill=CARD_BG, outline=C_HEAD, width=2)
        d.text((195, 52), "Stash Shelf", font=font_body, fill=C_HEAD)

        prog = min(step / 8.0, 1.0)
        sx = int(30 + prog * 165)
        d.rectangle([sx, 110, sx + 65, 145], fill=(70, 40, 80), outline=C_HEAD, width=2)
        d.text((sx + 7, 120), "stash@{0}", font=font_sub, fill=TEXT_WHITE)

        return img

    # 9. RESET (Rewinding HEAD)
    def render_reset(step):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        draw_header(d, "git reset", "Rewinding HEAD & History")

        d.line([(30, 95), (290, 95)], fill=MUTED, width=3)
        d.ellipse([40, 80, 70, 110], fill=C_REPO)
        d.text((48, 88), "C1", font=font_sub, fill=(0,0,0))
        d.ellipse([150, 80, 180, 110], fill=C_REPO)
        d.text((158, 88), "C2", font=font_sub, fill=(0,0,0))

        d.ellipse([240, 80, 270, 110], fill=(70,70,70))
        d.text((248, 88), "C3", font=font_sub, fill=MUTED)

        prog = min(step / 8.0, 1.0)
        hx = int(240 - prog * 90)
        d.text((hx, 125), "^ HEAD", font=font_body, fill=C_WORK)

        return img

    # 10. RESTORE (Discarding Edits)
    def render_restore(step):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        draw_header(d, "git restore", "Discarding Unstaged Local Edits")

        d.rectangle([20, 45, 160, 195], fill=CARD_BG, outline=C_WORK, width=2)
        d.text((28, 52), "Working Directory", font=font_body, fill=C_WORK)

        d.rectangle([180, 45, 320, 195], fill=CARD_BG, outline=C_REPO, width=2)
        d.text((188, 52), "Last Commit (HEAD)", font=font_body, fill=C_REPO)

        prog = min(step / 8.0, 1.0)
        d.rectangle([35, 95, 140, 135], fill=(80, 30, 30), outline=C_WORK)
        d.text((42, 107), "modified.py", font=font_body, fill=C_WORK)
        if prog > 0.4:
            d.line([(35, 95), (140, 135)], fill=(255, 0, 0), width=3)
            d.line([(35, 135), (140, 95)], fill=(255, 0, 0), width=3)
            d.text((45, 155), "[DISCARDED]", font=font_sub, fill=(255, 100, 100))

        return img

    # 11. DIFF (Code Comparison)
    def render_diff(step):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        draw_header(d, "git diff", "Line-by-Line Code Differences")

        d.rectangle([20, 45, 320, 195], fill=CARD_BG, outline=C_GOLD, width=2)
        d.text((30, 60), "@@ -10,4 +10,5 @@", font=font_sub, fill=MUTED)
        d.text((30, 85), "- const version = '1.0';", font=font_body, fill=(255, 100, 100))
        d.text((30, 110), "+ const version = '2.0';", font=font_body, fill=(100, 255, 100))
        d.text((30, 135), "+ console.log('Updated');", font=font_body, fill=(100, 255, 100))

        return img

    # 12. LOG (Commit Timeline)
    def render_log(step):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        draw_header(d, "git log", "Commit History Timeline")

        d.rectangle([20, 45, 320, 195], fill=CARD_BG, outline=C_REMOTE, width=2)
        d.text((30, 60), "* a1b2c3d (HEAD -> main) Add feature", font=font_sub, fill=C_GOLD)
        d.text((30, 90), "* 9e8d7c6 Fix login crash", font=font_sub, fill=C_REPO)
        d.text((30, 120), "* 5f4e3d2 Initial commit", font=font_sub, fill=MUTED)

        return img

    # 13. TAG (Version Marker)
    def render_tag(step):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        draw_header(d, "git tag", "Release Version Badge")

        d.ellipse([60, 90, 100, 130], fill=C_REPO)
        d.text((72, 103), "C3", font=font_body, fill=(0,0,0))

        prog = min(step / 8.0, 1.0)
        if prog > 0.2:
            d.rectangle([120, 95, 230, 125], fill=C_GOLD)
            d.text((130, 103), "v1.0.0 (Tag)", font=font_body, fill=(0,0,0))
            d.line([(100, 110), (120, 110)], fill=C_GOLD, width=2)

        return img

    # 14. CLEAN (Sweeping Files)
    def render_clean(step):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        draw_header(d, "git clean", "Removing Untracked Junk Files")

        d.rectangle([20, 45, 320, 195], fill=CARD_BG, outline=C_WORK, width=2)
        d.text((30, 55), "Untracked Files:", font=font_body, fill=C_WORK)

        prog = min(step / 8.0, 1.0)
        if prog < 0.7:
            d.text((40, 85), "• temp_debug.log", font=font_sub, fill=MUTED)
            d.text((40, 110), "• build/output.tmp", font=font_sub, fill=MUTED)
        else:
            d.text((40, 95), "[CLEANED & REMOVED]", font=font_body, fill=C_REPO)

        return img

    # 15. WORKTREE (Parallel Workspaces)
    def render_worktree(step):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        draw_header(d, "git worktree", "Parallel Checked-Out Worktrees")

        d.rectangle([120, 45, 220, 95], fill=CARD_BG, outline=C_REPO, width=2)
        d.text((135, 62), "Central .git", font=font_body, fill=C_REPO)

        d.line([(170, 95), (80, 130)], fill=C_GOLD, width=2)
        d.rectangle([20, 130, 140, 190], fill=CARD_BG, outline=C_STAGE, width=2)
        d.text((30, 145), "Worktree 1", font=font_sub, fill=C_STAGE)
        d.text((30, 165), "[main branch]", font=font_sub, fill=MUTED)

        d.line([(170, 95), (260, 130)], fill=C_GOLD, width=2)
        d.rectangle([200, 130, 320, 190], fill=CARD_BG, outline=C_REMOTE, width=2)
        d.text((210, 145), "Worktree 2", font=font_sub, fill=C_REMOTE)
        d.text((210, 165), "[hotfix branch]", font=font_sub, fill=MUTED)

        return img

    # 16. CHERRYPICK (Copying Commit)
    def render_cherrypick(step):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        draw_header(d, "git cherry-pick", "Copying Specific Commit")

        d.text((30, 55), "Branch feature:", font=font_sub, fill=C_STAGE)
        d.ellipse([150, 50, 180, 80], fill=C_GOLD)
        d.text((158, 58), "C5", font=font_body, fill=(0,0,0))

        d.text((30, 135), "Branch main:", font=font_sub, fill=C_REPO)
        d.ellipse([100, 130, 130, 160], fill=C_REPO)
        d.text((108, 138), "C1", font=font_body, fill=(0,0,0))

        prog = min(step / 8.0, 1.0)
        if prog > 0.3:
            d.ellipse([190, 130, 220, 160], fill=C_GOLD)
            d.text((196, 138), "C5'", font=font_body, fill=(0,0,0))
            d.line([(165, 80), (205, 130)], fill=C_GOLD, width=2)

        return img

    # 17. SUBMODULE (Nested Link)
    def render_submodule(step):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        draw_header(d, "git submodule", "Nested Git Repository Link")

        d.rectangle([20, 45, 320, 195], fill=CARD_BG, outline=C_REPO, width=2)
        d.text((30, 55), "Main Project Repository", font=font_body, fill=C_REPO)

        d.rectangle([50, 90, 290, 170], fill=(20, 40, 60), outline=C_REMOTE, width=2)
        d.text((60, 100), "Submodule: libs/vendor-repo", font=font_body, fill=C_REMOTE)
        d.text((60, 130), "• Embedded .git pointer", font=font_sub, fill=MUTED)

        return img

    # 18. DEFAULT (Architecture Overview)
    def render_default(step):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        draw_header(d, "Git Architecture Overview", "4 Core Git Stages")

        box_w = 70
        d.rectangle([10, 55, 10+box_w, 185], fill=CARD_BG, outline=C_WORK)
        d.text((15, 65), "Working\nDirectory", font=font_sub, fill=C_WORK)

        d.rectangle([90, 55, 90+box_w, 185], fill=CARD_BG, outline=C_STAGE)
        d.text((95, 65), "Staging\nArea", font=font_sub, fill=C_STAGE)

        d.rectangle([170, 55, 170+box_w, 185], fill=CARD_BG, outline=C_REPO)
        d.text((175, 65), "Local\nRepo", font=font_sub, fill=C_REPO)

        d.rectangle([250, 55, 250+box_w, 185], fill=CARD_BG, outline=C_REMOTE)
        d.text((255, 65), "Remote\nRepo", font=font_sub, fill=C_REMOTE)

        return img

    render_map = {
        "add.gif": render_add,
        "commit.gif": render_commit,
        "push.gif": render_push,
        "pull_fetch.gif": render_pull,
        "checkout_switch.gif": render_checkout,
        "merge.gif": render_merge,
        "rebase.gif": render_rebase,
        "stash.gif": render_stash,
        "reset.gif": render_reset,
        "restore.gif": render_restore,
        "diff.gif": render_diff,
        "log.gif": render_log,
        "tag.gif": render_tag,
        "clean.gif": render_clean,
        "worktree.gif": render_worktree,
        "cherrypick.gif": render_cherrypick,
        "submodule.gif": render_submodule,
        "default.gif": render_default
    }

    for filename, render_func in render_map.items():
        frames = []
        # Generate 10 motion frames
        for step in range(10):
            frames.append(render_func(step))
        
        # Add 4 pause/hold frames of final state for comfortable reading
        final_frame = frames[-1]
        for _ in range(4):
            frames.append(final_frame)

        out_path = os.path.join(visuals_dir, filename)
        # Duration = 450ms (45 centiseconds) per frame for smooth, relaxed animation
        frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=450, loop=0)

    print(f"PIL successfully generated {len(render_map)} custom GIF diagrams in '{visuals_dir}'.")


# --- PURE PYTHON ZERO-DEPENDENCY GENERATOR ---
def _generate_pure_python(visuals_dir):
    W, H = 340, 220
    
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
            f.write(b"GIF89a")
            f.write(struct.pack("<HH", W, H))
            f.write(bytes([0xF3, 0, 0]))

            for r, g, b in PALETTE:
                f.write(bytes([r, g, b]))

            f.write(b"\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00")

            for frame_data in frames_pixels:
                # 45 centiseconds delay = 450ms
                f.write(b"\x21\xF9\x04\x04\x2D\x00\x00\x00")
                f.write(b"\x2C" + struct.pack("<HHHH", 0, 0, W, H) + b"\x00")
                f.write(lzw_encode(frame_data, min_code_size=4))

            f.write(b"\x3B")

    specs = {
        "add.gif": (5, 6),
        "commit.gif": (6, 7),
        "push.gif": (7, 8),
        "pull_fetch.gif": (8, 7),
        "checkout_switch.gif": (9, 7),
        "merge.gif": (6, 10),
        "rebase.gif": (7, 10),
        "stash.gif": (5, 9),
        "reset.gif": (5, 7),
        "restore.gif": (5, 6),
        "diff.gif": (10, 5),
        "log.gif": (8, 7),
        "tag.gif": (10, 7),
        "clean.gif": (5, 7),
        "worktree.gif": (7, 8),
        "cherrypick.gif": (6, 10),
        "submodule.gif": (8, 7),
        "default.gif": (10, 7)
    }

    for filename, (col1, col2) in specs.items():
        frames = []
        for step in range(8):
            pixels = [0] * (W * H)

            for y in range(30):
                for x in range(W):
                    pixels[y * W + x] = 1

            for y in range(45, 196):
                for x in range(20, 151):
                    if x in (20, 21, 149, 150) or y in (45, 46, 194, 195):
                        pixels[y * W + x] = col1
                    else:
                        pixels[y * W + x] = 2

            for y in range(45, 196):
                for x in range(190, 321):
                    if x in (190, 191, 319, 320) or y in (45, 46, 194, 195):
                        pixels[y * W + x] = col2
                    else:
                        pixels[y * W + x] = 2

            prog = step / 7.0
            bx = int(35 + prog * 165)
            by = 110
            for y in range(by, by + 35):
                for x in range(bx, bx + 65):
                    if x in (bx, bx+1, bx+63, bx+64) or y in (by, by+1, by+33, by+34):
                        pixels[y * W + x] = 10
                    else:
                        pixels[y * W + x] = 14

            for x in range(140, 180):
                for y in range(126, 129):
                    pixels[y * W + x] = 10

            frames.append(pixels)

        # Duplicate final state for hold pause
        final_p = frames[-1]
        for _ in range(4):
            frames.append(final_p)

        out_path = os.path.join(visuals_dir, filename)
        create_gif_file(out_path, frames)

    print(f"Pure Python generated {len(specs)} GIF diagrams in '{visuals_dir}'.")


if __name__ == "__main__":
    create_visuals()
