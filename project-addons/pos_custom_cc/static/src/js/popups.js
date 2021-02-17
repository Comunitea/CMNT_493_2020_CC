odoo.define("pos_custom_cc.popups", function (require) {
    "use strict";

    var pos_popup = require("point_of_sale.popups");
    var gui = require("point_of_sale.gui");

    var SelectLotPopupWidget = pos_popup.extend({
        template: "SelectLotPopupWidget",
        init: function (parent, args) {
            this._super(parent, args);
            this.options = {};
        },
        show: function (options) {
            this._super(options);
        },

        add_serial_number_product: function () {
            var selectedOrder = this.pos.get("selectedOrder");
            var search_lot_name = $("#existing_serial_number").val();
            selectedOrder.add_product_by_lot(search_lot_name);
        },
        renderElement: function () {
            var self = this;
            this._super();
            this.$("#add_serial_number").click(function () {
                self.add_serial_number_product();
                self.gui.close_popup();
            });
        },
    });
    gui.define_popup({name: "select-lot", widget: SelectLotPopupWidget});
});
