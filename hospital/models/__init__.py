from . import appointment
from . import book_category
from . import doctor
from . import lab
from . import patient
from . import settings
from . import purchase_report



# results = self.env['crm.lead.convert2task'].read_group([('project_id', 'in', self.ids)], ['project_id'], 'project_id')
# dic = {}
# for x in results:
#     dic[x['project_id'][0]] = x['project_id_count']
# for record in self:
#     record['x_project_id__crm_lead_convert2task_count'] = dic.get(record.id, 0)
