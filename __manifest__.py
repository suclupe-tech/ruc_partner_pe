{
    "name": "RUC Partner Peru",
    "version": "1.0",
    "summary": "Consulta RUC para contactos",
    "author": "Detalles Textiles",
    "category": "Contacts",
    "depends": ["base", "contacts", "point_of_sale"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "ruc_partner_pe/static/src/pos/ruc_partner_button.js",
            
        ],
    },
    "installable": True,
    "application": False,
}
