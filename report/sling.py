import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.report import report_sxw

class sling_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(sling_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_lines': self._get_lines,
            'get_sling_lines': self._get_sling_lines,
            'get_spec_values': self._get_spec_values,            
        })
    
    def _get_lines(self, worder):
        res = []
        new_header = {}
        query = _("select st.name, MAX(st.id) from spec_task st, equipment_work_order_task ewt, equipment_work_order ew where st.task_id = ewt.id and ewt.wo_id=ew.id and ewt.equipment_customer_id in (select ec.id from equipment_type et, equipment_customer ec where ec.equipment_type_id = et.id and et.name='Sling') and ew.name='%s' group by st.name order by MAX(st.id)")%(str(worder))        
        self.cr.execute(query)
        specs = self.cr.fetchall()
        i = 0
        if specs:
            for sp in specs:
                if i==0:
                    new_header['first']=sp[0]
                elif i==1:
                    new_header['second']=sp[0]
                elif i==2:
                    new_header['third']=sp[0]
                elif i==3:
                    new_header['forth']=sp[0]
                i+=1
            if new_header:
                res.append(new_header)        
        return res
    
    def _get_sling_lines(self, worder):
        res = []        
        query = _("select ewt.name, (select ec.name from equipment_customer ec where ec.id=ewt.equipment_customer_id) as certificate from equipment_work_order_task ewt, equipment_work_order ew where ew.id = ewt.wo_id and ewt.equipment_customer_id in (select ec.id from equipment_type et, equipment_customer ec where ec.equipment_type_id = et.id and et.name='Sling') and ew.name='%s'")%(str(worder))        
        self.cr.execute(query)
        slings = self.cr.fetchall()        
        if slings:
            for sl in slings:
                sling_ids = {}
                sling_ids['name']=sl[0]
                sling_ids['certificate']=sl[1]
                res.append(sling_ids)
        return res
    
    def _get_spec_values(self, taskname):
        res = []
        new_values = {}
        query = _("select st.spec_value, (select it.name from inspection_result_type it where it.id=sp.point_status) as result, sp.point_comment from spec_inspection_points sp, spec_task st, equipment_work_order_task ewt where st.task_id = ewt.id and sp.task_id = ewt.id and ewt.name='%s' group by st.spec_value, sp.point_status, sp.point_comment order by Max(st.id)")%(str(taskname))        
        self.cr.execute(query)
        spec_values = self.cr.fetchall()
        i = 0
        if spec_values:
            for sv in spec_values:
                if i==0:
                    new_values['first']=sv[0]
                    new_values['result']=sv[1]
                    new_values['comment']=sv[2]
                elif i==1:
                    new_values['second']=sv[0]
                elif i==2:
                    new_values['third']=sv[0]
                elif i==3:
                    new_values['forth']=sv[0]
                i+=1
            if new_values:
                res.append(new_values)        
        return res
    
report_sxw.report_sxw('report.customer.sling.workorders', 'equipment.work.order', 'addons/crane_hoist_inspection_system/report/sling.rml', parser=sling_report, header=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

