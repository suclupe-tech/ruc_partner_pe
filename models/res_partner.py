from odoo import models, api
import requests
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.onchange("vat")
    def _onchange_vat_consultar_documento(self):
        if not self.vat:
            return

        numero = self.vat.strip()

        if not numero.isdigit():
            return {
                "warning": {
                    "title": "Número inválido",
                    "message": "El número de documento debe contener solo numeros.",
                }
            }

        if len(numero) not in (8, 11):
            return {
                "warning": {
                    "title": "Número inválido",
                    "message": "El número de documento debe tener 8 dígitos para DNI o 11 dígitos para RUC.",
                }
            }

        existing = self.env["res.partner"].search(
            [("vat", "=", numero), ("id", "!=", self.id)], limit=1
        )
        if existing:
            return {
                "warning": {
                    "title": "Cliente existente",
                    "message": f"Se usara el cliente: {existing.name}.",
                },
                "value": {"id": existing.id},
            }

        token = (
            self.env["ir.config_parameter"].sudo().get_param("ruc_partner_pe.api_token")
        )

        if not token:
            return

        if len(numero) == 8:
            url = f"https://dniruc.apisperu.com/api/v1/dni/{numero}?token={token}"
        else:
            url = f"https://dniruc.apisperu.com/api/v1/ruc/{numero}?token={token}"

        try:
            response = requests.get(url, timeout=10)
            data = response.json()

        except Exception:
            return

        if len(numero) == 8:
            nombre = (
                data.get("nombre_completo")
                or data.get("nombreCompleto")
                or (
                    f"{data.get('nombres', '')}"
                    f"{data.get('apellidoPaterno', '')}"
                    f"{data.get('apellidoMaterno', '')}"
                )
            ).strip()

            if nombre:
                self.name = nombre
                self.company_type = "person"

        else:
            razon_social = data.get("razonSocial") or data.get("razon_social")
            direccion = (
                data.get("direccion")
                or data.get("direccion_completa")
                or data.get("direccionCompleta")
            )

            if razon_social:
                self.name = razon_social
                self.street = direccion
                self.company_type = "company"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vat = vals.get("vat")

            if vat:
                vat = vat.strip()

                existing = self.search(
                    [
                        ("vat", "=", vat),
                        ("active", "in", [True, False]),
                    ],
                    limit=1,
                )

                if existing:
                    raise ValidationError(
                        f"Ya existe un cliente con este documento: {existing.name}"
                    )

                vals["vat"] = vat

        return super().create(vals_list)

    def write(self, vals):
        vat = vals.get("vat")

        if vat:
            for rec in self:
                existing = self.search(
                    [("vat", "=", vat), ("id", "!=", rec.id)], limit=1
                )
                if existing:
                    raise ValidationError(
                        f"Este documento ya está asignado a: {existing.name}"
                    )

        return super().write(vals)
