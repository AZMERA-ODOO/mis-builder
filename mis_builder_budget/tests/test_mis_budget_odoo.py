from odoo.tests.common import TransactionCase

from odoo.addons.mis_builder.tests.common import assert_matrix

from ..models.mis_budget_odoo import SRC_ODOO_BUDGET


class TestMisBudgetOdoo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account = cls.env["account.account"].search(
            [("account_type", "=", "expense"), ("company_ids", "in", cls.env.company.id)],
            limit=1,
        )
        if not cls.account:
            raise AssertionError("The test database must provide an expense account.")
        cls.plan = cls.env["account.analytic.plan"].create({"name": "MIS Budget Plan"})
        cls.analytic = cls.env["account.analytic.account"].create(
            {
                "name": "MIS Budget Analytic",
                "company_id": cls.env.company.id,
                "plan_id": cls.plan.id,
            }
        )
        cls.budget = cls.env["account.report.budget"].create(
            {
                "name": "MIS Odoo Budget",
                "company_id": cls.env.company.id,
            }
        )
        cls.item = cls.env["account.report.budget.item"].create(
            {
                "budget_id": cls.budget.id,
                "account_id": cls.account.id,
                "analytic_account_id": cls.analytic.id,
                "date": "2026-01-15",
                "amount": 42.0,
            }
        )
        cls.report = cls.env["mis.report"].create({"name": "MIS Odoo Budget Report"})
        cls.kpi = cls.env["mis.report.kpi"].create(
            {
                "report_id": cls.report.id,
                "name": "budget_income",
                "description": "Odoo budget income",
                "expression": "balp[('id', '=', %s)]" % cls.account.id,
            }
        )
        cls.instance = cls.env["mis.report.instance"].create(
            {"name": "MIS Odoo Budget Instance", "report_id": cls.report.id}
        )
        cls.period = cls.env["mis.report.instance.period"].create(
            {
                "name": "Budget January",
                "report_instance_id": cls.instance.id,
                "source": SRC_ODOO_BUDGET,
                "source_odoo_budget_id": cls.budget.id,
                "manual_date_from": "2026-01-01",
                "manual_date_to": "2026-01-31",
            }
        )

    def test_budget_item_has_mis_move_line_shape(self):
        self.assertEqual(self.item.debit, 42.0)
        self.assertEqual(self.item.credit, 0.0)
        self.assertEqual(self.item.company_id, self.env.company)
        self.assertEqual(self.item.analytic_account_id, self.analytic)

    def test_odoo_budget_is_a_mis_period_source(self):
        self.assertEqual(self.period.source_aml_model_name, "account.report.budget.item")
        self.assertEqual(self.period.source_odoo_budget_id, self.budget)
        assert_matrix(self.instance._compute_matrix(), [[42.0]])
