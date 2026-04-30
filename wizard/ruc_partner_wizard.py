from odoo import models, fields
from odoo.exceptions import UserError
import requests


class RucPartnerWizard(models.TransientModel):
    _name = "ruc.partner.wizard"
    _description = "Buscar contacto por DNI o RUC"

    document_number = fields.Char(string="DNI/RUC", required=True)

    def action_search_document(self):
        self.ensure_one()

        numero = (self.document_number or "").strip()

        if not numero:
            raise UserError("Ingrese DNI o RUC.")

        if len(numero) not in (8, 11):
            raise UserError("El documento debe tener 8 dígitos para DNI o 11 para RUC.")

        token = (
            self.env["ir.config_parameter"].sudo().get_param("ruc_partner_pe.api_token")
        )

        if not token:
            raise UserError("Configure primero el token en Ajustes.")

        if len(numero) == 8:
            url = f"https://dniruc.apisperu.com/api/v1/dni/{numero}?token={token}"
        else:
            url = f"https://dniruc.apisperu.com/api/v1/ruc/{numero}?token={token}"

        try:
            response = requests.get(url, timeout=10)
            data = response.json()
        except Exception as e:
            raise UserError(f"Error consultando API: {str(e)}")

        if len(numero) == 8:
            nombre = (
                f"{data.get('nombres', '')} "
                f"{data.get('apellidoPaterno', '')} "
                f"{data.get('apellidoMaterno', '')}"
            ).strip()

            if not nombre:
                raise UserError("No se encontró información para ese DNI.")

            values = {
                "name": nombre,
                "vat": numero,
                "company_type": "person",
            }

        else:
            razon_social = data.get("razonSocial")
            direccion = data.get("direccion")

            if not razon_social:
                raise UserError("No se encontró información para ese RUC.")

            values = {
                "name": razon_social,
                "vat": numero,
                "street": direccion,
                "company_type": "company",
            }

        partner = self.env["res.partner"].create(values)

        return {
            "type": "ir.actions.act_window",
            "name": "Contacto",
            "res_model": "res.partner",
            "res_id": partner.id,
            "view_mode": "form",
            "target": "current",
        }
