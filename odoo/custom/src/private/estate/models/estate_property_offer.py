from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(
        selection=[("accepted", "Accepted"), ("refused", "Refused")], copy=False
    )

    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)

    validity = fields.Integer(default=7, string="Validity (days)")

    date_deadline = fields.Date(
        string="Deadline",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
    )

    @api.model
    def create(self, vals):
        if vals.get("property_id"):
            property_obj = self.env["estate.property"].browse(vals["property_id"])

            if property_obj.offer_ids:
                max_offer = max(property_obj.offer_ids.mapped("price"))
                if vals.get("price") < max_offer:
                    raise UserError(_("The offer must be higher than %2.f") % max_offer)

            property_obj.state = "offer_received"

        return super().create(vals)

    @api.depends("validity", "create_date")
    def _compute_date_deadline(self):
        for record in self:
            date = (
                record.create_date.date() if record.create_date else fields.Date.today()
            )

            record.date_deadline = date + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            date = (
                record.create_date.date() if record.create_date else fields.Date.today()
            )
            if record.date_deadline:
                record.validity = (record.date_deadline - date).days

    def action_accept(self):
        for record in self:
            if record.status == "refused":
                raise UserError(_("Refused offers cannot be accepted"))

            if record.property_id.state == "offer_accepted":
                raise UserError(
                    _("You cannot accept an offer for a property that is already sold")
                )

            (record.property_id.offer_ids - record).write({"status": "refused"})

            record.status = "accepted"

            record.property_id.write(
                {
                    "state": "offer_accepted",
                    "selling_price": record.price,
                    "buyer_id": record.partner_id.id,
                }
            )
        return True

    def action_refuse(self):
        for record in self:
            if record.status == "accepted":
                raise UserError(_("Accepted offers cannot be refused"))
            record.status = "refused"
        return True
