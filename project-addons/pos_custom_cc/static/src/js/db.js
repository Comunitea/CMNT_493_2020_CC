odoo.define("pos_custom_cc.db", function (require) {
    "use strict";

    var PosDB = require("point_of_sale.DB");

    PosDB.include({
        // Copiado de pos_empty_home
        get_product_by_category: function (category_id) {
            if (category_id !== 0) {
                return this._super(category_id);
            }
            return [];
        },
    });

    return PosDB;
});
