odoo.define("pos_custom_cc.BarcodeReader", function (require) {
    "use strict";

    var BarcodeReader = require("point_of_sale.BarcodeReader");

    // BarcodeReader.include({
    //     scan: function (code) {
    //         return this._super(code);
    //     },
    // });

    return BarcodeReader;
});
