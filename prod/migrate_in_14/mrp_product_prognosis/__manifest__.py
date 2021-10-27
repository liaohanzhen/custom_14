# -*- coding: utf-8 -*-
{
    "name": "MRP Potential",
    "version": "14.0.1.0.2",
    "category": "Manufacturing",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/12.0/mrp-potential-11",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "mrp"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_view.xml"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "summary": "The tool to always know how much our production may promise",
    "description": """
    The app goal is to provide you and your clients with up-to-date information about:
<ul style="font-size:18px">
<li>How many products we may produce at the moment based on available components: <strong>MRP Potential</strong></li>
<li>What a component is of the most need and restricts us to produce more at the moment: <strong>Bottleneck component</strong></li>
<li>How many products we may produce in the future depending on virtual stocks planned by purchases or manufacturing: <strong>MRP forecast</strong></li>
</ul>

    The figures are calculated in real-time as soon as you decided to look at the indicators
    The figures are calculated for product variants (<i>not templates!</i>)
    The app supports bill of materials hierarchy. Thus, it let you assume how many of "X" may be produced if it is made of "Y", while "Y" is made of "Z", and we have 5 of "Y" and 10 of "Z" in stocks
    <i>Services</i> and <i>consumbale products</i> of bills of materials are not included into calculations.
    The module is fully compatible with other Odoo MRP apps. The app will be functioning with existing products and bills of materials. Just install it and start working
    # Use Case
        <ol>
     <li class="oe_mt16">
      Imagine, your product is "Ice cream, Chocolate" (5kg can)
     </li>
     <li class="oe_mt16">
      According to the bill of material it is produced of "Milk" (5kg) and "Chocolate" (1 kg)
     </li>
     <li class="oe_mt16">
      We have on stocks 20 kg of "Milk" and 2 kg of "Chocolate"
     </li>
     <li class="oe_mt16">
      <i class="fa fa-arrow-right">
      </i>
      Currently we may produce two cans of "Ice cram, Chocolate", taking 10 kg of "Milk" and 2 kg of "Chocolate". It is
      <strong>
       MRP potential
      </strong>
      . Since we have 10 kg more "Milk", but no more "Chocolate", the latter is
      <strong>
       Bottleneck component
      </strong>
     </li>
     <li class="oe_mt16">
      We also ordered from supplier 10 kg of "Chocolate" and planning to get it in 5 days (confirmed purchase order with the linked picking of the type "Receipt")
     </li>
     <li class="oe_mt16">
      <i class="fa fa-arrow-right">
      </i>
      So, in 5 days we anticipate 10 kg of "Chocolate". Taking into account 10 kg of "Milk" left in stocks, we will be able to produce 2 extra "Ice cream" cans. Or 4 cans together with MRP potential. This 4 is
      <strong>
       MRP forecast
      </strong>
     </li>
    </ol>
    MRP Potential indicators for product variants
    Bill of Material (first level)
    Bill of Material (second level of hierarchy)
    Components' inventory current ad forecast levels
""",
    "images": [
        "static/description/main.png"
    ],
    "price": "36.0",
    "currency": "EUR",
}