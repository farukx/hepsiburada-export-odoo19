from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Extends general settings to hold Hepsiburada API credentials."""

    _inherit = 'res.config.settings'

    hb_username = fields.Char(
        string='Hepsiburada Username',
        config_parameter='hepsiburada_export.username',
    )
    hb_password = fields.Char(
        string='Hepsiburada Password',
        config_parameter='hepsiburada_export.password',
    )
    hb_merchant_id = fields.Char(
        string='Merchant ID (UUID)',
        config_parameter='hepsiburada_export.merchant_id',
        help='Your Hepsiburada merchant UUID, e.g. 6fc6d90d-ee1d-4372-b3a6-264b1275e9ff',
    )
    hb_endpoint_url = fields.Char(
        string='Import Endpoint URL',
        config_parameter='hepsiburada_export.endpoint_url',
        default='https://mpop.hepsiburada.com/product/api/products/import',
        help='Full URL for the Hepsiburada product import endpoint (without query string).',
    )
