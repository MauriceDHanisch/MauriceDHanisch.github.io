import os
from PIL import Image
from csscompressor import compress as compress_css
from jsmin import jsmin

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(BASE_DIR, 'assets', 'img')
CSS_DIR = os.path.join(BASE_DIR, 'assets', 'css')
JS_DIR = os.path.join(BASE_DIR, 'assets', 'js')

def optimize_images():
    print("Optimizing images...")
    for filename in os.listdir(IMG_DIR):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(IMG_DIR, filename)
            try:
                with Image.open(filepath) as img:
                    # Resize if too big (max 800px width for PFP/content is plenty)
                    max_width = 800
                    if img.width > max_width:
                        ratio = max_width / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Save as WebP
                    webp_path = os.path.splitext(filepath)[0] + '.webp'
                    img.save(webp_path, 'WEBP', quality=85)
                    print(f"Converted {filename} to {os.path.basename(webp_path)}")
            except Exception as e:
                print(f"Failed to optimize {filename}: {e}")

def minify_css():
    print("Minifying CSS...")
    for filename in os.listdir(CSS_DIR):
        if filename.endswith('.css') and not filename.endswith('.min.css'):
            filepath = os.path.join(CSS_DIR, filename)
            with open(filepath, 'r') as f:
                css = f.read()
            minified = compress_css(css)
            min_path = os.path.splitext(filepath)[0] + '.min.css'
            with open(min_path, 'w') as f:
                f.write(minified)
            print(f"Minified {filename} to {os.path.basename(min_path)}")

def minify_js():
    print("Minifying JS...")
    for filename in os.listdir(JS_DIR):
        if filename.endswith('.js') and not filename.endswith('.min.js'):
            filepath = os.path.join(JS_DIR, filename)
            with open(filepath, 'r') as f:
                js = f.read()
            minified = jsmin(js)
            min_path = os.path.splitext(filepath)[0] + '.min.js'
            with open(min_path, 'w') as f:
                f.write(minified)
            print(f"Minified {filename} to {os.path.basename(min_path)}")

if __name__ == "__main__":
    optimize_images()
    minify_css()
    minify_js()
