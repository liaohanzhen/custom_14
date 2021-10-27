# -*- coding: utf-8 -*-
{
  "name"                 :  "Frogblue Google Analytics",
  "summary"              :  """The module integrates Odoo with Google Tag Manager so you can send the customer behaviour data from Odoo website to Google analytics.""",
  "category"             :  "Website",
  "version"              :  "1.0.2",
  "sequence"             :  1,
  "author"               :  "Nilesh Sheliya",
  "license"              :  "Other proprietary",
  "website"              :  "https://sheliyainfotech.com",
  "description"          :  """Google Analytics
Track customer behaviour on website""",
  "depends"              :  ['website_sale'],
  "data"                 :  [
                             'views/res_config_settings_views.xml',
                             'views/snippets_template.xml',
                            ],
  "application"          :  True,
}
