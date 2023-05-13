{
    'name': 'Construction Project Planning and Controlling',
    'version': '14.0.10',
    'category': 'Construction',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': "www.pragtech.co.in",
    'summary': 'Construction Project Planning and Controlling construction project planning and controlling project planning and controlling project planning project controlling construction construction management construction app construction module',
    'description': """
Construction Project Planning and Controlling
=============================================
Project Planning, budgeting, costing
<keywords>
construction project planning and controlling
project planning and controlling
project planning 
project controlling
construction
construction management
construction app
construction module
    """,
    'depends': ['base', 'product', 'project', 'stock', 'account'],  # 'web_list_view_sticky'],
    'data': [
        'views/execution_menu.xml',
        'views/stages_view.xml',
        'data/stage_master_data.xml',
        # 'data/stage_transaction_data.xml',
        'views/mail_message_view.xml',
        'wizard/stage_transaction_wizard.xml',
        'views/material_view.xml',
        'views/task_library_view.xml',
        'views/labour_view.xml',
        'views/category_view.xml',
        'security/access_rules.xml',
        'security/ir.model.access.csv',
        # 'security/user_groups.xml',
        'views/project_view.xml',
        'views/task_view.xml',
        'views/sub_project_view.xml',
        'views/category_budget.xml',
        'wizard/task_scheduler_wizard.xml',
        'views/sequence_view.xml',
        'report/report.xml',
        'report/groupwise_cost_variance_report.xml',
        'report/category_budget_report.xml',
        # 'wizard/wizard_gantt_view.xml',
        # 'views/assets.xml',
        'views/res_usr.xml',
    ],
    'images': ['images/Animated-Construction-ppc.gif'],
    'live_test_url': 'https://www.pragtech.co.in/company/proposal-form.html?id=103&name=Odoo-Construction-Management',
    'license': 'OPL-1',
    'price': 243.50,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
}
