{
    'name': 'Construction - Purchase Management',
    'version': '14.8',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': "www.pragtech.co.in",
    'category': 'Construction',
    'summary': 'Construction Purchase Management odoo construction purchase Construction Purchase Management odoo purchase construction management',
    'description': """
Construction Purchase Management
================================    
<keywords>
construction
purchase management
odoo construction
purchase
Construction Purchase Management
odoo purchase
construction management
    """,
    'depends': ['base', 'pragtech_ppc', 'purchase','purchase_stock'],
    'data': [
             'wizard/stage_transaction_wizard.xml',
        'security/pragtech_purchase_security.xml',
        'security/ir.model.access.csv',
        'wizard/purchase_requisition_wizard.xml',
        'views/account_invoice_view.xml',
        'views/purchase_requisition.xml',
        'views/partner_view.xml',
        'views/purchase_view.xml',
        'views/vendor_quotation.xml',
        'views/quotation_comparison_view.xml',
        'views/purchase_transaction.xml',
        'views/purchase_advance_view.xml',
        'views/purchase_debit_recovery_view.xml',
        'views/stock_view.xml',
        'views/sequence_view.xml',
        'views/shipment_scheduler.xml',
        'report/purchase_order_summary.xml',
        'report/purchase_order_bill_summary.xml',
        'report/short_supply.xml',
        'report/unbilled_grn.xml',
        'report/report.xml',
        'wizard/procurement_view.xml',
        'wizard/purchase_order_summary.xml',
        'wizard/purchase_bill_summary.xml',
        'wizard/short_supply.xml',
        'wizard/unbilled_grn.xml',
    ],
    'images': ['images/Animated-Construction-purchase.gif'],
    'live_test_url': 'https://www.pragtech.co.in/company/proposal-form.html?id=103&name=construction-purchase',
    'license': 'OPL-1',
    'price': 194.60,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
}
