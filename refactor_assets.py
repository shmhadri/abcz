
import os
import re

BASE_DIR = r"c:\Users\shmha\abcz"
HTML_FILE = os.path.join(BASE_DIR, "fgfg.html")
CSS_FILE = os.path.join(BASE_DIR, "static", "css", "fgfg.css")
JS_FILE = os.path.join(BASE_DIR, "static", "js", "fgfg.js")

def extract_assets():
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract CSS
    css_match = re.search(r"<style>(.*?)</style>", content, re.DOTALL)
    if css_match:
        css_content = css_match.group(1).strip()
        with open(CSS_FILE, "w", encoding="utf-8") as f:
            f.write(css_content)
        print(f"Extracted CSS to {CSS_FILE} ({len(css_content)} bytes)")
    else:
        print("No CSS Style block found.")

    # Extract JS
    # Finding the main script block at the end
    script_matches = list(re.finditer(r"<script>(.*?)</script>", content, re.DOTALL))
    if script_matches:
        # Assuming the last large script block is the main one
        main_script = script_matches[-1]
        js_content = main_script.group(1).strip()
        print(f"Extracted JS to {JS_FILE} ({len(js_content)} bytes)")
        
        # Rewrite HTML
        new_html = content
        
        # Replace CSS
        if css_match:
            new_html = new_html.replace(css_match.group(0), '<link rel="stylesheet" href="/static/css/fgfg.css">')
        
        # Replace JS
        # We replace the LAST script block.
        if script_matches:
            last_script = script_matches[-1]
            # Write JS file (restoring this logic just in case)
            with open(JS_FILE, "w", encoding="utf-8") as f:
                f.write(last_script.group(1).strip())
            
            # Replace in HTML
            new_html = new_html.replace(last_script.group(0), '<script src="/static/js/fgfg.js"></script>')
        
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(new_html)
        print("Updated fgfg.html with links.")

    else:
        print("No Script block found.")

if __name__ == "__main__":
    extract_assets()
