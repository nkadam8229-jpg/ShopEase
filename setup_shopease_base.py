#!/usr/bin/env python3
"""
ShopEase base inventory setup.
Creates/upserts the canonical categories, subcategories and 54-brand master,
and imports category/subcategory images plus verified brand logos when present.

Run from the ShopEase project root:
    python setup_shopease_base.py --inventory "../ShopEase_Inventry"

The script is safe to rerun. It matches records by canonical names and does not
create duplicate categories, subcategories or brands.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

from PIL import Image

# Make the script runnable from the project root regardless of cwd.
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

ALLOWED = {"jpg", "jpeg", "png", "webp"}


def parse_args():
    p = argparse.ArgumentParser(description="Set up ShopEase base inventory data.")
    p.add_argument(
        "--inventory",
        default=str(PROJECT_ROOT.parent / "ShopEase_Inventry"),
        help="Path to the ShopEase_Inventry directory.",
    )
    p.add_argument("--dry-run", action="store_true", help="Validate without changing the DB/files.")
    return p.parse_args()


def find_image(folder: Path, prefix: str) -> Path | None:
    if not folder.exists():
        return None
    candidates = []
    for f in folder.iterdir():
        if not f.is_file() or f.suffix.lower().lstrip(".") not in ALLOWED:
            continue
        if f.stem.lower() == prefix.lower():
            candidates.append(f)
    return sorted(candidates)[0] if candidates else None


def process_and_save(path: Path, storage, folder: str) -> str:
    with path.open("rb") as fh:
        output, filename = process_image(_NamedFile(fh, path.name))
    return storage.save(output, folder, filename)


class _NamedFile:
    def __init__(self, fh, name):
        self._fh = fh
        self.filename = name

    def seek(self, *args):
        return self._fh.seek(*args)

    def read(self, *args):
        return self._fh.read(*args)


def load_brand_manifest(brands_root: Path):
    manifest_path = brands_root / "brand_folder_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing brand_folder_manifest.json: {manifest_path}")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    brands = data.get("brands", [])
    if len(brands) != 54:
        raise ValueError(f"Expected 54 brands in manifest, found {len(brands)}")
    return brands


def main():
    args = parse_args()
    inventory = Path(args.inventory).expanduser().resolve()
    categories_root = inventory / "Categories"
    brands_root = inventory / "Brands"

    if not categories_root.is_dir():
        raise SystemExit(f"Inventory Categories folder not found: {categories_root}")
    if not brands_root.is_dir():
        raise SystemExit(f"Inventory Brands folder not found: {brands_root}")

    category_dirs = sorted(p for p in categories_root.iterdir() if p.is_dir())
    if len(category_dirs) != 4:
        raise SystemExit(f"Expected 4 category folders, found {len(category_dirs)}")

    manifest = load_brand_manifest(brands_root)

    # Validate all source images before touching the DB.
    image_sources = []
    for cat_dir in category_dirs:
        image_sources.append(("category", cat_dir.name, find_image(cat_dir, "category")))
        subdirs = sorted(p for p in cat_dir.iterdir() if p.is_dir())
        for sub_dir in subdirs:
            image_sources.append(("subcategory", f"{cat_dir.name}/{sub_dir.name}", find_image(sub_dir, "subcategory")))
    for item in manifest:
        folder = brands_root / item["name"]
        logo = None
        if folder.is_dir():
            imgs = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower().lstrip(".") in ALLOWED and f.name.lower() != "brand_folder_manifest.json"]
            logo = sorted(imgs)[0] if imgs else None
        image_sources.append(("brand", item["name"], logo))

    missing_base_images = [x for x in image_sources if x[0] != "brand" and x[2] is None]
    missing_logos = [x for x in image_sources if x[0] == "brand" and x[2] is None]
    if missing_base_images:
        raise SystemExit("Missing required category/subcategory images:\n" + "\n".join(f"- {x[1]}" for x in missing_base_images))

    if args.dry_run:
        print(f"DRY RUN: {len(category_dirs)} categories ready")
        print(f"DRY RUN: {sum(1 for x in image_sources if x[0] == 'subcategory')} subcategory images ready")
        print(f"DRY RUN: {len(manifest)} canonical brands ready")
        print(f"DRY RUN: {len(missing_logos)} brand logos currently missing (allowed; logo_key remains NULL)")
        return

    from app import create_app, db
    from app.models import Brand, Category, Subcategory
    from app.services.image_service import process_image
    from app.services.storage_service import StorageService

    app = create_app()
    with app.app_context():
        storage = StorageService()
        category_map = {}
        subcategory_map = {}

        for cat_dir in category_dirs:
            name = cat_dir.name
            slug = "-".join(name.lower().split())
            category = Category.query.filter(db.func.lower(Category.name) == name.lower()).first()
            if not category:
                category = Category(name=name, slug=slug, is_active=True)
                db.session.add(category)
                db.session.flush()
            else:
                category.name = name
                category.slug = slug
                category.is_active = True

            image = find_image(cat_dir, "category")
            old_key = category.image_key
            category.image_key = process_and_save(image, storage, "categories")
            if old_key and old_key != category.image_key:
                storage.delete(old_key)
            category_map[name] = category

        db.session.flush()

        for cat_dir in category_dirs:
            category = category_map[cat_dir.name]
            for sub_dir in sorted(p for p in cat_dir.iterdir() if p.is_dir()):
                name = sub_dir.name
                slug = "-".join(name.lower().split())
                sub = Subcategory.query.filter(
                    Subcategory.category_id == category.id,
                    db.func.lower(Subcategory.name) == name.lower(),
                ).first()
                if not sub:
                    sub = Subcategory(category_id=category.id, name=name, slug=slug, is_active=True)
                    db.session.add(sub)
                    db.session.flush()
                else:
                    sub.name = name
                    sub.slug = slug
                    sub.is_active = True
                    sub.category_id = category.id

                image = find_image(sub_dir, "subcategory")
                old_key = sub.image_key
                sub.image_key = process_and_save(image, storage, "subcategories")
                if old_key and old_key != sub.image_key:
                    storage.delete(old_key)
                subcategory_map[(category.name, sub.name)] = sub

        db.session.flush()

        brand_map = {}
        for item in manifest:
            name = item["name"].strip()
            slug = "-".join(name.lower().split())
            brand = Brand.query.filter(db.func.lower(Brand.name) == name.lower()).first()
            if not brand:
                brand = Brand(name=name, slug=slug, is_active=True)
                db.session.add(brand)
                db.session.flush()
            else:
                brand.name = name
                brand.slug = slug
                brand.is_active = True

            folder = brands_root / name
            imgs = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower().lstrip(".") in ALLOWED]
            if imgs:
                logo = sorted(imgs)[0]
                old_key = brand.logo_key
                brand.logo_key = process_and_save(logo, storage, "brands")
                if old_key and old_key != brand.logo_key:
                    storage.delete(old_key)
            brand_map[name.casefold()] = brand

        db.session.commit()

        print("\nBASE SETUP SUCCESS")
        print(f"Categories:    {len(category_map)}")
        print(f"Subcategories: {len(subcategory_map)}")
        print(f"Brands:        {len(brand_map)}")
        print(f"Missing logos: {len(missing_logos)} (logo_key left NULL until verified logos are supplied)")


if __name__ == "__main__":
    main()
