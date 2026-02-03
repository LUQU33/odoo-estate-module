from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"
    _sql_constraints = [
        ("name_unique", "UNIQUE(name)", "The property type name must be unique.")
    ]

    name = fields.Char(required=True)
