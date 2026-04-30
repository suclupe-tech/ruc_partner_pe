from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ruc_api_token = fields.Char(
        string="Token API RUC", config_parameter="ruc_partner_pe.api_token"
    )
