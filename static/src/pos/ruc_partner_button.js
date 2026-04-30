/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PartnerList } from "@point_of_sale/app/screens/partner_list/partner_list";

patch(PartnerList.prototype, {
    async onClickRucSearch() {
        const numero = prompt("Ingrese DNI o RUC");

        if (!numero) {
            return;
        }

        console.log("Documento ingresado:", numero);
    },
});