from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from openerp import tools

class equipment_work_order_followup(osv.osv_memory):
    _name = 'equipment.work.order.followup'
    _description = 'Work Order Followup'
    
    # Defining field for Followup wizard 
    _columns = {
         'name': fields.char('Followup WO Name', required=True),
    }
    
    def create_followup(self, cr, uid, ids, context=None):
        wo_obj = self.pool.get('equipment.work.order')# Workorder object        
        
        # Finding reference id of wizard
        data = self.browse(cr, uid, ids, context=context)[0]
        followup_name = data.name or '' # Assigning "Followup WO Name" field value to a variable
        
        #getting active workorder id and creating new followup workorder from that
        for wo in wo_obj.browse(cr, uid, context['active_ids'], context=context):            
            #Method to create new followup workorder
            wo_id = wo_obj.create(cr, uid, {
                'origin':wo.name,                            
                'name': followup_name,
                'partner_id': wo.partner_id.id,
                'purchase_order': wo.purchase_order,                
                'accepted_by': wo.accepted_by,
                'state': 'draft',
            }, context=context)
        # Automatically display new workorder screen after creation 
        return {
            'domain': "[]",
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'equipment.work.order',
            'res_id': int(wo_id),
            'view_id': False,
            'type': 'ir.actions.act_window',            
                }