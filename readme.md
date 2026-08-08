# Portable Notepad++ Git Command Launcher

An automated, interactive Git command search engine and launcher for Notepad++ using **NppExec**, **Python (Tkinter)**, and **XML**. Search your personalized Git command library by tags/keywords, preview warnings and alternative syntax, fill in placeholders (`<msg>`, `<branch>`, `<hash>`), and execute commands directly in the Notepad++ console.

---

## 🌟 Features

* **Instant Tag Search:** Search Git commands by tags, descriptions, or keyword filters.
* **Interactive Command Picker:** Browse matching commands in a clean GUI window using keyboard arrow keys.
* **Command Guidance:** Displays alternative command hints, risk warnings, and next recommended steps live in the preview panel.
* **Smart Parameter Prompts:** Automatically opens a wide multi-line text input box when commands contain placeholders like `<msg>`, `<branch>`, or `<hash>`.
* **Keyboard-First Workflow:** Press `ESC` to exit without running anything, `Ctrl+Enter` or `Enter` to submit.
* **Full Portability:** Uses `$(NPP_DIRECTORY)` variables—works seamlessly across portable USB drives or different system paths.

---

## 📁 File Structure

Place the following files directly inside your Notepad++ portable root directory (e.g., `E:\server\0installed\notePad++\npp.8.9.portable\`):

```text
Notepad++/
├── git_commands.xml           # XML database of Git commands, tags, and metadata
├── git_picker.py              # Python Tkinter GUI picker & input dialogs
├── git_picker_nppExec.txt     # NppExec automation script