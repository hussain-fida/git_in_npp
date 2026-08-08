import sys
import os
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import font

script_dir = os.path.dirname(os.path.abspath(__file__))
xml_file = os.path.join(script_dir, "git_commands.xml")

search_term = sys.argv[1].lower().strip() if len(sys.argv) > 1 else ""

if not os.path.exists(xml_file):
    sys.exit(0)

tree = ET.parse(xml_file)
root_xml = tree.getroot()

matches = []
for item in root_xml.findall('item'):
    cmd = item.find('command').text if item.find('command') is not None else ""
    tags = item.find('tagq').text if item.find('tagq') is not None else ""
    desc = item.find('desc').text if item.find('desc') is not None else ""
    alt = item.find('alt').text if item.find('alt') is not None else "N/A"
    warning = item.find('warning').text if item.find('warning') is not None else "None"
    next_cmd = item.find('next').text if item.find('next') is not None else "N/A"
    
    # Check if search term matches
    if search_term in tags.lower() or search_term in cmd.lower() or search_term in desc.lower():
        # Calculate relevance score for sorting
        score = 0
        cmd_lower = cmd.lower()
        desc_lower = desc.lower()
        tags_lower = tags.lower()
        
        # Highest priority: command starts with search term (exact match at start)
        if cmd_lower.startswith(search_term):
            score += 100
        # Second priority: search term is in command (as a word)
        elif search_term in cmd_lower:
            score += 50
        # Third priority: search term is in tags
        elif search_term in tags_lower:
            score += 30
        # Fourth priority: search term is in description
        elif search_term in desc_lower:
            score += 10
        
        # Additional boost for exact tag match
        if search_term in tags_lower.split(', '):
            score += 20
            
        matches.append({
            "cmd": cmd,
            "desc": desc,
            "tags": tags,
            "alt": alt,
            "warning": warning,
            "next": next_cmd,
            "score": score
        })

# Sort matches by relevance score (highest first)
matches.sort(key=lambda x: x["score"], reverse=True)

if not matches:
    sys.exit(0)

root = tk.Tk()
root.title(f"Git Command Selector — Keyword: '{search_term}'")
root.geometry("680x440")
root.attributes("-topmost", True)

# Header & Shortcuts Hint
lbl_header = tk.Label(root, text="Select Command (Up/Down to navigate | ENTER to run | ESC to cancel)", 
                      font=("Segoe UI", 9, "bold"), fg="#2b579a")
lbl_header.pack(anchor="w", padx=10, pady=(8, 2))

# Listbox with search result count
listbox_frame = tk.Frame(root)
listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=2)

listbox = tk.Listbox(listbox_frame, font=("Segoe UI", 10), selectmode=tk.SINGLE, height=6)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox.config(yscrollcommand=scrollbar.set)

# Display matches with command prefix visible
for m in matches:
    # Extract command name from desc (format: "command : description")
    display_text = m['desc']  # Already has "command : " prefix
    listbox.insert(tk.END, f"• {display_text}")

# Show result count
result_count = tk.Label(root, text=f"Found {len(matches)} matching command(s)", 
                        font=("Segoe UI", 8, "italic"), fg="#666666")
result_count.pack(anchor="w", padx=10, pady=(0, 2))

# Details Panel
lbl_detail = tk.Label(root, text="Command Details & Guidance:", font=("Segoe UI", 9, "bold"))
lbl_detail.pack(anchor="w", padx=10, pady=(5, 2))

txt_preview = tk.Text(root, height=8, font=("Consolas", 9), bg="#f8f9fa", wrap="word")
txt_preview.pack(fill=tk.BOTH, padx=10, pady=(0, 5))

# Footer Hint for ESC key
lbl_footer = tk.Label(root, text="Press [ESC] to exit without executing any command", 
                      font=("Segoe UI", 8, "italic"), fg="#666666")
lbl_footer.pack(anchor="e", padx=10, pady=(0, 8))

selected_command = [""]

def custom_prompt(title, prompt_text, default_value=""):
    """Custom wide/tall dialog box with optional default value."""
    dialog = tk.Toplevel(root)
    dialog.title(title)
    dialog.geometry("550x220")
    dialog.attributes("-topmost", True)
    dialog.grab_set()
    
    user_input = [""]
    
    lbl = tk.Label(dialog, text=prompt_text, font=("Segoe UI", 10, "bold"))
    lbl.pack(anchor="w", padx=15, pady=(15, 5))
    
    # Entry with optional default value
    entry = tk.Text(dialog, height=4, font=("Consolas", 10), wrap="word", relief=tk.SOLID, bd=1)
    entry.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
    if default_value:
        entry.insert("1.0", default_value)
    entry.focus_set()
    entry.tag_configure("center", justify='center')
    
    def on_ok(event=None):
        val = entry.get("1.0", tk.END).strip()
        if val:
            user_input[0] = val
        dialog.destroy()
        
    def on_cancel(event=None):
        dialog.destroy()
        
    btn_frame = tk.Frame(dialog)
    btn_frame.pack(anchor="e", padx=15, pady=(5, 15))
    
    btn_ok = tk.Button(btn_frame, text=" OK ", font=("Segoe UI", 9), width=10, command=on_ok)
    btn_ok.pack(side=tk.LEFT, padx=5)
    
    btn_cancel = tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 9), width=10, command=on_cancel)
    btn_cancel.pack(side=tk.LEFT, padx=5)
    
    # Keybindings for dialog
    dialog.bind("<Control-Return>", on_ok)
    dialog.bind("<Escape>", on_cancel)
    
    root.wait_window(dialog)
    return user_input[0]

def get_placeholder_prompt(cmd, placeholder):
    """Return appropriate prompt based on placeholder type."""
    prompts = {
        'commitmsg': {
            'title': 'Commit Message',
            'prompt': 'Enter commit message (Press Ctrl+ENTER or OK to submit):\n\nTip: Use present tense, be descriptive',
            'default': 'feat: Add new feature'
        },
        'branchname': {
            'title': 'Branch Name',
            'prompt': 'Enter branch name (Press Ctrl+ENTER or OK to submit):\n\nTip: Use descriptive names like feature/login-page',
            'default': 'feature/new-feature'
        },
        'filename': {
            'title': 'File Name',
            'prompt': 'Enter file name/path (Press Ctrl+ENTER or OK to submit):\n\nTip: Use relative path like src/index.html',
            'default': 'file.txt'
        },
        'commithash': {
            'title': 'Commit Hash',
            'prompt': 'Enter commit hash (Press Ctrl+ENTER or OK to submit):\n\nTip: Use full or short hash like a1b2c3d',
            'default': 'a1b2c3d'
        },
        'repourl': {
            'title': 'Repository URL',
            'prompt': 'Enter repository URL (Press Ctrl+ENTER or OK to submit):\n\nTip: Format: https://github.com/username/repo.git',
            'default': 'https://github.com/username/repo.git'
        },
        'username': {
            'title': 'Git Username',
            'prompt': 'Enter your Git username (Press Ctrl+ENTER or OK to submit):\n\nTip: Use your full name or GitHub username',
            'default': 'Your Name'
        },
        'useremail': {
            'title': 'Git Email',
            'prompt': 'Enter your Git email (Press Ctrl+ENTER or OK to submit):\n\nTip: Use the email associated with your GitHub account',
            'default': 'your.email@example.com'
        },
        'editor': {
            'title': 'Text Editor',
            'prompt': 'Enter editor command (Press Ctrl+ENTER or OK to submit):\n\nTip: Use "code --wait" for VS Code, "vim" for Vim',
            'default': 'code --wait'
        },
        'tagname': {
            'title': 'Tag Name',
            'prompt': 'Enter tag name (Press Ctrl+ENTER or OK to submit):\n\nTip: Use version like v1.0.0',
            'default': 'v1.0.0'
        },
        'tagmsg': {
            'title': 'Tag Message',
            'prompt': 'Enter tag message (Press Ctrl+ENTER or OK to submit):\n\nTip: Describe the release or version',
            'default': 'Release version 1.0.0'
        },
        'stashmsg': {
            'title': 'Stash Message',
            'prompt': 'Enter stash message (Press Ctrl+ENTER or OK to submit):\n\nTip: Describe what you\'re stashing',
            'default': 'WIP: Work in progress'
        },
        'number': {
            'title': 'Number',
            'prompt': 'Enter number (Press Ctrl+ENTER or OK to submit):\n\nTip: Enter a numeric value',
            'default': '5'
        },
        'branch1': {
            'title': 'First Branch',
            'prompt': 'Enter first branch name (Press Ctrl+ENTER or OK to submit):\n\nTip: Usually the base branch',
            'default': 'main'
        },
        'branch2': {
            'title': 'Second Branch',
            'prompt': 'Enter second branch name (Press Ctrl+ENTER or OK to submit):\n\nTip: Usually the feature branch',
            'default': 'develop'
        },
        'repodir': {
            'title': 'Directory Name',
            'prompt': 'Enter directory name (Press Ctrl+ENTER or OK to submit):\n\nTip: Repository folder name after cloning',
            'default': 'project-name'
        }
    }
    
    # Map placeholder to prompt config
    placeholder_map = {
        'commitmsg': prompts['commitmsg'],
        'branchname': prompts['branchname'],
        'filename': prompts['filename'],
        'commithash': prompts['commithash'],
        'repourl': prompts['repourl'],
        'username': prompts['username'],
        'useremail': prompts['useremail'],
        'editor': prompts['editor'],
        'tagname': prompts['tagname'],
        'tagmsg': prompts['tagmsg'],
        'stashmsg': prompts['stashmsg'],
        'number': prompts['number'],
        'branch1': prompts['branch1'],
        'branch2': prompts['branch2'],
        'repodir': prompts['repodir']
    }
    
    prompt_config = placeholder_map.get(placeholder, {
        'title': 'Input Required',
        'prompt': f'Enter value for {placeholder} (Press Ctrl+ENTER or OK to submit):',
        'default': ''
    })
    
    return prompt_config['title'], prompt_config['prompt'], prompt_config['default']

def update_preview(event=None):
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
        
        info_text = (
            f"COMMAND  : {m['cmd']}\n"
            f"ALT HINT : {m['alt']}\n"
            f"WARNING  : {m['warning']}\n"
            f"NEXT STEP: {m['next']}\n"
            f"TAGS     : {m['tags']}\n"
            f"SCORE    : {m['score']} (relevance)"
        )
        
        txt_preview.config(state=tk.NORMAL)
        txt_preview.delete("1.0", tk.END)
        txt_preview.insert(tk.END, info_text)
        txt_preview.config(state=tk.DISABLED)

def confirm_selection(event=None):
    selection = listbox.curselection()
    if selection:
        cmd = matches[selection[0]]['cmd']
        
        # Dictionary to store all placeholder replacements
        replacements = {}
        
        # Find all placeholders in the command
        import re
        placeholders = re.findall(r'<([^>]+)>', cmd)
        
        if placeholders:
            # Process each placeholder
            for placeholder in placeholders:
                # Get the appropriate prompt for this placeholder
                title, prompt_text, default_value = get_placeholder_prompt(cmd, placeholder)
                
                # Show the prompt dialog
                value = custom_prompt(title, prompt_text, default_value)
                if value:
                    replacements[placeholder] = value
                else:
                    # User cancelled
                    return
            
            # Apply all replacements
            for placeholder, value in replacements.items():
                cmd = cmd.replace(f'<{placeholder}>', value)
        
        selected_command[0] = cmd
    root.destroy()

def cancel_selection(event=None):
    selected_command[0] = ""
    root.destroy()

# Key & Event Bindings
listbox.bind("<<ListboxSelect>>", update_preview)
listbox.bind("<KeyRelease-Up>", update_preview)
listbox.bind("<KeyRelease-Down>", update_preview)
listbox.bind("<Return>", confirm_selection)
listbox.bind("<Double-Button-1>", confirm_selection)
root.bind("<Escape>", cancel_selection)

# Initial setup - select first item (most relevant due to sorting)
listbox.selection_set(0)
listbox.focus_set()
update_preview()

root.mainloop()

# Save selected command to text file for NppExec
out_file = os.path.join(script_dir, "selected_cmd.txt")
with open(out_file, "w", encoding="utf-8") as f:
    if selected_command[0]:
        f.write(f'set SELECTED_CMD = {selected_command[0]}\n')
    else:
        f.write('unset SELECTED_CMD\n')