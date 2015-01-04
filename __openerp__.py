{
    'name' : 'Crane & Hoist Service and Inspection System',  
    'version' : '1.0',
    'author' : 'RootRock Inc.',
    'summary': 'Equipments, Inspection & Work Order Management',
    'category' : 'Base',
    'depends' : ['base','hr'],
    'description' : """

Crane & Hoist Service and Inspection System:

- Equipment Type & Equipment management with sample report for Equipment.
- Work order Management
- Inspection Result Management

""",
    "website" : "http://rootrock.com",
    "init" : [],
    "demo" : [],
    "data" : ['security/crane_hoist_security.xml',
              'security/ir.model.access.csv',
              'wizard/inspection_point_photo.xml',
              'equipment_view.xml',
              'workorder_view.xml',
              'workorder_sequence.xml',
              'equipment_report_view.xml',
              'wizard/wo_followup_view.xml',              
              'res_partner_view.xml',
              'equipment_data.xml',
              'views/report_woinspection.xml',
              'views/layouts.xml',
              'views/report_workorder.xml',
              'views/report_workorder_inspection.xml',
              'views/report_workorder_sling.xml',
              'views/report_rr_equipment.xml'
              ],
     'css': ['static/src/css/crane_hoist.css'],
    "active": False 
}
