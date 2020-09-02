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
        'product',
        'stock'
    ],
    "data": [
        "views/product_view.xml",
    ],
    "installable": True,
}