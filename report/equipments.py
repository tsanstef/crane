import time

from openerp.report import report_sxw

class equipments(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(equipments, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time, 
        })
report_sxw.report_sxw('report.customer.equipments', 'equipment.customer', 'addons/crane_hoist_inspection_system/report/equipments.rml', parser=equipments, header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

