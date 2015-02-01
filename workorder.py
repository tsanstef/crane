from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime
import time
import calendar
from openerp import tools
import base64


class equipment_work_order_task(osv.osv):
    _name = "equipment.work.order.task"
    _description = "Work Order Tasks"
    
    # Array containing different task types
    TASK_TYPE = [
        ('inspection', 'Inspection'),
        ('service', 'Service'),        
    ]
    
    RESULT_SELECTION = [
         ('safe', 'Safe'),
         ('not_safe', 'Not Safe'),
     ]
    
    # Array containing different states
    STATE_SELECTION = [
        #('draft', 'Draft'),
        ('inprocess', 'In Process'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ]
    
    # Fetching labor totals from all the labor lines 
    def _get_labor_total(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for labor in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for lb in labor.labor_line:
                total += lb.duration
            res[labor.id] = total
        return res
    
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.signature, avoid_resize_medium=True)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'signature': tools.image_resize_image_big(value)}, context=context)

    
    _columns = {
        'name': fields.char('Work Order Task', required=True, select=True,readonly=True),              
        'task_type': fields.selection(TASK_TYPE, 'Type',required=True,readonly=False,states={'done': [('readonly', True)]}),        
        'equipment_customer_id': fields.many2one('equipment.customer','Certification Number', required=True,readonly=False,states={'done': [('readonly', True)]}),
        'equipment_type': fields.related('equipment_customer_id', 'equipment_type_id', type="many2one", relation="equipment.type", string="Equipment Type", readonly=True),        
        'date': fields.date('Completion Date',readonly=False,states={'done': [('readonly', True)]}),        
        'labor_total': fields.function(_get_labor_total, method=True, type="float", store=True, string='Total Labor h'),        
        'state': fields.selection(STATE_SELECTION, 'Status'),
        'notes': fields.text('Notes',readonly=False,states={'done': [('readonly', True)]}),
        'desc': fields.char('Description',size=128,readonly=False,states={'done': [('readonly', True)]}),
        'wo_id': fields.many2one('equipment.work.order', 'Work Order Task',select=True,ondelete='cascade'),
        'labor_line': fields.one2many('labor.task', 'task_id', 'Labor Lines', readonly=True, states={'inprocess': [('readonly', False)]}),
        'spec_line': fields.one2many('spec.task', 'task_id', 'Specification Lines'),
        'insp_spec_points': fields.one2many('spec.inspection.points', 'task_id', 'Inspection Points',readonly=False,states={'done': [('readonly', True)]}),
        'service_spec_parts': fields.one2many('spec.service.parts', 'task_id', 'Parts',readonly=True,states={'inprocess': [('readonly', False)],}),
        'inspection_result': fields.selection(RESULT_SELECTION, 'Inspection Result',readonly=True,states={'inprocess': [('readonly', False)]}),
        'inspector': fields.many2one('hr.employee','Performed By', select=True),
        'partner_id': fields.related('equipment_customer_id', 'partner_id', type="many2one", relation="res.partner", string="Customer", readonly=True),
        'signature': fields.binary("Signature", help="This field holds signature image, limited to 1024x1024px.",readonly=True,states={'inprocess': [('readonly', False)]}),
        'signature_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Signature", type="binary", multi="_get_image",
            store={
                'equipment.work.order.task': (lambda self, cr, uid, ids, c={}: ids, ['signature'], 10),
            }),
        'signature_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            store={
                'equipment.work.order.task': (lambda self, cr, uid, ids, c={}: ids, ['signature'], 10),
            },
            help="Small-sized image of the sign. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),        
        
    }
    _order = 'name'
    _defaults = {
        'date': fields.date.context_today,
        'state': 'inprocess',
        'task_type':'inspection',
        'name':'/',        
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name,wo_id)', 'Task name must be unique per WO!'),
    ]
    # Creating automatic sequence of Tasks
    def create(self, cr, uid, vals, context=None):               
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'equipment.work.order.task') or '/'
        if vals.get('wo_id'):
            query = _("update equipment_work_order set state='inprocess' where id=%s")%(str(vals.get('wo_id')))
            cr.execute(query)
        
        return super(equipment_work_order_task, self).create(cr, uid, vals, context=context)
    
    #Preventing deletion of a task which is not in draft state
    def unlink(self, cr, uid, ids, context=None):
        stat = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for t in stat:
            if t['state'] in ('draft', 'inprocess'):
                unlink_ids.append(t['id'])
            else:
                raise osv.except_osv(_('Invalid Action!'), _('You can not delete a task which is in "In Process" or "Done" state'))
        osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
        return True
    
    # Method will call when user click on "Start Task" button
#     def task_start(self, cr, uid, ids, context=None):        
#         self.write(cr, uid, ids, {'state': 'inprocess'}, context=context)        
#         query = ''
#         # Updating status of inspection points to make it readable
#         for insp_point in self.browse(cr, uid, ids, context=context):
#             if insp_point.task_type=='inspection' and insp_point.insp_spec_points:                
#                 query = _("update spec_inspection_points set state='task_not_draft' where task_id=%s")%(str(insp_point.id))                
#                     
#         if query:
#             cr.execute(query)
#         
#         wos_ids = set()
#         # Fetching "wo_id" from task table
#         for order in self.read(cr, uid, ids, ['wo_id'], context=context):
#             wos_ids.add(order['wo_id'][0])
#         wo_ids = []
#         
#         # Finding and assigning active workorder id to wo_ids array
#         for id in wos_ids: wo_ids.append(id)
#         
#         #Initiating workorder object
#         wo = self.pool.get('equipment.work.order')
#         inprocess_wo_ids = []
#         
#         #Running a loop inside selected workorder to define its state
#         for order in wo.browse(cr, uid, wo_ids, context=context):
#             inprocess = False
#             # If any of task having 'inprocess' state then and if workorder is not in 'inprocess',
#             # then this method will convert workorder state to 'inprocess'
#             for task in order.wo_task_lines:
#                 if task.state == 'inprocess':
#                     inprocess = True
#                     break
#             if inprocess: inprocess_wo_ids.append(order.id)
#         wo.write(cr, uid, inprocess_wo_ids, {'state': 'inprocess'})
#         return True
    
    def task_inprocess(self, cr, uid, ids, context=None):        
        # Check inspection result or inspector before completing task
        for insp in self.browse(cr, uid, ids, context=context):
            if not insp.inspection_result and insp.task_type=='inspection':                
                raise osv.except_osv(_('Warning!'), _('Please select inspection result before completing task'))
        
            emp = ''
            qur_select = _("select he.id from hr_employee he, resource_resource re where re.user_id='%s' and re.id=he.resource_id")%(str(uid))
            cr.execute(qur_select) 
            val_emp = cr.fetchone()
            if val_emp:
                emp = val_emp[0]
                qur_update = _("update equipment_work_order_task set inspector=%s where id=%s")%(str(emp),str(insp.id))
                cr.execute(qur_update)
            #else:
            #    raise osv.except_osv(_('Warning!'), _('The employee of this request is missing. Please make sure that your user login is linked to an employee.'))
        self.write(cr, uid, ids, {'state': 'done','date': time.strftime('%Y-%m-%d')}, context=context)
                
        wos_ids = set()
        # Fetching "wo_id" from task table
        for order in self.read(cr, uid, ids, ['wo_id'], context=context):
            wos_ids.add(order['wo_id'][0])
        wo_ids = []
        # Finding and assigning active workorder id to wo_ids array
        for id in wos_ids: wo_ids.append(id)
        #Initiating workorder object
        wo = self.pool.get('equipment.work.order')
        done_wo_ids = []
        
        #Running a loop inside selected workorder to define its state
        for order in wo.browse(cr, uid, wo_ids, context=context):
            done = True
            
            # If any of task having 'done' state then and if workorder is not in 'done',
            # then this method will convert workorder state to 'done'
            for task in order.wo_task_lines:
                if task.state != 'done':
                    done = False
                    break
            if done:                  
                done_wo_ids.append(order.id)
        wo.write(cr, uid, done_wo_ids, {'state': 'task_completed'})
        return True
    
    def task_set_to_draft(self, cr, uid, ids, context=None):        
        self.write(cr, uid, ids, {'state': 'inprocess'}, context=context)
        wos_ids = set()
        # Fetching "wo_id" from task table
        for order in self.read(cr, uid, ids, ['wo_id'], context=context):
            wos_ids.add(order['wo_id'][0])
        wo_ids = []
        
        # Finding and assigning active workorder id to wo_ids array
        for id in wos_ids: wo_ids.append(id)
        
        #Initiating workorder object
        wo = self.pool.get('equipment.work.order')
        inprocess_wo_ids = []
        
        #Running a loop inside selected workorder to define its state
        for order in wo.browse(cr, uid, wo_ids, context=context):
            inprocess = False
            # If any of task having 'inprocess' state then and if workorder is not in 'inprocess',
            # then this method will convert workorder state to 'inprocess'
            for task in order.wo_task_lines:
                if task.state == 'inprocess':
                    inprocess = True
                    break
            if inprocess: inprocess_wo_ids.append(order.id)
        wo.write(cr, uid, inprocess_wo_ids, {'state': 'inprocess'})
        return True
    
    def print_inspection(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time'        
        datas = {
            'model': 'equipment.work.order.task',
            'ids': ids,
            'form': self.read(cr, uid, ids[0], context=context),
        }
        return {
            'type': 'ir.actions.report.xml', 
            'report_name': 'crane_hoist_inspection_system.report_woinspection', 
            'datas': datas, 'nodestroy': True
        }
    
    
    # Fetching specification lines and equipment type values
    def onchange_equipment_customer_id(self, cr, uid, ids, equipment_customer_id=False,context=None):
        spec_line_obj = self.pool.get('equipment.customer.specification')
        customer_obj = self.pool.get('equipment.customer')
        task_obj = self.pool.get('spec.task')
        inspection_obj = self.pool.get('spec.inspection.points')
        inspection_line_obj = self.pool.get('equipment.type.inspection.point')
        specification_ids =[]
        specification_ids1 =[]
        
        if context is None:
            context = {}
        #delete old specification lines
        old_spec_line_ids = ids and task_obj.search(cr, uid, [('task_id', '=', ids[0])], context=context) or False
        if old_spec_line_ids:
            task_obj.unlink(cr, uid, old_spec_line_ids, context=context)
            
        #delete old inspection points
        old_insp_line_ids1 = ids and inspection_obj.search(cr, uid, [('task_id', '=', ids[0])], context=context) or False
        if old_insp_line_ids1:
            inspection_obj.unlink(cr, uid, old_insp_line_ids1, context=context)

        #defaults
        res = {'value':{
                      'spec_line':[],
                      'insp_spec_points':[],
                      'equipment_type':'',
                      'partner_id':'',                 
                }
            }
        
        # if not equipment customer id present then nothing will process
        if (not equipment_customer_id):
            return res      
       
        # Getting equipment type values       
        eq = customer_obj.browse(cr, uid, equipment_customer_id, context=context)
        res['value'].update({
                'equipment_type': eq.equipment_type_id.id,
                'partner_id':eq.partner_id.id,                                                                                       
        })
        
        # Getting specification lines values       
        equip_type_ids1 = spec_line_obj.search(cr, uid, [('equipment_id', '=', equipment_customer_id)], context=context)
        for eq_id in spec_line_obj.browse(cr, uid, equip_type_ids1, context=context):
                
                specs = {
                          'name': eq_id.name,
                          'spec_value':eq_id.spec_value,
                          'orderno': eq_id.orderno,                             
                        }
                specification_ids += [specs]
        
        res['value'].update({
                    'spec_line': specification_ids,
        }) 
        
        # Getting specification points values       
        equip_type_ids2 = inspection_line_obj.search(cr, uid, [('equipment_type_id', '=', eq.equipment_type_id.id)], context=context)
        for point_id in inspection_line_obj.browse(cr, uid, equip_type_ids2, context=context):
                
                specs1 = {
                          'name': point_id.name,
                          'point_header': point_id.point_header,
                          'state':'task_draft',                                                       
                        }
                specification_ids1 += [specs1]
        
        res['value'].update({
                    'insp_spec_points': specification_ids1,
        })       
        return res
    
    def onchange_wo_id(self, cr, uid, ids, wo_id=False,context=None):
        wo_obj = self.pool.get('equipment.work.order')        
        if context is None:
            context = {}
            
        #defaults
        res = {'value':{
                      'partner_id':'',      
                }
            }
        
        # if not work order id present then nothing will process
        if (not wo_id):
            return res      
       
        wo = wo_obj.browse(cr, uid, wo_id, context=context)
        wo_partner_id = wo.partner_id.id
        
        # Getting partner id       
        if wo_partner_id:
            res['value'].update({
                    'partner_id': wo_partner_id,
                    })
      
        return res
    
    # Fetching total labor values from labor lines
    def onchange_task_labor_time(self, cr, uid, ids, labor_total):
        total = 0.0        
        for labor in self.resolve_2many_commands(cr, uid, 'labor_line', labor_total, context=None):
            if labor.get('duration'):
                total += labor.get('duration')        
        return {'value': {
            'labor_total': total,
        }}

# Initializing specification lines object
class spec_task(osv.osv):
    _name = "spec.task"
    _description = "Specification Lines"
    _columns = {
        'name': fields.char('Specification', size=128,required=True),
        'spec_value': fields.char('Value', size=128),
        'orderno':fields.integer('Order'),
        'task_id': fields.many2one('equipment.work.order.task', 'Work Order Task',select=True,ondelete='cascade'),        
    }
    _defaults = {        
        'orderno': 1,
    }
    _order='orderno, id'

# Initializing labor lines object
class labor_task(osv.osv):
    _name = "labor.task"
    _description = "Task Specification"
    
    # Array containing different labor types
    LABOR_TYPE = [
        ('regular', 'R'),
        ('overtime', 'O'),
        ('double', 'D'),        
    ]
    
    _columns = {
        'name': fields.char('Comment', size=512),
        'start_time': fields.datetime('Start',required=True),
        'end_time': fields.datetime('End',required=True),
        'duration': fields.float('Duration',required=True,digits=(16,2)),        
        'labor_type': fields.selection(LABOR_TYPE, 'Type'),        
        'task_id': fields.many2one('equipment.work.order.task', 'Work Order Task',select=True,ondelete='cascade'),                        
    }
    _defaults = {
        'labor_type':'regular',                                 
    }
    
    def onchange_labor_time(self, cr, uid, ids, start_time, end_time, duration):
        # if start time and end time is present then it will calculate duration automatically
        if start_time and end_time:
            start_time = 1.0*calendar.timegm(time.strptime(start_time, "%Y-%m-%d %H:%M:%S"))
            end_time = 1.0*calendar.timegm(time.strptime(end_time, "%Y-%m-%d %H:%M:%S"))
            return {'value': {
                'duration': (end_time - start_time)/3600,
            }}
        # if start time is present then it will automatically fetch end time
        if start_time:
            end_time = 1.0*calendar.timegm(time.strptime(start_time, "%Y-%m-%d %H:%M:%S")) + 3600*duration
            return {'value': {
            'end_time': time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(end_time)),
            }}
        # if end time is present then it will automatically fetch start time
        if end_time:
            start_time = 1.0*calendar.timegm(time.strptime(end_time, "%Y-%m-%d %H:%M:%S")) - 3600*duration
            return {'value': {
            'start_time': time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(start_time)),
            }}
        return {}

    def onchange_labor_duration(self, cr, uid, ids, start_time, end_time, duration):
        # end time will automatically calculate based on duration and start time
        if start_time:
            end_time = 1.0*calendar.timegm(time.strptime(start_time, "%Y-%m-%d %H:%M:%S")) + 3600*duration
            return {'value': {
            'end_time': time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(end_time)),
            }}
        # start time will automatically calculate based on duration and end time
        if end_time:
            start_time = 1.0*calendar.timegm(time.strptime(end_time, "%Y-%m-%d %H:%M:%S")) - 3600*duration
            return {'value': {
            'start_time': time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(start_time)),
            }}
        return {}

# Work order object functionality    
class equipment_work_order(osv.osv):
    _name = "equipment.work.order"
    _description = "Equipment Work Order"
    
    # Array containing different workorder states
    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('inprocess', 'In Process'),
        ('task_completed', 'Task(s) Completed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ]
    
    # Calculating total labor lines from all the tasks
    def _get_labor_total(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for wo_task in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for wt in wo_task.wo_task_lines:
                if wt.labor_line:
                    for lt in wt.labor_line:
                        total += lt.duration
            res[wo_task.id] = total
        return res
    
    _columns = {
        'name': fields.char('Work Order', size=64, required=True, select=True,readonly=False,states={'inprocess': [('readonly', True)],'task_completed': [('readonly', True)],'done': [('readonly', True)]}),
        'partner_id': fields.many2one('res.partner','Customer', select=True, required=True,readonly=False,states={'inprocess': [('readonly', True)],'task_completed': [('readonly', True)],'done': [('readonly', True)]}),        
        'purchase_order': fields.char('Purchase Order', size=64,readonly=False,states={'inprocess': [('readonly', True)],'task_completed': [('readonly', True)],'done': [('readonly', True)]}),
        'date': fields.date('Date',readonly=False,states={'inprocess': [('readonly', True)],'task_completed': [('readonly', True)],'done': [('readonly', True)]}),
        'origin': fields.char('Source Document', size=64,readonly=False,states={'inprocess': [('readonly', True)],'task_completed': [('readonly', True)],'done': [('readonly', True)]}),
        'accepted_by': fields.char('Accepted By (Customer Name)', size=64,readonly=False,states={'done': [('readonly', True)]}),
        'labor_total': fields.function(_get_labor_total, method=True, store=True,type="float", string='Total Labor h'),
        'state': fields.selection(STATE_SELECTION, 'Status',readonly=False),
        'desc': fields.text('Description',readonly=False,states={'done': [('readonly', True)]}),
        'wo_task_lines': fields.one2many('equipment.work.order.task', 'wo_id', 'Task',readonly=False,states={'done': [('readonly', True)]}),                       
    }
    _defaults = {
        'date': fields.date.context_today,
        'state': 'draft',       
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Work Order number must be unique!'),
    ]
    
    
    def wo_done(self, cr, uid, ids, context=None):
        for wo in self.browse(cr, uid, ids, context=context):
            if not wo.accepted_by:
                raise osv.except_osv(_('Warning!'), _('Please fill Accepted By to complete the WO'))
        self.write(cr, uid, ids, {'state': 'done','date': time.strftime('%Y-%m-%d')}, context=context)        
        return True
    
class inspection_result_type(osv.osv):
    _name = "inspection.result.type"
    _description = "Inspection Result Types"
    
    _columns = {
        'name': fields.char('Inspection Results', required=True, select=True),
        'orderno':fields.integer('Order'),
    }
    _defaults = {
        'orderno':1,
    }
    _order='orderno, id'
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Inspection Result type must be unique!'),
    ]

class spec_inspection_points(osv.osv):
    _name = "spec.inspection.points"
    _description = "Inspection Points"
    
    STATE_SELECTION = [
         ('task_draft', 'Task In Draft'),
         ('task_not_draft', 'Task Not In Draft'),         
     ]
    
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    
    _columns = {
        'name': fields.char('Point Name', size=128,required=True),
        'point_header':fields.boolean('Header'),
        'point_status': fields.many2one('inspection.result.type','Result'),
        'point_comment': fields.char('Comment', size=128),        
        'task_id': fields.many2one('equipment.work.order.task', 'Tasks',select=True,ondelete='cascade'),
        'state': fields.selection(STATE_SELECTION, 'Status'),
        'image': fields.binary("Image", help="This field holds the photo of inspection point, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Photo", type="binary", multi="_get_image",
            store={
                'spec.inspection.points': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            }),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            store={
                'spec.inspection.points': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of the sign. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),        
    }
    _defaults = {
        'state':'task_not_draft',
    }  

class spec_service_parts(osv.osv):
    _name = "spec.service.parts"
    _description = "Service Parts"
    
    _columns = {
        'name': fields.char('Part Number', size=32,required=True),
        'part_desc': fields.char('Description', size=128),
        'part_qty': fields.integer('Quantity',required=True),
        'task_id': fields.many2one('equipment.work.order.task', 'Tasks',select=True,ondelete='cascade'),                
    }
    _defaults = {
        'part_qty':1,        
    }  
