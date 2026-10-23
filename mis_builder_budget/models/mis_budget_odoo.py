"""Expose standard Odoo report budgets as a MIS Builder source."""

from odoo import api, fields, models


SRC_ODOO_BUDGET = "odoo_budget"
ODOO_BUDGET_ITEM_MODEL = "account.report.budget.item"


class AccountReportBudgetItem(models.Model):
    """Give standard budget items the move-line shape MIS Builder queries."""

    _inherit = ODOO_BUDGET_ITEM_MODEL

    debit = fields.Float(compute="_compute_mis_amounts", store=True)
    credit = fields.Float(compute="_compute_mis_amounts", store=True)
    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Analytic Account",
        index=True,
    )
    company_id = fields.Many2one(
        related="budget_id.company_id", store=True, index=True, readonly=True
    )
    @api.depends("amount")
    def _compute_mis_amounts(self):
        for item in self:
            item.debit = item.amount if item.amount > 0 else 0.0
            item.credit = -item.amount if item.amount < 0 else 0.0


class MisReportInstancePeriod(models.Model):
    _inherit = "mis.report.instance.period"

    source = fields.Selection(
        selection_add=[(SRC_ODOO_BUDGET, "Odoo Budget")],
        ondelete={SRC_ODOO_BUDGET: "cascade"},
    )
    source_odoo_budget_id = fields.Many2one(
        "account.report.budget",
        string="Odoo Budget",
        help="Approved Odoo report budget used for this MIS column.",
    )

    @api.depends("source")
    def _compute_source_aml_model_id(self):
        super()._compute_source_aml_model_id()
        budget_item_model = (
            self.env["ir.model"]
            .sudo()
            .search([("model", "=", ODOO_BUDGET_ITEM_MODEL)], limit=1)
        )
        for record in self.filtered(lambda period: period.source == SRC_ODOO_BUDGET):
            record.source_aml_model_id = budget_item_model

    def _get_additional_move_line_filter(self):
        domain = super()._get_additional_move_line_filter()
        if self.source == SRC_ODOO_BUDGET:
            domain.append(("budget_id", "=", self.source_odoo_budget_id.id))
        return domain
