#!/usr/bin/env python3
"""
ShopEase complete inventory importer.
Imports every product.json plus every real product image from ShopEase_Inventry.

Run from the ShopEase project root:
    python import_complete_inventory.py --inventory "../ShopEase_Inventry"

Safe to rerun:
- Products are matched by SKU.
- Variants are reconciled by name while preserving existing ProductSize IDs.
- Existing product images are replaced with the source gallery after the product
  is reconciled, so a partial/failed earlier import can be repaired by rerunning.
- Non-master brands are deliberately left unassigned (brand_id=NULL).
"""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

from sqlalchemy import func, text

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

ALLOWED = {"jpg", "jpeg", "png", "webp"}


class _NamedFile:
    def __init__(self, fh, name):
        self._fh = fh
        self.filename = name

    def seek(self, *args):
        return self._fh.seek(*args)

    def read(self, *args):
        return self._fh.read(*args)


def parse_args():
    p = argparse.ArgumentParser(description="Import complete ShopEase product inventory.")
    p.add_argument("--inventory", default=str(PROJECT_ROOT.parent / "ShopEase_Inventry"))
    p.add_argument("--dry-run", action="store_true", help="Validate all product data/images without changing the DB/files.")
    return p.parse_args()


def slug_for(name: str) -> str:
    return "-".join(name.lower().split())


def process_and_save(path: Path, storage, folder: str) -> str:
    with path.open("rb") as fh:
        output, filename = process_image(_NamedFile(fh, path.name))
    return storage.save(output, folder, filename)


def canonical_brand_map(brands):
    return {b.name.strip().casefold(): b for b in brands}


def all_product_dirs(root: Path):
    return sorted(p.parent for p in root.rglob("product.json"))


def validate_inventory(inventory: Path):
    root = inventory
    product_dirs = all_product_dirs(root)
    if len(product_dirs) != 275:
        raise ValueError(f"Expected 275 product folders, found {len(product_dirs)}")

    seen_skus = set()
    errors = []
    image_count = 0
    variant_count = 0
    for product_dir in product_dirs:
        jf = product_dir / "product.json"
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{jf}: invalid JSON: {exc}")
            continue

        required = ["name", "sku", "category", "subcategory", "price", "stock_quantity", "description", "specifications", "has_sizes"]
        for key in required:
            if key not in data:
                errors.append(f"{jf}: missing field {key}")
        sku = str(data.get("sku", ""))
        if sku in seen_skus:
            errors.append(f"Duplicate SKU: {sku}")
        seen_skus.add(sku)

        imgs = sorted(f for f in product_dir.iterdir() if f.is_file() and f.suffix.lower().lstrip(".") in ALLOWED and f.name != "product.json")
        if not imgs:
            errors.append(f"{product_dir}: no product images")
        image_count += len(imgs)
        variant_count += len(data.get("variants") or [])

        if data.get("has_sizes") and not isinstance(data.get("variants"), list):
            errors.append(f"{jf}: has_sizes=true but variants is missing or not a list")
        if not isinstance(data.get("specifications"), dict):
            errors.append(f"{jf}: specifications is not an object")

    return product_dirs, image_count, variant_count, errors


def main():
    args = parse_args()
    inventory = Path(args.inventory).expanduser().resolve()
    if not inventory.is_dir():
        raise SystemExit(f"Inventory directory not found: {inventory}")

    product_dirs, image_count, variant_count, errors = validate_inventory(inventory)
    if errors:
        print("VALIDATION FAILED")
        for e in errors[:100]:
            print("-", e)
        if len(errors) > 100:
            print(f"... and {len(errors)-100} more")
        raise SystemExit(1)

    if args.dry_run:
        print("DRY RUN VALIDATION SUCCESS")
        print(f"Products: {len(product_dirs)}")
        print(f"Images:   {image_count}")
        print(f"Variants: {variant_count}")
        return

    from app import create_app, db
    from app.models import Brand, Category, Product, ProductImage, ProductSize, Subcategory
    from app.services.image_service import process_image
    from app.services.storage_service import StorageService

    app = create_app()
    with app.app_context():
        categories = {c.name.casefold(): c for c in Category.query.all()}
        subcategories = {(s.category_id, s.name.casefold()): s for s in Subcategory.query.all()}
        brands = canonical_brand_map(Brand.query.all())
        storage = StorageService()

        if len(categories) < 4:
            raise SystemExit("Base setup is incomplete: fewer than 4 categories exist. Run setup_shopease_base.py first.")
        if len(brands) < 54:
            raise SystemExit("Base setup is incomplete: fewer than 54 brands exist. Run setup_shopease_base.py first.")

        imported = 0
        updated = 0
        unmapped_brand_count = 0
        imported_images = 0
        imported_variants = 0
        failed = []
        unmapped_examples = []

        for index, product_dir in enumerate(product_dirs, start=1):
            jf = product_dir / "product.json"
            try:
                data = json.loads(jf.read_text(encoding="utf-8"))
                category = categories.get(str(data["category"]).strip().casefold())
                if not category:
                    raise ValueError(f"Category not found: {data['category']}")
                subcategory = subcategories.get((category.id, str(data["subcategory"]).strip().casefold()))
                if not subcategory:
                    raise ValueError(f"Subcategory not found under {category.name}: {data['subcategory']}")

                brand_value = str(data.get("brand", "")).strip()
                brand = brands.get(brand_value.casefold()) if brand_value else None
                if brand_value and not brand:
                    unmapped_brand_count += 1
                    if len(unmapped_examples) < 20:
                        unmapped_examples.append(f"{data['sku']} -> {brand_value}")

                sku = str(data["sku"]).strip()
                product = Product.query.filter_by(sku=sku).first()
                is_new = product is None
                if is_new:
                    product = Product(sku=sku)
                    db.session.add(product)

                product.category_id = category.id
                product.subcategory_id = subcategory.id
                product.brand_id = brand.id if brand else None
                product.name = str(data["name"]).strip()
                product.slug = slug_for(product.name)
                # Ensure uniqueness when a different product already owns the natural slug.
                conflict = Product.query.filter(Product.slug == product.slug, Product.sku != sku).first()
                if conflict:
                    base = product.slug
                    n = 2
                    while Product.query.filter(Product.slug == f"{base}-{n}", Product.sku != sku).first():
                        n += 1
                    product.slug = f"{base}-{n}"
                product.description = data.get("description") or None
                product.specifications = data.get("specifications") or None
                product.price = Decimal(str(data["price"]))
                variants = data.get("variants") or []
                product.stock_quantity = sum(int(v.get("quantity", 0)) for v in variants) if data.get("has_sizes") else int(data.get("stock_quantity", 0))
                product.featured = bool(data.get("featured", False))
                product.is_active = bool(data.get("is_active", True))
                db.session.flush()

                # Reconcile variants by name, preserving IDs for existing variants.
                existing = {v.size: v for v in product.sizes}
                submitted_names = set()
                for v in variants:
                    name = str(v.get("name", "")).strip()
                    if not name:
                        raise ValueError("Variant has empty name")
                    submitted_names.add(name)
                    row = existing.get(name)
                    if row is None:
                        row = ProductSize(product_id=product.id, size=name)
                        db.session.add(row)
                    row.size = name
                    row.price = Decimal(str(v.get("price", data["price"])))
                    row.quantity = int(v.get("quantity", 0))
                    row.description = v.get("description") or None
                    row.specifications = v.get("specifications") or None
                    imported_variants += 1

                db.session.flush()

                # Remove obsolete variants only when they are not used by carts.
                for row in list(product.sizes):
                    if row.size in submitted_names:
                        continue
                    usage = db.session.execute(
                        text("SELECT COUNT(*) FROM cart_items WHERE product_size_id = :id"),
                        {"id": row.id},
                    ).scalar_one()
                    if usage == 0:
                        db.session.delete(row)

                # Replace image gallery with the source-of-truth gallery.
                old_images = list(product.images)
                for old in old_images:
                    storage.delete(old.image_key)
                    db.session.delete(old)
                db.session.flush()

                imgs = sorted(f for f in product_dir.iterdir() if f.is_file() and f.suffix.lower().lstrip(".") in ALLOWED and f.name != "product.json")
                if not imgs:
                    raise ValueError("No product images found")
                for order, img_path in enumerate(imgs):
                    key = process_and_save(img_path, storage, "products")
                    db.session.add(ProductImage(
                        product_id=product.id,
                        image_key=key,
                        alt_text=product.name,
                        display_order=order,
                        is_primary=(order == 0),
                    ))
                    imported_images += 1

                db.session.commit()
                if is_new:
                    imported += 1
                else:
                    updated += 1

                if index % 10 == 0 or index == len(product_dirs):
                    print(f"[{index}/{len(product_dirs)}] processed | new={imported} updated={updated} images={imported_images}")

            except Exception as exc:
                db.session.rollback()
                failed.append((jf, str(exc)))
                print(f"FAILED [{index}/{len(product_dirs)}] {jf}: {exc}")

        print("\nIMPORT COMPLETE")
        print(f"New products:       {imported}")
        print(f"Updated products:   {updated}")
        print(f"Product images:     {imported_images}")
        print(f"Variant rows seen:  {imported_variants}")
        print(f"Unmapped brands:    {unmapped_brand_count}")
        if unmapped_examples:
            print("Unmapped examples:")
            for x in unmapped_examples:
                print("  -", x)
        print(f"Failures:            {len(failed)}")
        if failed:
            print("Failure list:")
            for path, msg in failed:
                print(f"  - {path}: {msg}")
            raise SystemExit(2)


if __name__ == "__main__":
    main()
