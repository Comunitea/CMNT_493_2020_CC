/* Copyright 2018 Tecnativa - David Vidal
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

odoo.define('pos_custom_cc.models', function (require) {
    'use strict';

    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;

    var pos_super = models.PosModel.prototype;
    var order_super = models.Order.prototype;
   

    var OrderLine = models.Orderline;

    models.PosModel = models.PosModel.extend({
        scan_product: function(parsed_code) {
            // OVERWRITED TO ALWAYS SEARCH BY LOT NAME
            // pos_super.scan_product.apply(this, arguments);
            var selectedOrder = this.get_order();
            var search_lot_name = parsed_code['code']
            selectedOrder.add_product_by_lot(search_lot_name);
            return true
        },
    });
        
    // ************************************************************************
    // ************************************************************************
    // ************************************************************************
    // ************************************************************************
    
    models.Order = models.Order.extend({
        add_product_by_lot: function(lot_name){
            var self = this;
            var domain = [['name', '=', lot_name]];
            var fields = ['name', 'list_price', 'product_id', 'standard_price'];
            rpc.query({
                model: 'stock.production.lot',
                method: 'search_read',
                args: [domain, fields],
            }).then(function (res) {
                if (res){
                    var lot = res[0];
                    self.add_lot(lot, {})
                }
                else{
                    self.pos.gui.show_popup('error', {
                        'title': _t('Error searching Lot'),
                        'body': _t('Lot not exists'),
                    });
                }
            }).catch(function (reason){
                var error = reason.message;
                self.pos.gui.show_popup('error', {
                    'title': _t('Error searching Lot'),
                    'body': _t('Lot not exists or TpV is offline'),
                });
                // event.preventDefault();
            });
            
        },

        add_lot: function(lot, options){
            var product_id = lot.product_id[0]
            var product = this.pos.db.get_product_by_id(product_id);

            if(this._printed){
                this.destroy();
                return this.pos.get_order().add_product(product, options);
            }
            this.assert_editable();
            options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;
            debugger;
            var line = new OrderLine({}, {pos: this.pos, order: this, product: product, cost: lot.standard_price, lot_id: lot.id});
            this.fix_tax_included_price(line);
            
            line.set_quantity(1);
           
            
            // if(options.lst_price !== undefined){
                //     line.set_lst_price(options.lst_price);
                // }
            
                
            this.orderlines.add(line);
            this.select_orderline(this.get_last_orderline());
                
                // if(line.has_product_lot){
                    //     this.display_lot_popup();
                    // }

            debugger;
            if (line.product.tracking == 'serial'){
                var pack_lot_lines =  line.compute_lot_lines();
                var lot_line = pack_lot_lines.models[0];
                lot_line.set_lot_name(lot.name);
                pack_lot_lines.remove_empty_model();
                pack_lot_lines.set_quantity_by_lot();
                line.set_unit_price(lot.list_price);
                this.fix_tax_included_price(line);
                this.save_to_db();
                this.orderlines.trigger('change', line);
            }


            if (this.pos.config.iface_customer_facing_display) {
                this.pos.send_current_order_to_customer_facing_display();
            }
        }

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
    models.Orderline.prototype.initialize = function(attr, options){
        debugger;
        var self = this;
        this.cost = options.cost || 0.0
        this.lot_id = options.lot_id || false
        // this.set({
        //     cost:  options.cost || 0.0,
        //     lot_id:  options.lot_id || false,
        // });
        
        return _initialize_.call(this, attr, options);
    }
    
    var _exportjson_ = models.Orderline.prototype.export_as_JSON;
    models.Orderline.prototype.export_as_JSON = function(){
        debugger;
        var self = this;
        var res = _exportjson_.call(this);
        res.lot_id = this.lot_id;
        res.cost = this.cost;
        return res
    }

    // var _compute_ = models.Orderline.prototype.compute_all;
    // models.Orderline.prototype.compute_all = function(taxes, price_unit, quantity, currency_rounding, handle_price_include=true) {
    //     debugger;
    //     var self = this;
    //     if (this.cost && this.lot_id) {
    //         price_unit = price_unit - this.cost
    //     }
    //     return _compute_.call(this, taxes, price_unit, quantity, currency_rounding, handle_price_include);
    // }

});
