# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': 'Template Report',
    'description': 'Is Easy an elegant and scalable solution to design reports'
                   'using LibreOffice or OpenOffice.',
    'summary': 'Export data all objects Odoo to LibreOffice, professional report, simple report designer, ideal for contracts. LibreOffice output files odt, pdf, doc, docx, ods',
    'category': 'All',
    'version': '1.0',
    'website': 'http://www.buildfish.com/',
    "license": "AGPL-3",
    'author': 'BuildFish',
    'depends': [
        'base', 'web'
    ],
    "external_dependencies": {
        "python": ["py3o.template", "genshi"],
        "bin": ["unoconv"],
    },
    'data': [
        'data/templates.xml',
        'report.xml',
        'views/webclient_templates.xml',
        'views/report_views.xml'
    ],
    'live_test_url': 'https://youtu.be/1AMrnUH7Kh8',
    'price': 109.00,
    'currency': 'EUR',
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
