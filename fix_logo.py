import base64
import re

with open("static/logo.jpg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")

with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace all image srcs that contain logo.jpg
new_html = re.sub(r'src="[^"]*logo\.jpg[^"]*"', f'src="data:image/jpeg;base64,{b64}"', html)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(new_html)

print("Logo successfully embedded as base64.")
