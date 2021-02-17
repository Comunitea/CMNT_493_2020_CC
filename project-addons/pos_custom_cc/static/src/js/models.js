odoo.define("pos_custom_cc.models", function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    var rpc = require("web.rpc");
    var core = require("web.core");
    var _t = core._t;

    // Var pos_super = models.PosModel.prototype;
    // var order_super = models.Order.prototype;

    var OrderLine = models.Orderline;

    models.PosModel = models.PosModel.extend({
        scan_product: function (parsed_code) {
            // OVERWRITED TO ALWAYS SEARCH BY LOT NAME
            // pos_super.scan_product.apply(this, arguments);
            var selectedOrder = this.get_order();
            var search_lot_name = parsed_code.code;
            selectedOrder.add_product_by_lot(search_lot_name);
            return true;
        },
    });

    // ************************************************************************
    // ************************************************************************
    // ************************************************************************
    // ************************************************************************

    models.Order = models.Order.extend({
        add_product_by_lot: function (lot_name) {
            var self = this;
            var domain = [["name", "=", lot_name]];
            var fields = [
                "name",
                "list_price",
                "product_id",
                "standard_price",
                "rebu",
                "salable",
            ];
            rpc.query({
                model: "stock.production.lot",
                method: "search_read",
                args: [domain, fields],
            })
                .then(function (res) {
                    if (res) {
                        var lot = res[0];
                        if (lot.salable === false) {
                            self.pos.gui.show_popup("error", {
                                title: _t("Lot not salable"),
                                body: _t(
                                    "This lot is marked as no salable. Maybe is in police state or is a recoverable purchase"
                                ),
                            });
                        } else {
                            self.add_lot(lot, {});
                        }
                    } else {
                        self.pos.gui.show_popup("error", {
                            title: _t("Error searching Lot"),
                            body: _t("Lot not exists"),
                        });
                    }
                })
                // .catch(function (reason) {
                .catch(function () {
                    // Var error = reason.message;
                    self.pos.gui.show_popup("error", {
                        title: _t("Error searching Lot"),
                        body: _t("Lot not exists or TpV is offline"),
                    });
                    // Event.preventDefault();
                });
        },

        add_lot: function (lot, options) {
            var product_id = lot.product_id[0];
            var product = this.pos.db.get_product_by_id(product_id);

            if (this._printed) {
                this.destroy();
                return this.pos.get_order().add_product(product, options);
            }
            this.assert_editable();
            // Options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;
            // Debugger;
            var line = new OrderLine(
                {},
                {
                    pos: this.pos,
                    order: this,
                    product: product,
                    cost: lot.standard_price,
                    lot_id: lot.id,
                    rebu: lot.rebu,
                    lot_price: lot.list_price,
                }
            );
            this.fix_tax_included_price(line);
            
            line.set_quantity(1);
            // Que al setar cliente y hacer set_pricelist no se calcule el precio de nuevo
            line.price_manually_set = true

            // If(options.lst_price !== undefined){
            //     line.set_lst_price(options.lst_price);
            // }

            this.orderlines.add(line);
            this.select_orderline(this.get_last_orderline());

            // If(line.has_product_lot){
            //     this.display_lot_popup();
            // }

            // debugger;
            if (line.product.tracking === "serial") {
                var pack_lot_lines = line.compute_lot_lines();
                var lot_line = pack_lot_lines.models[0];
                lot_line.set_lot_name(lot.name);
                pack_lot_lines.remove_empty_model();
                pack_lot_lines.set_quantity_by_lot();
                line.set_unit_price(lot.list_price);
                this.fix_tax_included_price(line);
                this.save_to_db();
                this.orderlines.trigger("change", line);
            }

            if (this.pos.config.iface_customer_facing_display) {
                this.pos.send_current_order_to_customer_facing_display();
            }
        },
    });

    // ************************************************************************
    // ************************************************************************
    // ************************************************************************
    // ************************************************************************

    // Asi no me funciona del todo, no siempre entra en la herencia, lo hace al
    // principio, la manera de abajo es equivalente y funciona bien, aunque mas rara

    // var order_line_super = models.Orderline.prototype;
    // models.Orderline = models.Orderline.extend({
    //     initialize: function(attr, options){
    //         debugger;
    //         this.cost = options.cost || 0.0
    //         this.lot_id = options.lot_id || false
    //         order_line_super.initialize.apply(this, arguments);
    //     },
    //     export_as_JSON: function () {
    //         debugger;
    //         var res = order_line_super.export_as_JSON.apply(this, arguments);
    //         // if (this.lot_id) {
    //         res.lot_id = this.lot_id;
    //         res.cost = this.cost;
    //         // }
    //         return res;
    //     },
    //     compute_all: function(taxes, price_unit, quantity, currency_rounding, handle_price_include=true) {
    //         debugger;
    //         if (this.cost && this.lot_id) {
    //             price_unit = price_unit - this.cost
    //         }
    //         var res = order_line_super.compute_all.apply(this, arguments);
    //         return res
    //     },

    // });

    var _initialize_ = models.Orderline.prototype.initialize;
    models.Orderline.prototype.initialize = function (attr, options) {
        // Debugger;
        // var self = this;
        this.cost = options.cost || 0.0;
        this.lot_price = options.lot_price || 0.0;
        this.lot_id = options.lot_id || false;
        this.rebu = options.rebu || false;
        // This.set({
        //     cost:  options.cost || 0.0,
        //     lot_id:  options.lot_id || false,
        // });

        return _initialize_.call(this, attr, options);
    };

    var _exportjson_ = models.Orderline.prototype.export_as_JSON;
    models.Orderline.prototype.export_as_JSON = function () {
        // Debugger;
        // var self = this;
        var res = _exportjson_.call(this);
        res.lot_id = this.lot_id;
        res.cost = this.cost;
        res.rebu = this.rebu;
        return res;
    };

    var _initjson_ = models.Orderline.prototype.init_from_JSON;
    models.Orderline.prototype.init_from_JSON = function (json) {
        _initjson_.call(this, json);
        this.lot_id = json.lot_id;
        this.cost = json.cost;
        this.rebu = json.rebu;
    };

    // Añado REBU a los impuestos
    // models.load_fields("account.tax", ['rebu']);

    var _compute_ = models.Orderline.prototype.compute_all;
    models.Orderline.prototype.compute_all = function (
        taxes,
        price_unit,
        quantity,
        currency_rounding,
        handle_price_include = true
    ) {
        var original_price_unit = price_unit;
        var new_price_unit = price_unit;
        if (this.rebu && this.cost && this.lot_id) {
            new_price_unit -= this.cost;
        }
        var res = _compute_.call(
            this,
            taxes,
            original_price_unit,
            quantity,
            currency_rounding,
            handle_price_include
        );
        var res2 = _compute_.call(
            this,
            taxes,
            new_price_unit,
            quantity,
            currency_rounding,
            handle_price_include
        );
        if (this.rebu && this.cost && this.lot_id) {
            res.taxes = res2.taxes;
            res.total_excluded = res2.total_excluded + this.cost;
        }
        return res;
    };

    // Var _map_ = models.Orderline.prototype._map_tax_fiscal_position;
    models.Orderline.prototype._map_tax_fiscal_position = function (tax) {
        // Debugger;
        var self = this;
        var current_order = this.pos.get_order();
        var order_fiscal_position = current_order && current_order.fiscal_position;
        var taxes = [];

        // BUSCO LA POSICIÓN REBU y si la línea está marcada como rebu la añado
        var fp_rebu = _.filter(this.pos.fiscal_positions, function (fp) {
            return fp.rebu === true;
        });

        var fp_nacional = _.filter(this.pos.fiscal_positions, function (fp) {
            return fp.rebu === false;
        });

        // TODO COMPROBAR QUE NO HAYA ENCONTRADO REBU
        order_fiscal_position = this.rebu === true ? fp_rebu[0] : fp_nacional[0];

        if (order_fiscal_position) {
            var tax_mappings = _.filter(
                order_fiscal_position.fiscal_position_taxes_by_id,
                function (fiscal_position_tax) {
                    return fiscal_position_tax.tax_src_id[0] === tax.id;
                }
            );

            if (tax_mappings && tax_mappings.length) {
                _.each(tax_mappings, function (tm) {
                    if (tm.tax_dest_id) {
                        taxes.push(self.pos.taxes_by_id[tm.tax_dest_id[0]]);
                    }
                });
            } else {
                taxes.push(tax);
            }
        } else {
            taxes.push(tax);
        }

        return taxes;
    };
});
