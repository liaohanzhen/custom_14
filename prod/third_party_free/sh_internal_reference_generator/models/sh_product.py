# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api


class ShProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        res = super(ShProduct, self).create(vals)
        if self.env.company and self.env.company.sh_product_int_ref_generator and self.env.company.sh_new_product_int_ref_generator:
            product_sequence = ''
            if self.env.company.sh_product_name_config:
                product_name = str(res.name)
                if int(self.env.company.sh_product_name_digit) >= 1:
                    product_name = product_name[:int(
                        self.env.company.sh_product_name_digit)]
                    if " " in product_name:
                        if self.env.company.sh_product_name_separate:
                            product_name = product_name.replace(
                                " ", str(self.env.company.sh_product_name_separate))
                            if self.env.company.sh_product_sequence_separate:
                                product_sequence = product_sequence + \
                                    product_name[:int(self.env.company.sh_product_name_digit)] + str(
                                        self.env.company.sh_product_sequence_separate)
                            else:
                                product_sequence = product_sequence + \
                                    product_name[:int(
                                        self.env.company.sh_product_name_digit)]
                        else:
                            if self.env.company.sh_product_sequence_separate:
                                product_sequence = product_sequence + \
                                    product_name[:int(self.env.company.sh_product_name_digit)] + str(
                                        self.env.company.sh_product_sequence_separate)
                            else:
                                product_sequence = product_sequence + \
                                    product_name[:int(
                                        self.env.company.sh_product_name_digit)]
                    else:
                        if self.env.company.sh_product_sequence_separate:
                            product_sequence = product_sequence + \
                                product_name[:int(self.env.company.sh_product_name_digit)] + str(
                                    self.env.company.sh_product_sequence_separate)
                        else:
                            product_sequence = product_sequence + \
                                product_name[:int(
                                    self.env.company.sh_product_name_digit)]

            if self.env.company.sh_product_attribute_config:
                if int(self.env.company.sh_product_attribute_name_digit) >= 1:
                    if res.product_template_attribute_value_ids:
                        atrributes_name = []
                        for attribute in res.product_template_attribute_value_ids:
                            for value in attribute.product_attribute_value_id:
                                atrributes_name.append(value.name)
                        for atrributes_value in atrributes_name:
                            value = atrributes_value
                            value = value[:int(
                                self.env.company.sh_product_attribute_name_digit)]
                            if " " in value:
                                if self.env.company.sh_product_attribute_name_separate:
                                    value = value.replace(
                                        " ", str(self.env.company.sh_product_attribute_name_separate))
                                    if self.env.company.sh_product_sequence_separate:
                                        product_sequence += value[:int(self.env.company.sh_product_attribute_name_digit)] + str(
                                            self.env.company.sh_product_sequence_separate)
                                    else:
                                        product_sequence += value[:int(
                                            self.env.company.sh_product_attribute_name_digit)]
                                else:
                                    if self.env.company.sh_product_sequence_separate:
                                        product_sequence += value[:int(self.env.company.sh_product_attribute_name_digit)] + str(
                                            self.env.company.sh_product_sequence_separate)
                                    else:
                                        product_sequence += value[:int(
                                            self.env.company.sh_product_attribute_name_digit)]
                            else:
                                if self.env.company.sh_product_sequence_separate:
                                    product_sequence += value[:int(self.env.company.sh_product_attribute_name_digit)] + str(
                                        self.env.company.sh_product_sequence_separate)
                                else:
                                    product_sequence += value[:int(
                                        self.env.company.sh_product_attribute_name_digit)]
            if self.env.company.sh_product_cataegory_config:
                category_name = str(res.categ_id.name)
                if int(self.env.company.sh_product_category_digit) >= 1:
                    category_name = category_name[:int(
                        self.env.company.sh_product_category_digit)]
                    if " " in category_name:
                        if self.env.company.sh_product_catagory_separate:
                            category_name = category_name.replace(
                                " ", str(self.env.company.sh_product_catagory_separate))
                            if self.env.company.sh_product_sequence_separate:
                                product_sequence += category_name[:int(self.env.company.sh_product_category_digit)] + str(
                                    self.env.company.sh_product_sequence_separate)
                            else:
                                product_sequence += category_name[:int(
                                    self.env.company.sh_product_category_digit)]
                        else:
                            if self.env.company.sh_product_sequence_separate:
                                product_sequence += category_name[:int(self.env.company.sh_product_category_digit)] + str(
                                    self.env.company.sh_product_sequence_separate)
                            else:
                                product_sequence += category_name[:int(
                                    self.env.company.sh_product_category_digit)]
                    else:
                        if self.env.company.sh_product_sequence_separate:
                            product_sequence += category_name[:int(self.env.company.sh_product_category_digit)] + str(
                                self.env.company.sh_product_sequence_separate)
                        else:
                            product_sequence += category_name[:int(
                                self.env.company.sh_product_category_digit)]
            if self.env.company.sh_product_sequence_config and self.env.company.sh_product_sequence:
                sequence = self.env['ir.sequence'].next_by_code(self.env.company.sh_product_sequence.code)
                product_sequence += str(sequence)
            if product_sequence.endswith(str(self.env.company.sh_product_sequence_separate)):
                product_sequence = product_sequence[:-1]
            if product_sequence != '':
                res.default_code = product_sequence

        return res
