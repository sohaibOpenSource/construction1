# -*- encoding: utf-8 -*-

{
    'name' : 'Bolson',
    'version' : '2.0',
    'category': 'Custom',
    'description': """Manejo de cajas chicas y liquidaciones ( obsoleto, ya no usar )""",
    'author': 'aquíH',
    'website': 'http://www.aquih.com/',
    'depends' : [ 'account' ],
    'data' : [
        'views/report.xml',
        'views/bolson_view.xml',
        'views/reporte_bolson.xml',
        'security/ir.model.access.csv',
        'security/bolson_security.xml',
    ],
    'installable': True,
    'certificate': '',
}
