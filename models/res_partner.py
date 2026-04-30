from odoo import models
from odoo.exceptions import UserError
import requests


class ResPartner(models.Model):
    _inherit = "res.partner"

    def action_consultar_ruc(self):
        self.ensure_one()

        if not self.vat:
            raise UserError("Ingrese DNI o RUC")

        if not self.name:
            self.name = "CONSULTANDO DOCUMENTO..."

        token = (
            self.env["ir.config_parameter"].sudo().get_param("ruc_partner_pe.api_token")
        )

        if not token:
            raise UserError("Configure el token primero")

        numero = self.vat.strip()

        if len(numero) == 8:
            url = f"https://dniruc.apisperu.com/api/v1/dni/{numero}?token={token}"

        elif len(numero) == 11:
            url = f"https://dniruc.apisperu.com/api/v1/ruc/{numero}?token={token}"

        else:
            raise UserError("Documento inválido")

        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            if len(numero) == 8:
                nombre = (
                    f"{data.get('nombres','')} "
                    f"{data.get('apellidoPaterno','')} "
                    f"{data.get('apellidoMaterno','')}"
                ).strip()

                self.name = nombre

            else:
                self.name = data.get("razonSocial")
                self.street = data.get("direccion")

        except Exception as e:
            raise UserError(f"Error: {str(e)}")
