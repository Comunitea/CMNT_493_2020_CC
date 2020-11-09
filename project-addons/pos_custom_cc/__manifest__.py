# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Pos Custom CC",
    "version": "13.0.0.0.0",
    "category": "Point Of Sale",
    "summary": """
        Point of Sale - Cutomizations Cash COnverters""",
    "author": "Comunitea",
    "website": "https://comunitea.com",
    "license": "AGPL-3",
    "depends": [
        "point_of_sale",
    ],
    "data": [
        "views/assets.xml",
    ],
    "qweb": [
        "static/src/xml/pos_custom_cc.xml",
    ],
}
