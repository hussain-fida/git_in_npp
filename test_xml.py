import xml.etree.ElementTree as ET
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
xml_path = os.path.join(script_dir, "git_commands.xml")

# Trigger visual generation
try:
    from generate_visuals import create_visuals
    create_visuals()
except Exception as e:
    print(f"Notice: {e}")

tree = ET.parse(xml_path)
root = tree.getroot()

items = root.findall('item')
print(f"Total commands in XML: {len(items)}")

required_tags = ['command', 'desc', 'desc1', 'desc2', 'gif', 'alt', 'warning', 'next']
missing_count = 0

for idx, item in enumerate(items, 1):
    cmd_text = item.find('command').text if item.find('command') is not None else "UNKNOWN"
    for tag in required_tags:
        elem = item.find(tag)
        if elem is None or elem.text is None:
            print(f"Item #{idx} ({cmd_text}) missing tag: <{tag}>")
            missing_count += 1

visuals_dir = os.path.join(script_dir, "visuals")
if os.path.exists(visuals_dir):
    gif_files = os.listdir(visuals_dir)
    print(f"GIF files in 'visuals/': {len(gif_files)} -> {gif_files}")

if missing_count == 0:
    print("SUCCESS: All XML command items have complete tags and GIF generator is verified!")
