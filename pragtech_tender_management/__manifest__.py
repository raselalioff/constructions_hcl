{
    'name': 'Odoo Tender Management',
    'version': '14.0.2',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': "www.pragtech.co.in",
    'category': 'Construction',
    'depends': ['resource', 'product', 'website', 'website_sale'],
    'summary': 'Odoo Tender Management System odoo tender management app tender management software odoo tender',
    'description': """
Odoo Tender Management System
=============================
This app has below features:
----------------------------
    1) Tender publication
    2) Pre-bid meeting and MOM
    3) Final tender correction and publication 
    4) Technical bids submission
    5) Financial bids submission
    6) Bids comparison and bid winner announcement
<keywords>
odoo tender management
tender management
tender management app
tender management software
tender
odoo tender
    """,
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/tenders_view.xml',
        'views/bids_view.xml',
        'views/assets.xml',
        'data/entry.xml',
        'views/tenders_template.xml',
        'views/rank_template.xml',
        'views/tenders_labours.xml',
        'views/bids_template.xml',
        'views/logged_in_template.xml',
    ],
    'images': ['images/Animated-tender-management.gif'],
    'live_test_url': 'https://www.pragtech.co.in/company/proposal-form.html?id=103&name=tender-management',
    'license': 'OPL-1',
    'price': 145.71,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
}
