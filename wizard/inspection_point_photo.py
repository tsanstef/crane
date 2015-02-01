from openerp.osv import fields, osv
from openerp.tools.translate import _

class wo_task_inspection_photo(osv.osv_memory):
    _name = 'wo.task.inspection.photo'
    _description = 'Inspection Point Photo'

    insPhoto = ""
    
    def get_inspection_point_photo(self, cr, uid, context=None):
        if context is None:
            context = {}
        
        inspection_point = self.pool.get('spec.inspection.points').browse(cr, uid, context.get('active_ids', [])[0])
        if inspection_point.image:
            return inspection_point.image
        #else:
         #   raise osv.except_osv(_('Invalid Action!'), _("No Inspection image available !"))

    _columns = {
        'inspection_point_id': fields.many2one('spec.inspection.points', 'Inspection Point'),
 		'photo': fields.related('inspection_point_id', 'image', type="binary"),
    }

    _defaults = {
        'photo': get_inspection_point_photo,
    }
    
    
    
    def onchange_add_inspection_image(self, cr, uid, ids, photo):
        self.insPhoto = ""
        if photo:
            self.insPhoto = photo        
        return True
    
    def add_inspection_image(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        sip_obj = self.pool.get('spec.inspection.points')
         
        if self.insPhoto:
            #raise osv.except_osv(_('Invalid Action!'), _(str(self.insPhoto)))
            sip_obj.write(cr, uid, context.get('active_ids', [])[0],{'image': self.insPhoto},context=context)
        else:
            sip_obj.write(cr, uid, context.get('active_ids', [])[0],{'image': ""},context=context)
        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: