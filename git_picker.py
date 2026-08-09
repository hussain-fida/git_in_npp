import sys
import os
import re
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import font, messagebox

script_dir = os.path.dirname(os.path.abspath(__file__))
xml_file = os.path.join(script_dir, "git_commands.xml")
visuals_dir = os.path.join(script_dir, "visuals")

# Ensure visuals directory exists and contains all required GIF files
required_gifs = [
    "add.gif", "commit.gif", "push.gif", "pull_fetch.gif",
    "checkout_switch.gif", "merge.gif", "rebase.gif", "stash.gif",
    "reset.gif", "restore.gif", "diff.gif", "log.gif", "tag.gif",
    "clean.gif", "worktree.gif", "cherrypick.gif", "submodule.gif", "default.gif"
]

missing_gifs = not os.path.exists(visuals_dir) or any(
    not os.path.exists(os.path.join(visuals_dir, g)) for g in required_gifs
)

if missing_gifs:
    try:
        from generate_visuals import create_visuals
        create_visuals()
    except Exception as e:
        print(f"Notice: Visual generation warning: {e}")

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

# --- TOP AREA (SPLIT: LISTBOX LEFT | GIF PREVIEW RIGHT) ---
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

lbl_gif_display = tk.Label(right_container, bg="#181c24")
lbl_gif_display.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

current_gif_frames = []
gif_animation_after_id = None
current_frame_index = 0

def stop_gif_animation():
    global gif_animation_after_id
    if gif_animation_after_id is not None:
        try:
            root.after_cancel(gif_animation_after_id)
        except Exception:
            pass
        gif_animation_after_id = None

def animate_gif():
    global current_frame_index, gif_animation_after_id
    if current_gif_frames:
        try:
            frame = current_gif_frames[current_frame_index]
            lbl_gif_display.config(image=frame)
            current_frame_index = (current_frame_index + 1) % len(current_gif_frames)
            gif_animation_after_id = root.after(180, animate_gif)
        except Exception:
            stop_gif_animation()

def load_and_play_gif(gif_filename):
    global current_gif_frames, current_frame_index
    stop_gif_animation()
    current_gif_frames.clear()
    current_frame_index = 0

    gif_path = os.path.join(visuals_dir, gif_filename)
    if not os.path.exists(gif_path):
        gif_path = os.path.join(visuals_dir, "default.gif")

    if os.path.exists(gif_path):
        idx = 0
        while True:
            try:
                frame = tk.PhotoImage(file=gif_path, format=f"gif -index {idx}")
                current_gif_frames.append(frame)
                idx += 1
            except tk.TclError:
                break
            except Exception:
                break
    
    if current_gif_frames:
        animate_gif()
    else:
        lbl_gif_display.config(image='', text="[ No Visual Diagram Available ]", fg="#94a3b8", font=("Segoe UI", 9, "italic"))

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
            
            load_and_play_gif(m['gif'])
            
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
        stop_gif_animation()
        root.destroy()
    except Exception as err:
        show_error_dialog("Selection Error", f"Error confirming command selection: {err}")

def cancel_selection(event=None):
    selected_command[0] = ""
    stop_gif_animation()
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