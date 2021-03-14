# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Product Serial Number",
    "version": "13.0.0.0.0",
    "category": "Custom",
    "author": "Comunitea",
    "license": "AGPL-3",
    "summary": "Manage product flow by unique serial number",
    "depends": [
        "product",
        "stock",
        "sale_order_lot_selection",
        "purchase",
        "point_of_sale",
        "stock_picking_auto_create_lot",
        "base_multi_image",
        "purchase_operating_unit",
        "stock_move_location",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/product_data.xml",
        "data/cron.xml",
        "wizard/transfer_lot_wzd_view.xml",
        "views/product_view.xml",
        "views/stock_production_lot_view.xml",
        "views/purchase_view.xml",
        "views/sale_view.xml",
        "views/location_info_view.xml",
        "views/operating_unit_view.xml",
        "views/stock_location_view.xml",
    ],
    "installable": True,
}
