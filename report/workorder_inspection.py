import time

from openerp.report import report_sxw

class workorder_inspection(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(workorder_inspection, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
    
report_sxw.report_sxw('report.customer.workorders.inspection', 'equipment.work.order', 'addons/crane_hoist_inspection_system/report/workorder_inspection.rml', parser=workorder_inspection, header=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

