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
        'product',
        'stock',
        'sale_order_lot_selection',
        'purchase',
        'stock_picking_auto_create_lot',
        'base_multi_image'
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/purchase_view.xml',
    ],
    "installable": True,
}