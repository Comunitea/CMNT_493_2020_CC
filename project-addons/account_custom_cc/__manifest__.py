# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Account Custom CC",
    "version": "13.0.0.0.0",
    "category": "Custom",
    "author": "Comunitea",
    "license": "AGPL-3",
    "summary": "Manage account related flow",
    "depends": [
        "product",
        "sale",
        "purchase",
        "account_tax_python",
        "product_serial_number",
        "product_serial_number",
        "pos_operating_unit_cc",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/account_tax_data.xml",
        "wizard/purchase_invoice_wzd.xml",
        "views/purchase_view.xml",
        "views/product_view.xml",
        "views/operating_unit_view.xml",
        "views/account_tax_view.xml",
        "views/fiscal_position_view.xml",
        "views/account_move_view.xml",
        "views/stock_production_lot_view.xml",
    ],
    "installable": True,
}
