# -*- coding: utf-8 -*-
##############################################################################
#
#    Trey, Kilobytes de Soluciones
#    Copyright (C) 2014-Today Trey, Kilobytes de Soluciones (<http://www.trey.es>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv
from openerp.tools.translate import _
from functools import partial
import logging

_log = logging.getLogger(__name__)


class SaleReport(osv.AbstractModel):
    _name = 'report.sale.report_saleorder'

    def get_taxes(self, cr, uid, order, context=None):
        taxes = {}
        for line in order.order_line:
            for t in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit * (1-(line.discount or 0.0)/100.0), line.product_uom_qty, line.product_id, line.order_id.partner_id)['taxes']:
                if t['name'] not in taxes:
                    taxes[t['name']] = 0
                taxes[t['name']] += t['amount']
        return taxes

    def render_html(self, cr, uid, ids, data=None, context=None):
        report_obj = self.pool['report']
        order_obj = self.pool['sale.order']
        report = report_obj._get_report_from_name(cr, uid, 'sale.report_saleorder')
        selected_orders = order_obj.browse(cr, uid, ids, context=context)

        docargs = {
            'doc_ids': ids,
            'doc_model': report.model,
            'docs': selected_orders,
            'get_taxes': partial(self.get_taxes, cr, uid, context=context),
        }

        return report_obj.render(cr, uid, ids, 'sale.report_saleorder', docargs, context=context)


class InvoiceReport(osv.AbstractModel):
    _name = 'report.trey_customize.report_invoice_trey'

    def get_taxes(self, cr, uid, invoice, context=None):
        taxes = {}
        for line in invoice.invoice_line:
            for t in self.pool.get('account.tax').compute_all(cr, uid, line.invoice_line_tax_id, line.price_unit * (1-(line.discount or 0.0)/100.0), line.quantity, line.product_id, invoice.partner_id)['taxes']:
                if t['name'] not in taxes:
                    taxes[t['name']] = 0
                taxes[t['name']] += t['amount']
        return taxes

    def render_html(self, cr, uid, ids, data=None, context=None):
        report_obj = self.pool['report']
        invoice_obj = self.pool['account.invoice']
        report = report_obj._get_report_from_name(cr, uid, 'trey_customize.report_invoice_trey')
        selected_orders = invoice_obj.browse(cr, uid, ids, context=context)

        docargs = {
            'doc_ids': ids,
            'doc_model': report.model,
            'docs': selected_orders,
            'get_taxes': partial(self.get_taxes, cr, uid, context=context),
        }

        return report_obj.render(cr, uid, ids, 'trey_customize.report_invoice_trey', docargs, context=context)

