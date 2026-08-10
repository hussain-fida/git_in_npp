import sys
import os
import re
import math
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import font, messagebox

script_dir = os.path.dirname(os.path.abspath(__file__))
xml_file = os.path.join(script_dir, "git_commands.xml")

search_term = sys.argv[1].lower().strip() if len(sys.argv) > 1 else ""

def show_error_dialog(title, message):
    """Graceful error popup dialog."""
    try:
        err_root = tk.Tk()
        err_root.withdraw()
        err_root.attributes("-topmost", True)
        messagebox.showerror(title, message, parent=err_root)
        err_root.destroy()
    except Exception:
        print(f"[{title}] {message}")

def load_xml_safely(filepath):
    """Safely loads XML file, auto-repairing unescaped brackets or entity errors if needed."""
    if not os.path.exists(filepath):
        show_error_dialog("File Not Found", f"Database file not found:\n{filepath}")
        return None
    try:
        tree = ET.parse(filepath)
        return tree.getroot()
    except ET.ParseError as pe:
        # Auto-recovery: Read raw file content and sanitize unescaped < > brackets in text nodes
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            valid_tags = {'commands', '/commands', 'item', '/item', 'command', '/command', 
                          'tagq', '/tagq', 'desc', '/desc', 'desc1', '/desc1', 
                          'desc2', '/desc2', 'gif', '/gif', 'alt', '/alt', 'warning', '/warning', 'next', '/next'}
            
            def sanitize_bracket(match):
                tag_name = match.group(1)
                if tag_name in valid_tags:
                    return f"<{tag_name}>"
                return f"&lt;{tag_name}&gt;"

            sanitized = re.sub(r'<([^>]+)>', sanitize_bracket, content)
            root = ET.fromstring(sanitized)
            return root
        except Exception as recovery_err:
            show_error_dialog("XML Parse Error", f"Failed to parse 'git_commands.xml':\n\n{pe}\n\nRecovery attempt also failed: {recovery_err}")
            return None
    except Exception as e:
        show_error_dialog("XML Load Error", f"Unexpected error reading XML:\n\n{e}")
        return None

root_xml = load_xml_safely(xml_file)
if root_xml is None:
    sys.exit(0)

class GitCanvasVisualizer:
    """High-performance native Tkinter Canvas visualizer for Git workflow diagrams."""
    def __init__(self, parent_frame, width=340, height=220):
        self.canvas = tk.Canvas(parent_frame, width=width, height=height, bg="#0f172a", highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.width = width
        self.height = height
        self.anim_after_id = None
        self.anim_step = 0
        self.current_gif_key = "default.gif"
        self.current_cmd = ""

    def stop_animation(self):
        if self.anim_after_id is not None:
            try:
                self.canvas.after_cancel(self.anim_after_id)
            except Exception:
                pass
            self.anim_after_id = None

    def render(self, gif_key, cmd=""):
        self.stop_animation()
        self.current_gif_key = gif_key
        self.current_cmd = cmd
        self.anim_step = 0
        self.animate()

    def animate(self):
        self.draw_frame(self.current_gif_key, self.current_cmd, self.anim_step)
        self.anim_step = (self.anim_step + 1) % 20
        self.anim_after_id = self.canvas.after(90, self.animate)

    def draw_base_zones(self, active_zones=(1, 2, 3, 4)):
        c = self.canvas
        c.delete("all")
        
        # Header bar
        c.create_rectangle(0, 0, 340, 30, fill="#1e293b", outline="")
        c.create_text(12, 15, text=f"Visual: {self.current_cmd or 'Git Architecture'}", anchor="w", fill="#eab308", font=("Segoe UI", 9, "bold"))

        # Zone Definitions: (id, x1, x2, title, color)
        zones = [
            (1, 8, 85, "Working Dir", "#ef4444"),
            (2, 91, 168, "Staging", "#f59e0b"),
            (3, 174, 251, "Local Repo", "#10b981"),
            (4, 257, 332, "Remote", "#3b82f6")
        ]

        for zid, x1, x2, title, color in zones:
            is_active = zid in active_zones
            bg_col = "#1e293b" if is_active else "#0f172a"
            bd_col = color if is_active else "#334155"
            txt_col = color if is_active else "#64748b"
            
            c.create_rectangle(x1, 38, x2, 215, fill=bg_col, outline=bd_col, width=2 if is_active else 1)
            c.create_text((x1 + x2) // 2, 48, text=title, fill=txt_col, font=("Segoe UI", 8, "bold"))

    def draw_file_badge(self, x, y, text, color="#f59e0b"):
        c = self.canvas
        c.create_rectangle(x - 28, y - 10, x + 28, y + 10, fill="#0f172a", outline=color, width=1.5)
        c.create_text(x, y, text=text, fill=color, font=("Consolas", 8, "bold"))

    def draw_commit_node(self, x, y, label, color="#10b981", active=False):
        c = self.canvas
        r = 11 if active else 9
        outline_w = 2 if active else 1.5
        c.create_oval(x - r, y - r, x + r, y + r, fill="#0f172a", outline=color, width=outline_w)
        c.create_text(x, y, text=label, fill=color, font=("Consolas", 8, "bold"))

    def draw_arrow(self, x1, y1, x2, y2, color="#38bdf8", width=2):
        c = self.canvas
        c.create_line(x1, y1, x2, y2, fill=color, width=width, arrow=tk.LAST, arrowshape=(8, 10, 4))

    def draw_frame(self, gif_key, cmd, step):
        c = self.canvas
        prog = step / 19.0  # 0.0 to 1.0

        if gif_key == "add.gif":
            self.draw_base_zones(active_zones=(1, 2))
            self.draw_file_badge(46, 85, "file.txt", color="#ef4444")
            
            # Motion from Work (46) to Stage (130)
            fx = int(46 + prog * 84)
            self.draw_file_badge(fx, 135, "index.html", color="#f59e0b")
            self.draw_arrow(86, 135, 125, 135, color="#f59e0b")
            c.create_text(170, 195, text="Staging Working Changes", fill="#f59e0b", font=("Segoe UI", 8, "italic"))

        elif gif_key == "commit.gif":
            self.draw_base_zones(active_zones=(2, 3))
            self.draw_file_badge(130, 85, "index.html", color="#f59e0b")
            
            # Existing local commits
            self.draw_commit_node(195, 150, "C1", color="#10b981")
            self.draw_commit_node(230, 150, "C2", color="#10b981")
            c.create_line(204, 150, 221, 150, fill="#10b981", width=2)
            
            # Motion into new commit C3
            if prog > 0.3:
                self.draw_commit_node(240, 110, "C3", color="#eab308", active=True)
                c.create_line(230, 141, 237, 120, fill="#eab308", width=2)
                c.create_text(240, 92, text="HEAD -> main", fill="#eab308", font=("Consolas", 7, "bold"))
            
            self.draw_arrow(160, 110, 220, 110, color="#eab308")
            c.create_text(170, 195, text="Creating Snapshot in History", fill="#eab308", font=("Segoe UI", 8, "italic"))

        elif gif_key == "push.gif":
            self.draw_base_zones(active_zones=(3, 4))
            self.draw_commit_node(195, 135, "C1", color="#10b981")
            self.draw_commit_node(230, 135, "C2", color="#10b981")
            c.create_line(204, 135, 221, 135, fill="#10b981", width=2)
            
            # Transfer packet moving from Local Repo (212) to Remote (295)
            px = int(230 + prog * 65)
            py = int(135 - math.sin(prog * math.pi) * 35) if 'math' in sys.modules else 115
            self.draw_commit_node(px, py, "C2", color="#3b82f6", active=True)
            self.draw_arrow(235, 120, 290, 120, color="#38bdf8", width=2.5)
            
            self.draw_commit_node(295, 135, "C1", color="#3b82f6")
            c.create_text(170, 195, text="Uploading Local Commits -> Remote", fill="#38bdf8", font=("Segoe UI", 8, "italic"))

        elif gif_key == "pull_fetch.gif":
            self.draw_base_zones(active_zones=(3, 4))
            self.draw_commit_node(295, 135, "C1", color="#3b82f6")
            self.draw_commit_node(295, 95, "C2", color="#3b82f6")
            c.create_line(295, 126, 295, 104, fill="#3b82f6", width=2)
            
            # Incoming download packet moving Remote (295) -> Local (212)
            px = int(295 - prog * 83)
            self.draw_commit_node(px, 135, "C2", color="#a855f7", active=True)
            self.draw_arrow(280, 155, 225, 155, color="#a855f7", width=2.5)
            
            self.draw_commit_node(212, 135, "C1", color="#10b981")
            c.create_text(170, 195, text="Downloading & Merging Remote", fill="#a855f7", font=("Segoe UI", 8, "italic"))

        elif gif_key == "checkout_switch.gif":
            self.draw_base_zones(active_zones=(3,))
            # Main line
            c.create_text(188, 70, text="main", fill="#10b981", font=("Consolas", 8, "bold"))
            self.draw_commit_node(212, 90, "M1", color="#10b981")
            self.draw_commit_node(240, 90, "M2", color="#10b981")
            c.create_line(221, 90, 231, 90, fill="#10b981", width=2)
            
            # Feature line
            c.create_text(188, 140, text="feat", fill="#a855f7", font=("Consolas", 8, "bold"))
            self.draw_commit_node(212, 160, "F1", color="#a855f7")
            self.draw_commit_node(240, 160, "F2", color="#a855f7")
            c.create_line(221, 160, 231, 160, fill="#a855f7", width=2)
            
            # Switching HEAD pointer
            head_y = 90 if prog < 0.5 else 160
            head_col = "#eab308" if prog < 0.5 else "#a855f7"
            c.create_rectangle(172, head_y - 8, 200, head_y + 8, fill=head_col, outline="")
            c.create_text(186, head_y, text="HEAD", fill="#0f172a", font=("Consolas", 7, "bold"))
            c.create_text(170, 195, text="Switching Active Working Branch", fill="#eab308", font=("Segoe UI", 8, "italic"))

        elif gif_key == "merge.gif":
            self.draw_base_zones(active_zones=(3,))
            self.draw_commit_node(195, 120, "C1", color="#10b981")
            self.draw_commit_node(220, 85, "F1", color="#a855f7")
            c.create_line(204, 120, 212, 85, fill="#a855f7", width=2)
            
            # Merge commit
            if prog > 0.4:
                self.draw_commit_node(245, 120, "M", color="#eab308", active=True)
                c.create_line(204, 120, 236, 120, fill="#10b981", width=2)
                c.create_line(228, 85, 239, 112, fill="#a855f7", width=2)
                c.create_text(245, 140, text="Merge Node", fill="#eab308", font=("Consolas", 7, "bold"))
            
            c.create_text(170, 195, text="Combining History Paths", fill="#eab308", font=("Segoe UI", 8, "italic"))

        elif gif_key == "rebase.gif":
            self.draw_base_zones(active_zones=(3,))
            self.draw_commit_node(195, 100, "C1", color="#10b981")
            self.draw_commit_node(225, 100, "C2", color="#10b981")
            c.create_line(204, 100, 216, 100, fill="#10b981", width=2)
            
            # Lifted feature commit re-attaching
            rx = int(195 + prog * 55)
            ry = int(140 - prog * 40)
            self.draw_commit_node(rx, ry, "F1'", color="#a855f7", active=True)
            c.create_line(225, 100, rx, ry, fill="#a855f7", width=1.5, dash=(2, 2))
            c.create_text(170, 195, text="Re-applying Commits on Top of Main", fill="#a855f7", font=("Segoe UI", 8, "italic"))

        elif gif_key == "stash.gif":
            self.draw_base_zones(active_zones=(1, 2))
            # Stash storage drawer on bottom
            c.create_rectangle(15, 160, 160, 205, fill="#0f172a", outline="#a855f7", width=1.5)
            c.create_text(87, 172, text="Temporary Stash Stack", fill="#a855f7", font=("Segoe UI", 8, "bold"))
            
            sy = int(85 + prog * 85) if prog < 0.5 else int(170 - (prog - 0.5) * 85)
            self.draw_file_badge(46, sy, "WIP.patch", color="#a855f7")
            c.create_text(170, 195, text="Shelving Work-In-Progress", fill="#a855f7", font=("Segoe UI", 8, "italic"))

        elif gif_key == "reset.gif":
            self.draw_base_zones(active_zones=(2, 3))
            self.draw_commit_node(195, 120, "C1", color="#10b981")
            self.draw_commit_node(225, 120, "C2", color="#ef4444")
            c.create_line(204, 120, 216, 120, fill="#10b981", width=2)
            
            # Rewind arrow pointing backwards
            self.draw_arrow(225, 95, 195, 95, color="#ef4444", width=2)
            c.create_text(210, 80, text="Rewind HEAD", fill="#ef4444", font=("Consolas", 7, "bold"))
            c.create_text(170, 195, text="Resetting History / Unstaging", fill="#ef4444", font=("Segoe UI", 8, "italic"))

        elif gif_key == "restore.gif":
            self.draw_base_zones(active_zones=(1, 2))
            self.draw_file_badge(46, 110, "file.txt [M]", color="#ef4444")
            
            # Discard motion
            alpha_col = "#ef4444" if prog < 0.7 else "#64748b"
            c.create_line(25, 110, 67, 110, fill=alpha_col, width=2)
            c.create_text(170, 195, text="Discarding Unstaged Changes", fill="#ef4444", font=("Segoe UI", 8, "italic"))

        elif gif_key == "diff.gif":
            c.delete("all")
            c.create_rectangle(0, 0, 340, 30, fill="#1e293b", outline="")
            c.create_text(12, 15, text=f"Visual: {cmd or 'git diff'}", anchor="w", fill="#eab308", font=("Segoe UI", 9, "bold"))
            
            # Code diff viewer card
            c.create_rectangle(15, 40, 325, 185, fill="#1e293b", outline="#334155", width=1.5)
            c.create_text(30, 58, text="--- a/src/main.py", fill="#94a3b8", anchor="w", font=("Consolas", 8))
            c.create_text(30, 75, text="+++ b/src/main.py", fill="#94a3b8", anchor="w", font=("Consolas", 8))
            
            c.create_rectangle(25, 92, 315, 112, fill="#451a1a", outline="")
            c.create_text(30, 102, text="-  def old_calculator():", fill="#ef4444", anchor="w", font=("Consolas", 8, "bold"))
            
            c.create_rectangle(25, 120, 315, 140, fill="#064e3b", outline="")
            c.create_text(30, 130, text="+  def modern_fast_calculator():", fill="#10b981", anchor="w", font=("Consolas", 8, "bold"))
            
            c.create_text(30, 158, text="   return result", fill="#cbd5e1", anchor="w", font=("Consolas", 8))
            c.create_text(170, 195, text="Comparing Changes Line by Line", fill="#38bdf8", font=("Segoe UI", 8, "italic"))

        elif gif_key == "log.gif":
            c.delete("all")
            c.create_rectangle(0, 0, 340, 30, fill="#1e293b", outline="")
            c.create_text(12, 15, text=f"Visual: {cmd or 'git log'}", anchor="w", fill="#eab308", font=("Segoe UI", 9, "bold"))
            
            # Commit history timeline
            c.create_rectangle(15, 40, 325, 185, fill="#1e293b", outline="#334155", width=1.5)
            
            logs = [
                ("a1b2c3d", "feat: Add core visualizer", "HEAD -> main", "#eab308"),
                ("9f8e7d6", "fix: Optimize XML safe load", "origin/main", "#3b82f6"),
                ("5a4b3c2", "docs: Update setup guide", "", "#94a3b8")
            ]
            
            for idx, (chash, cmsg, ctag, ccol) in enumerate(logs):
                ly = 65 + idx * 38
                is_sel = (int(step / 6) % 3) == idx
                if is_sel:
                    c.create_rectangle(22, ly - 12, 318, ly + 14, fill="#0f172a", outline=ccol, width=1.5)
                
                c.create_oval(32 - 4, ly - 4, 32 + 4, ly + 4, fill=ccol, outline="")
                if idx < 2:
                    c.create_line(32, ly + 4, 32, ly + 34, fill="#475569", width=1.5)
                    
                c.create_text(45, ly, text=chash, fill="#eab308", anchor="w", font=("Consolas", 8, "bold"))
                c.create_text(105, ly, text=cmsg, fill="#f8fafc", anchor="w", font=("Segoe UI", 8))
                if ctag:
                    c.create_text(285, ly, text=ctag, fill=ccol, anchor="e", font=("Consolas", 7, "bold"))

            c.create_text(170, 195, text="Interactive Commit History Timeline", fill="#eab308", font=("Segoe UI", 8, "italic"))

        elif gif_key == "tag.gif":
            self.draw_base_zones(active_zones=(3,))
            self.draw_commit_node(195, 130, "C1", color="#10b981")
            self.draw_commit_node(230, 130, "C2", color="#10b981", active=True)
            c.create_line(204, 130, 221, 130, fill="#10b981", width=2)
            
            # Tag badge pinning down
            tag_y = int(70 + prog * 20)
            c.create_rectangle(205, tag_y - 10, 255, tag_y + 10, fill="#eab308", outline="#0f172a")
            c.create_text(230, tag_y, text="v1.0.0", fill="#0f172a", font=("Consolas", 8, "bold"))
            c.create_line(230, tag_y + 10, 230, 119, fill="#eab308", width=2, arrow=tk.LAST)
            c.create_text(170, 195, text="Pinning Release Milestone Tag", fill="#eab308", font=("Segoe UI", 8, "italic"))

        elif gif_key == "clean.gif":
            self.draw_base_zones(active_zones=(1,))
            self.draw_file_badge(46, 85, "tracked.py", color="#10b981")
            
            # Untracked files getting cleared
            if prog < 0.7:
                self.draw_file_badge(46, 125, "temp.log", color="#ef4444")
                self.draw_file_badge(46, 160, "build/", color="#ef4444")
            else:
                c.create_text(46, 140, text="[CLEARED]", fill="#10b981", font=("Consolas", 8, "bold"))
                
            c.create_text(170, 195, text="Purging Untracked Junk Files", fill="#ef4444", font=("Segoe UI", 8, "italic"))

        elif gif_key == "worktree.gif":
            c.delete("all")
            c.create_rectangle(0, 0, 340, 30, fill="#1e293b", outline="")
            c.create_text(12, 15, text=f"Visual: {cmd or 'git worktree'}", anchor="w", fill="#eab308", font=("Segoe UI", 9, "bold"))
            
            # Shared .git db
            c.create_rectangle(120, 130, 220, 180, fill="#1e293b", outline="#10b981", width=2)
            c.create_text(170, 155, text="Shared .git DB", fill="#10b981", font=("Segoe UI", 8, "bold"))
            
            # Worktree 1
            c.create_rectangle(20, 45, 140, 90, fill="#1e293b", outline="#ef4444", width=1.5)
            c.create_text(80, 67, text="Worktree 1\n(main branch)", fill="#ef4444", font=("Segoe UI", 8, "bold"))
            
            # Worktree 2
            c.create_rectangle(200, 45, 320, 90, fill="#1e293b", outline="#3b82f6", width=1.5)
            c.create_text(260, 67, text="Worktree 2\n(feature branch)", fill="#3b82f6", font=("Segoe UI", 8, "bold"))
            
            c.create_line(80, 90, 140, 130, fill="#ef4444", width=1.5)
            c.create_line(260, 90, 200, 130, fill="#3b82f6", width=1.5)
            c.create_text(170, 195, text="Multiple Linked Working Directories", fill="#eab308", font=("Segoe UI", 8, "italic"))

        elif gif_key == "cherrypick.gif":
            self.draw_base_zones(active_zones=(3,))
            c.create_text(188, 75, text="main", fill="#10b981", font=("Consolas", 8, "bold"))
            self.draw_commit_node(212, 95, "M1", color="#10b981")
            
            c.create_text(188, 140, text="feat", fill="#a855f7", font=("Consolas", 8, "bold"))
            self.draw_commit_node(212, 160, "F1", color="#a855f7")
            self.draw_commit_node(240, 160, "F2*", color="#eab308", active=True)
            
            # Copying commit F2* onto main line
            cx = int(240 - prog * 0)
            cy = int(160 - prog * 65)
            self.draw_commit_node(cx, cy, "F2*", color="#eab308", active=True)
            c.create_line(212, 95, cx, cy, fill="#eab308", width=1.5)
            c.create_text(170, 195, text="Copying Specific Commit to Main", fill="#eab308", font=("Segoe UI", 8, "italic"))

        elif gif_key == "submodule.gif":
            c.delete("all")
            c.create_rectangle(0, 0, 340, 30, fill="#1e293b", outline="")
            c.create_text(12, 15, text=f"Visual: {cmd or 'git submodule'}", anchor="w", fill="#eab308", font=("Segoe UI", 9, "bold"))
            
            # Outer Main Repo
            c.create_rectangle(20, 45, 320, 185, fill="#1e293b", outline="#3b82f6", width=2)
            c.create_text(40, 60, text="Parent Repository (main-project)", fill="#3b82f6", anchor="w", font=("Segoe UI", 8, "bold"))
            
            # Inner Submodule Repo
            c.create_rectangle(60, 85, 280, 160, fill="#0f172a", outline="#a855f7", width=1.5)
            c.create_text(75, 102, text="Submodule: lib/shared-plugin", fill="#a855f7", anchor="w", font=("Consolas", 8, "bold"))
            c.create_text(75, 125, text="Pinned Pointer: @ commit 7a8b9c", fill="#94a3b8", anchor="w", font=("Consolas", 8))
            c.create_text(170, 195, text="Nested Standalone Repository", fill="#a855f7", font=("Segoe UI", 8, "italic"))

        else:  # default.gif
            self.draw_base_zones(active_zones=(1, 2, 3, 4))
            self.draw_arrow(86, 125, 90, 125, color="#ef4444")
            self.draw_arrow(169, 125, 173, 125, color="#f59e0b")
            self.draw_arrow(252, 125, 256, 125, color="#10b981")
            
            # Animated active pulse dot
            px = int(45 + (step % 4) * 80)
            c.create_oval(px - 5, 120, px + 5, 130, fill="#eab308", outline="")
            c.create_text(170, 195, text="Interactive Git 4-Zone Flow Diagram", fill="#eab308", font=("Segoe UI", 8, "italic"))

matches = []
try:
    for item in root_xml.findall('item'):
        cmd = item.find('command').text if item.find('command') is not None else ""
        tags = item.find('tagq').text if item.find('tagq') is not None else ""
        desc = item.find('desc').text if item.find('desc') is not None else ""
        desc1 = item.find('desc1').text if item.find('desc1') is not None else "Detailed mechanism not specified."
        desc2 = item.find('desc2').text if item.find('desc2') is not None else "Practical use cases not specified."
        gif_file = item.find('gif').text if item.find('gif') is not None else "default.gif"
        alt = item.find('alt').text if item.find('alt') is not None else "N/A"
        warning = item.find('warning').text if item.find('warning') is not None else "None"
        next_cmd = item.find('next').text if item.find('next') is not None else "N/A"
        
        # Check if search term matches
        if search_term in tags.lower() or search_term in cmd.lower() or search_term in desc.lower():
            score = 0
            cmd_lower = cmd.lower()
            desc_lower = desc.lower()
            tags_lower = tags.lower()
            
            if cmd_lower.startswith(search_term):
                score += 100
            elif search_term in cmd_lower:
                score += 50
            elif search_term in tags_lower:
                score += 30
            elif search_term in desc_lower:
                score += 10
            
            if search_term in tags_lower.split(', '):
                score += 20
                
            matches.append({
                "cmd": cmd,
                "desc": desc,
                "desc1": desc1,
                "desc2": desc2,
                "gif": gif_file,
                "tags": tags,
                "alt": alt,
                "warning": warning,
                "next": next_cmd,
                "score": score
            })

    matches.sort(key=lambda x: x["score"], reverse=True)
except Exception as parse_err:
    show_error_dialog("Data Error", f"Error filtering XML commands:\n{parse_err}")
    sys.exit(0)

if not matches:
    sys.exit(0)

root = tk.Tk()
root.title(f"Interactive Git Command Launcher — Keyword: '{search_term}'")
root.geometry("960x600")
root.configure(bg="#f0f2f5")
root.attributes("-topmost", True)

# --- TOP AREA (SPLIT: LISTBOX LEFT | CANVAS PREVIEW RIGHT) ---
top_frame = tk.Frame(root, bg="#f0f2f5")
top_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(10, 5))

left_container = tk.Frame(top_frame, bg="#f0f2f5")
left_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

lbl_header = tk.Label(left_container, text="Select Command (Up/Down to navigate | ENTER to run | ESC to cancel)", 
                      font=("Segoe UI", 9, "bold"), fg="#2b579a", bg="#f0f2f5")
lbl_header.pack(anchor="w", pady=(0, 4))

listbox_frame = tk.Frame(left_container, bg="#ffffff", bd=1, relief=tk.SOLID)
listbox_frame.pack(fill=tk.BOTH, expand=True)

listbox = tk.Listbox(listbox_frame, font=("Segoe UI", 10), selectmode=tk.SINGLE, height=7, bd=0, highlightthickness=0)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)

scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox.config(yscrollcommand=scrollbar.set)

for m in matches:
    display_text = m['desc']
    listbox.insert(tk.END, f"• {display_text}")

result_count = tk.Label(left_container, text=f"Found {len(matches)} matching command(s)", 
                        font=("Segoe UI", 8, "italic"), fg="#666666", bg="#f0f2f5")
result_count.pack(anchor="w", pady=(4, 0))

right_container = tk.Frame(top_frame, bg="#ffffff", bd=1, relief=tk.SOLID, width=350)
right_container.pack(side=tk.RIGHT, fill=tk.Y, padx=(4, 0))
right_container.pack_propagate(False)

lbl_visual_header = tk.Label(right_container, text="Visual Command Diagram", 
                             font=("Segoe UI", 9, "bold"), fg="#1e293b", bg="#e2e8f0")
lbl_visual_header.pack(fill=tk.X, ipady=4)

visualizer = GitCanvasVisualizer(right_container, width=340, height=220)


# --- BOTTOM AREA: DETAILS & GUIDANCE PANEL ---
bottom_frame = tk.Frame(root, bg="#f0f2f5")
bottom_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))

lbl_detail = tk.Label(bottom_frame, text="Command Details & In-Depth Guidance:", font=("Segoe UI", 9, "bold"), fg="#1e293b", bg="#f0f2f5")
lbl_detail.pack(anchor="w", pady=(2, 2))

txt_preview = tk.Text(bottom_frame, height=10, font=("Consolas", 10), bg="#ffffff", fg="#0f172a", wrap="word", bd=1, relief=tk.SOLID)
txt_preview.pack(fill=tk.BOTH, expand=True)

txt_preview.tag_configure("header", font=("Consolas", 10, "bold"), foreground="#2563eb")
txt_preview.tag_configure("cmd_text", font=("Consolas", 10, "bold"), foreground="#059669")
txt_preview.tag_configure("warn_text", font=("Consolas", 10, "bold"), foreground="#dc2626")
txt_preview.tag_configure("body_text", font=("Consolas", 10), foreground="#1e293b")
txt_preview.tag_configure("sub_text", font=("Consolas", 10), foreground="#475569")

lbl_footer = tk.Label(root, text="Press [ESC] to exit without executing | Use [Up/Down] arrows to explore", 
                      font=("Segoe UI", 8, "italic"), fg="#64748b", bg="#f0f2f5")
lbl_footer.pack(anchor="e", padx=12, pady=(0, 6))

selected_command = [""]

def custom_prompt(title, prompt_text, default_value=""):
    """Custom wide modal input dialog."""
    try:
        dialog = tk.Toplevel(root)
        dialog.title(title)
        dialog.geometry("560x230")
        dialog.configure(bg="#f8fafc")
        dialog.attributes("-topmost", True)
        dialog.grab_set()
        
        user_input = [""]
        
        lbl = tk.Label(dialog, text=prompt_text, font=("Segoe UI", 10, "bold"), fg="#0f172a", bg="#f8fafc")
        lbl.pack(anchor="w", padx=15, pady=(15, 5))
        
        entry = tk.Text(dialog, height=4, font=("Consolas", 10), wrap="word", relief=tk.SOLID, bd=1)
        entry.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        if default_value:
            entry.insert("1.0", default_value)
        entry.focus_set()
        
        def on_ok(event=None):
            val = entry.get("1.0", tk.END).strip()
            if val:
                user_input[0] = val
            dialog.destroy()
            
        def on_cancel(event=None):
            dialog.destroy()
            
        btn_frame = tk.Frame(dialog, bg="#f8fafc")
        btn_frame.pack(anchor="e", padx=15, pady=(5, 15))
        
        btn_ok = tk.Button(btn_frame, text=" OK ", font=("Segoe UI", 9, "bold"), bg="#2563eb", fg="#ffffff", width=10, command=on_ok, relief=tk.FLAT)
        btn_ok.pack(side=tk.LEFT, padx=5)
        
        btn_cancel = tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 9), bg="#e2e8f0", fg="#334155", width=10, command=on_cancel, relief=tk.FLAT)
        btn_cancel.pack(side=tk.LEFT, padx=5)
        
        dialog.bind("<Control-Return>", on_ok)
        dialog.bind("<Escape>", on_cancel)
        
        root.wait_window(dialog)
        return user_input[0]
    except Exception as err:
        show_error_dialog("Dialog Error", f"Input prompt error: {err}")
        return ""

def get_placeholder_prompt(cmd, placeholder):
    prompts = {
        'commitmsg': ('Commit Message', 'Enter descriptive commit message (Ctrl+ENTER to submit):', 'feat: Add new feature'),
        'branchname': ('Branch Name', 'Enter branch name (Ctrl+ENTER to submit):', 'feature/new-feature'),
        'filename': ('File Name', 'Enter file path (Ctrl+ENTER to submit):', 'index.html'),
        'commithash': ('Commit Hash', 'Enter target commit hash (Ctrl+ENTER to submit):', 'a1b2c3d'),
        'repourl': ('Repository URL', 'Enter Git repository URL (Ctrl+ENTER to submit):', 'https://github.com/username/repo.git'),
        'username': ('Git Username', 'Enter Git username (Ctrl+ENTER to submit):', 'Your Name'),
        'useremail': ('Git Email', 'Enter Git email address (Ctrl+ENTER to submit):', 'your.email@example.com'),
        'editor': ('Text Editor', 'Enter core editor command (Ctrl+ENTER to submit):', 'code --wait'),
        'tagname': ('Tag Name', 'Enter release tag name (Ctrl+ENTER to submit):', 'v1.0.0'),
        'tagmsg': ('Tag Message', 'Enter tag message (Ctrl+ENTER to submit):', 'Release version 1.0.0'),
        'stashmsg': ('Stash Message', 'Enter stash label message (Ctrl+ENTER to submit):', 'WIP: Work in progress'),
        'number': ('Number', 'Enter numeric value (Ctrl+ENTER to submit):', '5'),
        'branch1': ('First Branch', 'Enter base branch (Ctrl+ENTER to submit):', 'main'),
        'branch2': ('Second Branch', 'Enter feature branch (Ctrl+ENTER to submit):', 'develop'),
        'repodir': ('Directory Name', 'Enter target directory path (Ctrl+ENTER to submit):', 'project-folder')
    }
    return prompts.get(placeholder, ('Input Required', f'Enter value for <{placeholder}>:', ''))

def update_preview(event=None):
    try:
        if event and event.keysym in ("Up", "Down"):
            curr_idx = listbox.curselection()[0] if listbox.curselection() else 0
            if event.keysym == "Up" and curr_idx > 0:
                curr_idx -= 1
            elif event.keysym == "Down" and curr_idx < listbox.size() - 1:
                curr_idx += 1
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(curr_idx)
            listbox.see(curr_idx)

        selection = listbox.curselection()
        if selection:
            idx = selection[0]
            m = matches[idx]
            
            visualizer.render(m['gif'], m['cmd'])
            
            txt_preview.config(state=tk.NORMAL)
            txt_preview.delete("1.0", tk.END)
            
            txt_preview.insert(tk.END, "COMMAND        : ", "header")
            txt_preview.insert(tk.END, f"{m['cmd']}\n", "cmd_text")
            
            txt_preview.insert(tk.END, "HOW IT WORKS   : ", "header")
            txt_preview.insert(tk.END, f"{m['desc1']}\n", "body_text")
            
            txt_preview.insert(tk.END, "USE CASES & TIPS: ", "header")
            txt_preview.insert(tk.END, f"{m['desc2']}\n", "body_text")
            
            txt_preview.insert(tk.END, "ALTERNATIVE HINT: ", "header")
            txt_preview.insert(tk.END, f"{m['alt']}\n", "sub_text")
            
            txt_preview.insert(tk.END, "WARNING/SAFETY : ", "header")
            warn_style = "warn_text" if "DANGER" in m['warning'] or "CAUTION" in m['warning'] or "RISKY" in m['warning'] else "sub_text"
            txt_preview.insert(tk.END, f"{m['warning']}\n", warn_style)
            
            txt_preview.insert(tk.END, "RECOMMENDED NEXT: ", "header")
            txt_preview.insert(tk.END, f"{m['next']}\n", "cmd_text")
            
            txt_preview.insert(tk.END, "TAGS & SEARCH  : ", "header")
            txt_preview.insert(tk.END, f"{m['tags']} (Score: {m['score']})", "sub_text")
            
            txt_preview.config(state=tk.DISABLED)
    except Exception as err:
        print(f"Preview update error: {err}")

def confirm_selection(event=None):
    try:
        selection = listbox.curselection()
        if selection:
            cmd = matches[selection[0]]['cmd']
            replacements = {}
            placeholders = re.findall(r'<([^>]+)>', cmd)
            
            if placeholders:
                for placeholder in placeholders:
                    title, prompt_text, default_value = get_placeholder_prompt(cmd, placeholder)
                    value = custom_prompt(title, prompt_text, default_value)
                    if value:
                        replacements[placeholder] = value
                    else:
                        return
                
                for placeholder, value in replacements.items():
                    cmd = cmd.replace(f'<{placeholder}>', value)
            
            selected_command[0] = cmd
        visualizer.stop_animation()
        root.destroy()
    except Exception as err:
        show_error_dialog("Selection Error", f"Error confirming command selection: {err}")

def cancel_selection(event=None):
    selected_command[0] = ""
    visualizer.stop_animation()
    root.destroy()

listbox.bind("<<ListboxSelect>>", update_preview)
listbox.bind("<KeyRelease-Up>", update_preview)
listbox.bind("<KeyRelease-Down>", update_preview)
listbox.bind("<Return>", confirm_selection)
listbox.bind("<Double-Button-1>", confirm_selection)
root.bind("<Escape>", cancel_selection)

listbox.selection_set(0)
listbox.focus_set()
update_preview()

root.mainloop()

out_file = os.path.join(script_dir, "selected_cmd.txt")
try:
    with open(out_file, "w", encoding="utf-8") as f:
        if selected_command[0]:
            f.write(f'set SELECTED_CMD = {selected_command[0]}\n')
        else:
            f.write('unset SELECTED_CMD\n')
except Exception as err:
    show_error_dialog("File Save Error", f"Failed to save selected_cmd.txt:\n{err}")