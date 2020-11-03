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
            // debugger;
            var line = new OrderLine({}, {pos: this.pos, order: this, product: product});
            this.fix_tax_included_price(line);
    
            line.set_quantity(1);
            line.set_unit_price(lot.list_price);
            this.fix_tax_included_price(line);
    
            // if(options.lst_price !== undefined){
            //     line.set_lst_price(options.lst_price);
            // }
              
            this.orderlines.add(line);
            this.select_orderline(this.get_last_orderline());
    
            // if(line.has_product_lot){
            //     this.display_lot_popup();
            // }
            if (this.pos.config.iface_customer_facing_display) {
                this.pos.send_current_order_to_customer_facing_display();
            }
        }

    });
});
