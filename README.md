# Hepsiburada Export – Odoo 19 Module

An Odoo 19 application that exports products from Odoo to the
[Hepsiburada](https://www.hepsiburada.com) marketplace via the official
product-import API.

---

## Features

- **Per-product Hepsiburada tab** on `product.template` for mapping
  `categoryId`, brand, warranty, weight, VAT rate, variant properties and up to
  5 image URLs + 1 video URL.
- **Per-variant fields** (`hb_merchant_sku`, `hb_barcode`) on `product.product`.
- **Export wizard** – select one or many products, preview the JSON payload,
  upload it to Hepsiburada and retrieve the **tracking code**.
- **Download JSON** button – download `hepsiburada_export.json` without sending.
- **Settings page** inside Odoo General Settings for API credentials and
  endpoint URL.

---

## Installation

### 1. Copy the module

Place the `hepsiburada_export/` directory inside your Odoo add-ons path, e.g.:

```bash
cp -r hepsiburada_export /opt/odoo/custom-addons/
```

### 2. Update the add-ons list

In Odoo:  `Apps → Update Apps List`

### 3. Install

Search for **Hepsiburada Export** and click **Install**.

---

## Configuration

1. Go to **Settings → (scroll to) Hepsiburada** (or navigate directly from the
   *Hepsiburada → Settings* menu).
2. Fill in:
   | Field | Description |
   |---|---|
   | **Username** | Your Hepsiburada API username |
   | **Password** | Your Hepsiburada API password |
   | **Merchant ID** | Your merchant UUID (e.g. `6fc6d90d-ee1d-4372-b3a6-264b1275e9ff`) |
   | **Import Endpoint URL** | Default: `https://mpop.hepsiburada.com/product/api/products/import` |
3. Click **Save**.

> **Tip:** Use the SIT (staging) endpoint while testing:
> `https://mpop-sit.hepsiburada.com/product/api/products/import`

---

## Mapping products

Open any **product.template** form view and navigate to the **Hepsiburada** tab.

| Odoo field | Hepsiburada attribute |
|---|---|
| HB Category ID | `categoryId` |
| HB Variant Group ID | `VaryantGroupID` |
| HB Brand (Marka) | `Marka` |
| Warranty (months) | `GarantiSuresi` |
| Weight (kg) | `kg` |
| VAT Rate (%) | `tax_vat_rate` |
| Colour Variant | `renk_variant_property` |
| Size Variant | `ebatlar_variant_property` |
| Image 1–5 URL | `Image1`–`Image5` |
| Video 1 URL | `Video1` |

For each **product variant** (`product.product`) you can additionally override:

| Odoo field | Hepsiburada attribute |
|---|---|
| HB Merchant SKU | `merchantSku` (fallback: Internal Reference) |
| HB Barcode | `Barcode` (fallback: product barcode) |

---

## Exporting

1. Go to **Hepsiburada → Export Products**.
2. Select one or more products in the **Products to Export** field.
3. Click **Preview JSON** to inspect the payload without sending it.
4. Click **Export to Hepsiburada** to upload and receive the tracking code.
5. The **Tracking Code** is shown on the same form after a successful upload.

---

## API payload shape

The module builds a JSON array matching the structure required by Hepsiburada:

```json
[
  {
    "categoryId": 18021982,
    "merchant": "6fc6d90d-ee1d-4372-b3a6-264b1275e9ff",
    "attributes": {
      "merchantSku": "SAMPLE-SKU-INT-0",
      "VaryantGroupID": "Hepsiburada0",
      "Barcode": "1234567891234",
      "UrunAdi": "Product Name",
      "UrunAciklamasi": "Product description text.",
      "Marka": "Nike",
      "GarantiSuresi": 24,
      "kg": "1",
      "tax_vat_rate": "5",
      "price": "130,50",
      "stock": "13",
      "Image1": "https://...",
      "Video1": "https://...",
      "renk_variant_property": "Siyah",
      "ebatlar_variant_property": "Büyük Ebat"
    }
  }
]
```

The file is uploaded as `multipart/form-data` with the field name `file`
(filename `integrator.json`) — exactly as the Hepsiburada API expects.

---

## License

LGPL-3