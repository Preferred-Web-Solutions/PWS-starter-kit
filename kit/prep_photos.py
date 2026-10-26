"""Export a site's photos at two widths with light, honest correction (no retouching of content).
Usage from a site's prep script:
    from prep_photos import export
    export({'hero': ('src/g-dig.jpg', (0, 0, 1, 1))}, out='site/img', meta='build/img-meta.json')
crop is (left, top, right, bottom) as fractions of the image, so faces, third-party brands or clutter can be cropped out."""
import os, json
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

def export(spec, out, meta, widths=(640, 1100), q_small=72, q_big=68):
    os.makedirs(out, exist_ok=True); m = {}
    for key, (src, crop) in spec.items():
        im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
        W, H = im.size; l, t, r, b = crop
        im = im.crop((round(l * W), round(t * H), round(r * W), round(b * H)))
        im = ImageOps.autocontrast(im, cutoff=0.3, preserve_tone=True)
        im = ImageEnhance.Contrast(im).enhance(1.03); im = ImageEnhance.Color(im).enhance(1.04)
        W, H = im.size
        sizes = sorted({min(w, W) for w in widths})
        for tw in sizes:
            x = im.resize((tw, round(H * tw / W)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.0, percent=30, threshold=2))
            x.save(f'{out}/{key}-{tw}.jpg', quality=q_big if tw > widths[0] else q_small, optimize=True, progressive=True)
        m[key] = {'w': W, 'h': H, 'sizes': sizes}
    json.dump(m, open(meta, 'w'), indent=1)
    kb = sum(os.path.getsize(f'{out}/{f}') for f in os.listdir(out) if f.endswith('.jpg')) // 1024
    print(len(m), 'photos;', kb, 'KB total')
    return m
