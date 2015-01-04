import time

from openerp.report import report_sxw

class inspection(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(inspection, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time, 
        })
report_sxw.report_sxw('report.customer.inspections', 'equipment.work.order.task', 'addons/crane_hoist_inspection_system/report/inspection.rml', parser=inspection, header=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

