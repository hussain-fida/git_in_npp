# Portable Notepad++ Visual Git Command Launcher

An automated, interactive Git command search engine and visual launcher for Notepad++ using **NppExec**, **Python (Tkinter)**, and an **XML database**. Search your personalized Git command library by tags/keywords, view live animated GIF visual diagrams of Git operations, read in-depth explanations (`<desc1>`) and practical use cases (`<desc2>`), fill in placeholders (`<commitmsg>`, `<branchname>`, `<commithash>`), and execute commands directly in the Notepad++ console.

---

## 🌟 Features

* **Visual GIF Diagrams:** Displays live animated diagrams for each Git command showing file movement (Working Directory $\rightarrow$ Staging $\rightarrow$ Local Repo $\rightarrow$ Remote), HEAD pointer movement, branch merging, rebase, and stashing.
* **In-Depth Guidance (`<desc1>` & `<desc2>`):** Multi-tiered documentation detailing technical mechanisms under the hood (`<desc1>`) and practical use-cases / best practices (`<desc2>`).
* **Instant Tag Search & Scoring:** Search Git commands by tags, descriptions, or keywords sorted by relevance score.
* **Interactive Command Picker:** Browse matching commands in a side-by-side GUI window using keyboard arrow keys.
* **Smart Parameter Prompts:** Automatically opens a wide modal dialog when commands contain placeholders like `<commitmsg>`, `<branchname>`, or `<commithash>`.
* **Keyboard-First Workflow:** Press `ESC` to exit without running anything, `Ctrl+Enter` or `Enter` to submit.
* **Full Portability:** Uses `$(NPP_DIRECTORY)` variables—works seamlessly across portable USB drives or different system paths.

---

## 📁 File Structure

Place the following files directly inside your Notepad++ portable root directory:

```text
Notepad++/
├── git_commands.xml           # XML database of Git commands, tags, <desc1>, <desc2>, and <gif> metadata
├── git_picker.py              # Python Tkinter GUI picker with GIF preview & modal input dialogs
├── generate_visuals.py        # Python script to render animated GIF visual diagrams
├── visuals/                   # Subdirectory containing animated GIF diagrams for Git command categories
├── git_picker_nppExec_command.txt  # NppExec automation script
```