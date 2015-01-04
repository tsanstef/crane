from openerp.osv import fields, osv
from openerp import tools


class equipment_type(osv.osv):
    _name = "equipment.type"
    _description = "Equipment Type"
    _columns = {
        'name': fields.char('Equipment Type Name', size=64, required=True, select=True),
        'specification_line': fields.one2many('equipment.type.specification', 'equipment_type_id', 'Specification List'),
        'inspection_line': fields.one2many('equipment.type.inspection.point', 'equipment_type_id', 'Inspection Points'),                
    }

class equipment_type_specification(osv.osv):
    _name = "equipment.type.specification"
    _description = "Specification List"
    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),
        'orderno':fields.integer('Order'),
        'equipment_type_id': fields.many2one('equipment.type', 'Equipment Type Reference', select=True),        
    }
    _defaults = {        
        'orderno': 1,
    }
    _order='orderno, id'
    
class equipment_type_inspection_point(osv.osv):
    _name = "equipment.type.inspection.point"
    _description = "Inspection Points"
    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),
        'point_header':fields.boolean('Header'),
        'orderno':fields.integer('Order'),
        'equipment_type_id': fields.many2one('equipment.type', 'Equipment Type Reference', select=True),        
    }
    _defaults = {
        'point_header':False,
        'orderno': 1,
    }
    _order='orderno, id'    
    
    
class equipment_customer(osv.osv):
    _name = "equipment.customer"
    _description = "Equipments"
    _columns = {
        'name': fields.char('Certification Number', select=True, required=True),
        'equipment_type_id': fields.many2one('equipment.type', 'Equipment Type', select=True, required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', select=True, required=True),
        'photo' : fields.binary('Picture'),
        'notes' : fields.text('Notes'),
        'equip_specification_line': fields.one2many('equipment.customer.specification', 'equipment_id', 'Specification List'),                
    }
        
    def onchange_equipment_type_id(self, cr, uid, ids, equipment_type_id=False,context=None):
        equipment_obj = self.pool.get('equipment.type.specification')
        specification_obj = self.pool.get('equipment.customer.specification')
        specification_ids =[]
        
        if context is None:
            context = {}
        #delete old specification lines
        old_equipment_type_ids = ids and specification_obj.search(cr, uid, [('equipment_id', '=', ids[0])], context=context) or False
        if old_equipment_type_ids:
            specification_obj.unlink(cr, uid, old_equipment_type_ids, context=context)

        #defaults
        res = {'value':{
                      'equip_specification_line':[],                      
                }
            }
        
        if (not equipment_type_id):
            return res      
       
        
        equip_type_ids = equipment_obj.search(cr, uid, [('equipment_type_id', '=', equipment_type_id)], context=context)
        #raise osv.except_osv(_('Error!'), _(str(ids[0]))) 
        
        for eq_id in equipment_obj.browse(cr, uid, equip_type_ids, context=context):
                specs = {
                          'name': eq_id.name,
                          'orderno': eq_id.orderno,                             
                        }
                specification_ids += [specs]
        
        res['value'].update({
                    'equip_specification_line': specification_ids,
        })        
        return res
    
class equipment_customer_specification(osv.osv):
    _name = "equipment.customer.specification"
    _description = "Specification List"
    _columns = {
        'name': fields.char('Specification', size=128, required=True, select=True),
        'spec_value': fields.char('Value', size=128, select=True),
        'orderno':fields.integer('Order'),
        'equipment_id': fields.many2one('equipment.customer', 'Customer Equipment', select=True),        
    }
    _defaults = {        
        'orderno': 1,
    }
    _order='orderno, id'
    