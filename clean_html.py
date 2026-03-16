import re

with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace any data:image.. or url_for logo.jpg with url_for logo.png
html = re.sub(r'src="data:image[^"]*"', r'src="{{ url_for(\'static\', filename=\'logo.png\') }}"', html)
html = re.sub(r'src="[^"]*logo\.jpg[^"]*"', r'src="{{ url_for(\'static\', filename=\'logo.png\') }}"', html)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Updated HTML to use logo.png")
