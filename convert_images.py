import os
import re
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "source", "images")
# 需要更新引用路径的文件/目录
REF_ROOTS = [
    os.path.join(BASE_DIR, "source"),
    os.path.join(BASE_DIR, "_config.butterfly.yml"),
]

def convert_png_to_webp():
    converted = {}
    for name in os.listdir(IMG_DIR):
        if name.lower().endswith(".png"):
            src = os.path.join(IMG_DIR, name)
            dst = os.path.join(IMG_DIR, name[:-4] + ".webp")
            with Image.open(src) as im:
                im = im.convert("RGB")
                im.save(dst, "WEBP", quality=82)
            os.remove(src)
            converted[name] = name[:-4] + ".webp"
            print(f"converted: {name} -> {converted[name]}")
    return converted

def update_refs(converted):
    # 构建 png->webp 映射（含 /images/ 前缀与 .png 后缀）
    mapping = {}
    for png, webp in converted.items():
        mapping["/images/" + png] = "/images/" + webp
        mapping["images/" + png] = "images/" + webp

    # 遍历 source 下所有 md 与主题 yml
    targets = []
    for root, _, files in os.walk(os.path.join(BASE_DIR, "source")):
        for f in files:
            if f.endswith(".md"):
                targets.append(os.path.join(root, f))
    targets.append(os.path.join(BASE_DIR, "_config.butterfly.yml"))

    for path in targets:
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
        new_content = content
        for png_ref, webp_ref in mapping.items():
            new_content = new_content.replace(png_ref, webp_ref)
        if new_content != content:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new_content)
            print(f"updated refs: {path}")

if __name__ == "__main__":
    c = convert_png_to_webp()
    update_refs(c)
    print("DONE")
