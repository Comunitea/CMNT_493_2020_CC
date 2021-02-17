odoo.define("pos_custom_cc.screens", function (require) {
    "use strict";

    var screens = require("point_of_sale.screens");

    var core = require("web.core");
    var _t = core._t;

    // Copiado de pos_empty_home.
    // Del módulo hide de la 12, ocultar productos para la selección
    screens.ProductListWidget.include({
        set_product_list: function (product_list) {
            this._super(product_list);
            if (product_list.length) {
                $(this.el.querySelector(".product-list-empty-home")).hide();
            } else {
                $(this.el.querySelector(".product-list-empty-home")).show();
            }
        },
    });

    // Limitar cambios de cantidad en productos con Nº de serie
    screens.OrderWidget.include({
        set_value: function (val) {
            var mode = this.numpad_state.get("mode");
            if (mode === "quantity" && parseFloat(val) > 1) {
                var order = this.pos.get_order();
                var selected_orderline = order.get_selected_orderline();
                if (selected_orderline.product.tracking === "serial") {
                    var msg = {
                        title: _t("Cant set quantity greater than 1"),
                        body: _t(
                            "This product has serial number management. Quantity must be 1"
                        ),
                    };
                    this.gui.show_popup("error", msg);
                }
                return;
            }
            this._super(val);
        },
    });

    // BUTTON TO OPEN POPUP LOT
    var ButtonOpenLotPopupWidget = screens.ActionButtonWidget.extend({
        template: "ButtonOpenLotPopupWidget",
        init: function (parent) {
            return this._super(parent);
        },
        renderElement: function () {
            var self = this;
            this._super();
            this.$(".select-lot").click(function () {
                self.gui.show_popup("select-lot", {
                    title: _t("Enter Serial Nº"),
                });
            });
        },
    });

    // // POP UP LOT
    screens.ProductScreenWidget.include({
        start: function () {
            this._super();
            this.popup_lot = new ButtonOpenLotPopupWidget(this, {});
            this.popup_lot.replace(this.$(".placeholder-ButtonOpenLotPopupWidget"));
        },
    });

    return screens;
});
