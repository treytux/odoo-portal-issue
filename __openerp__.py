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

{
    'name': 'Personalizacion para trey',
    'category': 'customize',
    'summary': 'Personalizacion para la instancia de Trey ',
    'version': '0.1',
    'description': """
    """,
    'author': 'Trey',
    'depends': ['base', 'report', 'sale', 'account'],
    'data': [
        'reports/report_paperformat.xml',
        'reports/report_layout.xml',
        'reports/report_saleorder.xml',
        'reports/report_invoice.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'qweb': [
    ],
    'js': [
    ],
    'css': [
    ],
    'installable': True,
}
