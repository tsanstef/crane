import time

from openerp.report import report_sxw

class workorder(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(workorder, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_time_string': self._get_time_string,
        })
        
    def _get_time_string(self,duration):
        result =''
        currentHours = int(duration // 1)
        currentMinutes =int(round(duration % 1 * 60))
        if(currentHours <= 9): 
            currentHours = "0" + str(currentHours)                
        if(currentMinutes <= 9): 
            currentMinutes = "0" + str(currentMinutes)
        result = str(currentHours)+":"+str(currentMinutes)     
        return result
        
    
report_sxw.report_sxw('report.customer.workorders', 'equipment.work.order', 'addons/crane_hoist_inspection_system/report/workorder.rml', parser=workorder, header=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

