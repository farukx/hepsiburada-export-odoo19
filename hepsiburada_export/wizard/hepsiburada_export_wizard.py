import base64
import io
import json
import logging

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

_ENDPOINT_VERSION = '1'
_DEFAULT_WARRANTY_MONTHS = 24


def _get_param(env, key, default=''):
    return env['ir.config_parameter'].sudo().get_param(key) or default


class HepsiburadaExportWizard(models.TransientModel):
    """Wizard: select products, build JSON payload, upload to Hepsiburada."""

    _name = 'hepsiburada.export.wizard'
    _description = 'Hepsiburada Product Export'

    # ── Product selection ────────────────────────────────────────────────────
    product_ids = fields.Many2many(
        'product.template',
        string='Products to Export',
        required=True,
    )

    # ── Result display ───────────────────────────────────────────────────────
    state = fields.Selection(
        [('draft', 'Draft'), ('done', 'Done'), ('error', 'Error')],
        default='draft',
        readonly=True,
    )
    tracking_code = fields.Char(string='Tracking Code', readonly=True)
    response_message = fields.Text(string='API Response', readonly=True)

    # ── JSON preview ─────────────────────────────────────────────────────────
    json_preview = fields.Text(
        string='JSON Preview',
        readonly=True,
        help='Preview of the payload that will be sent to Hepsiburada.',
    )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_credentials(self):
        env = self.env
        username = _get_param(env, 'hepsiburada_export.username')
        password = _get_param(env, 'hepsiburada_export.password')
        merchant_id = _get_param(env, 'hepsiburada_export.merchant_id')
        endpoint_url = _get_param(
            env,
            'hepsiburada_export.endpoint_url',
            'https://mpop.hepsiburada.com/product/api/products/import',
        )
        if not username or not password:
            raise UserError(
                _(
                    'Hepsiburada credentials are not configured. '
                    'Go to Settings → Hepsiburada and fill in username & password.'
                )
            )
        if not merchant_id:
            raise UserError(
                _(
                    'Hepsiburada Merchant ID is not configured. '
                    'Go to Settings → Hepsiburada and enter your merchant UUID.'
                )
            )
        return username, password, merchant_id, endpoint_url

    def _build_auth_header(self, username, password):
        token = base64.b64encode(f'{username}:{password}'.encode()).decode()
        return f'Basic {token}'

    def _format_price(self, value):
        """Return price as Turkish decimal string (comma as decimal separator)."""
        return f'{value:.2f}'.replace('.', ',')

    def _get_stock(self, variant):
        """Return available stock qty for a variant as string."""
        try:
            qty = variant.with_context(warehouse=False).qty_available
        except Exception:
            qty = 0.0
        return str(int(qty))

    def _build_payload(self, merchant_id):
        """Build and return the list of product dicts for the Hepsiburada API."""
        payload = []
        for tmpl in self.product_ids:
            variants = tmpl.product_variant_ids
            for variant in variants:
                merchant_sku = variant.hb_merchant_sku or variant.default_code or ''
                barcode = variant.hb_barcode or variant.barcode or ''
                weight = tmpl.hb_weight or (
                    str(tmpl.weight) if tmpl.weight else ''
                )

                attributes = {
                    'merchantSku': merchant_sku,
                    'VaryantGroupID': tmpl.hb_variant_group_id or '',
                    'Barcode': barcode,
                    'UrunAdi': tmpl.name or '',
                    'UrunAciklamasi': (
                        tmpl.description_sale
                        or tmpl.description
                        or ''
                    ),
                    'Marka': tmpl.hb_brand or '',
                    'GarantiSuresi': tmpl.hb_warranty or _DEFAULT_WARRANTY_MONTHS,
                    'kg': weight,
                    'tax_vat_rate': tmpl.hb_tax_vat_rate or '',
                    'price': self._format_price(variant.lst_price),
                    'stock': self._get_stock(variant),
                }

                # Images – only include non-empty URLs
                for i, url_field in enumerate(
                    [
                        'hb_image1_url',
                        'hb_image2_url',
                        'hb_image3_url',
                        'hb_image4_url',
                        'hb_image5_url',
                    ],
                    start=1,
                ):
                    url = getattr(tmpl, url_field, '') or ''
                    if url:
                        attributes[f'Image{i}'] = url

                if tmpl.hb_video1_url:
                    attributes['Video1'] = tmpl.hb_video1_url

                if tmpl.hb_color_variant:
                    attributes['renk_variant_property'] = tmpl.hb_color_variant
                if tmpl.hb_size_variant:
                    attributes['ebatlar_variant_property'] = tmpl.hb_size_variant

                payload.append(
                    {
                        'categoryId': tmpl.hb_category_id or 0,
                        'merchant': merchant_id,
                        'attributes': attributes,
                    }
                )
        return payload

    # ── Actions ───────────────────────────────────────────────────────────────

    def action_preview_json(self):
        """Populate the JSON preview field without uploading."""
        self.ensure_one()
        _, _, merchant_id, _ = self._get_credentials()
        payload = self._build_payload(merchant_id)
        self.json_preview = json.dumps(payload, ensure_ascii=False, indent=2)
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_export(self):
        """Build JSON, upload to Hepsiburada and store the tracking code."""
        self.ensure_one()
        username, password, merchant_id, endpoint_url = self._get_credentials()
        payload = self._build_payload(merchant_id)

        json_bytes = json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8')
        self.json_preview = json_bytes.decode('utf-8')

        auth_header = self._build_auth_header(username, password)
        url = f'{endpoint_url.rstrip("/")}?version={_ENDPOINT_VERSION}'

        try:
            response = requests.post(
                url,
                headers={
                    'accept': 'application/json',
                    'authorization': auth_header,
                },
                files={'file': ('integrator.json', io.BytesIO(json_bytes), 'application/json')},
                timeout=30,
            )
        except requests.exceptions.RequestException as exc:
            self.write({'state': 'error', 'response_message': str(exc)})
            raise UserError(_('Hepsiburada API request failed: %s') % exc) from exc

        _logger.info(
            'Hepsiburada export response: status=%s length=%s',
            response.status_code,
            len(response.content),
        )

        try:
            resp_data = response.json()
        except ValueError:
            resp_data = {}

        tracking_code = (
            resp_data.get('trackingId')
            or resp_data.get('tracking_id')
            or resp_data.get('data', {}).get('trackingId', '')
            if isinstance(resp_data, dict)
            else ''
        )

        if response.status_code in (200, 201, 202):
            self.write(
                {
                    'state': 'done',
                    'tracking_code': tracking_code,
                    'response_message': response.text,
                }
            )
        else:
            self.write(
                {
                    'state': 'error',
                    'response_message': response.text,
                }
            )
            raise UserError(
                _('Hepsiburada returned error %s:\n%s')
                % (response.status_code, response.text)
            )

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_download_json(self):
        """Return the built JSON as a downloadable attachment."""
        self.ensure_one()
        _, _, merchant_id, _ = self._get_credentials()
        payload = self._build_payload(merchant_id)
        json_bytes = json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8')

        attachment = self.env['ir.attachment'].create(
            {
                'name': 'hepsiburada_export.json',
                'type': 'binary',
                'datas': base64.b64encode(json_bytes),
                'mimetype': 'application/json',
            }
        )
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
