from odoo import fields, models


class ProductTemplate(models.Model):
    """Adds Hepsiburada-specific mapping fields to product templates."""

    _inherit = 'product.template'

    # ── Category & merchant ─────────────────────────────────────────────────
    hb_category_id = fields.Integer(
        string='HB Category ID',
        help='Hepsiburada category ID (integer), e.g. 18021982.',
    )
    hb_variant_group_id = fields.Char(
        string='HB Variant Group ID',
        help='VaryantGroupID sent to Hepsiburada, e.g. "Hepsiburada0".',
    )

    # ── Product attributes ───────────────────────────────────────────────────
    hb_brand = fields.Char(
        string='HB Brand (Marka)',
        help='Brand name as recognised by Hepsiburada.',
    )
    hb_warranty = fields.Integer(
        string='Warranty (months)',
        default=24,
        help='GarantiSuresi – warranty period in months.',
    )
    hb_weight = fields.Char(
        string='Weight (kg)',
        help='Weight in kg as a string (e.g. "1"). Falls back to product weight when empty.',
    )
    hb_tax_vat_rate = fields.Char(
        string='VAT Rate (%)',
        help='tax_vat_rate as expected by Hepsiburada, e.g. "5" or "18".',
    )

    # ── Variant properties ───────────────────────────────────────────────────
    hb_color_variant = fields.Char(
        string='Colour Variant (renk)',
        help='renk_variant_property value, e.g. "Siyah".',
    )
    hb_size_variant = fields.Char(
        string='Size Variant (ebat)',
        help='ebatlar_variant_property value, e.g. "Büyük Ebat".',
    )

    # ── Media ────────────────────────────────────────────────────────────────
    hb_image1_url = fields.Char(string='Image 1 URL')
    hb_image2_url = fields.Char(string='Image 2 URL')
    hb_image3_url = fields.Char(string='Image 3 URL')
    hb_image4_url = fields.Char(string='Image 4 URL')
    hb_image5_url = fields.Char(string='Image 5 URL')
    hb_video1_url = fields.Char(string='Video 1 URL')


class ProductProduct(models.Model):
    """Adds Hepsiburada SKU / barcode override at the variant level."""

    _inherit = 'product.product'

    hb_merchant_sku = fields.Char(
        string='HB Merchant SKU',
        help='merchantSku override. Falls back to Internal Reference (default_code) when empty.',
    )
    hb_barcode = fields.Char(
        string='HB Barcode',
        help='Barcode override for Hepsiburada. Falls back to product barcode when empty.',
    )
