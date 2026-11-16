# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
"""Report-instance fixture shared by the integration tests."""

import odoo.tests.common as common

from ..models.mis_report import TYPE_STR


class MisReportInstanceCase(common.HttpCase):
    def setUp(self):
        super().setUp()
        # Odoo 19 test users no longer expose ``res.users.tz`` in this suite.
        # Keep date computations deterministic through the supported context.
        self.env = self.env(context=dict(self.env.context, tz="UTC"))
        partner_model_id = self.env.ref("base.model_res_partner").id
        partner_create_date_field_id = self.env.ref(
            "base.field_res_partner__create_date"
        ).id
        partner_debit_field_id = self.env.ref("account.field_res_partner__debit").id
        # create a report with 2 subkpis and one query
        self.report = self.env["mis.report"].create(
            dict(
                name="test report",
                subkpi_ids=[
                    (0, 0, dict(name="sk1", description="subkpi 1", sequence=1)),
                    (0, 0, dict(name="sk2", description="subkpi 2", sequence=2)),
                ],
                query_ids=[
                    (
                        0,
                        0,
                        dict(
                            name="partner",
                            model_id=partner_model_id,
                            field_ids=[(4, partner_debit_field_id, None)],
                            date_field=partner_create_date_field_id,
                            aggregate="sum",
                        ),
                    )
                ],
            )
        )
        # create another report with 2 subkpis, no query
        self.report_2 = self.env["mis.report"].create(
            dict(
                name="another test report",
                subkpi_ids=[
                    (
                        0,
                        0,
                        dict(
                            name="subkpi1_report2",
                            description="subkpi 1, report 2",
                            sequence=1,
                        ),
                    ),
                    (
                        0,
                        0,
                        dict(
                            name="subkpi2_report2",
                            description="subkpi 2, report 2",
                            sequence=2,
                        ),
                    ),
                ],
            )
        )
        # Third report, 2 subkpis, no query
        self.report_3 = self.env["mis.report"].create(
            dict(
                name="test report 3",
                subkpi_ids=[
                    (
                        0,
                        0,
                        dict(
                            name="subkpi1_report3",
                            description="subkpi 1, report 3",
                            sequence=1,
                        ),
                    ),
                    (
                        0,
                        0,
                        dict(
                            name="subkpi2_report3",
                            description="subkpi 2, report 3",
                            sequence=2,
                        ),
                    ),
                ],
            )
        )
        # kpi with accounting formulas
        self.kpi1 = self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report.id,
                description="kpi 1",
                name="k1",
                multi=True,
                expression_ids=[
                    (
                        0,
                        0,
                        dict(name="bale[200%]", subkpi_id=self.report.subkpi_ids[0].id),
                    ),
                    (
                        0,
                        0,
                        dict(name="balp[200%]", subkpi_id=self.report.subkpi_ids[1].id),
                    ),
                ],
            )
        )
        # kpi with accounting formula and query
        self.kpi2 = self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report.id,
                description="kpi 2",
                name="k2",
                multi=True,
                expression_ids=[
                    (
                        0,
                        0,
                        dict(name="balp[200%]", subkpi_id=self.report.subkpi_ids[0].id),
                    ),
                    (
                        0,
                        0,
                        dict(
                            name="partner.debit", subkpi_id=self.report.subkpi_ids[1].id
                        ),
                    ),
                ],
            )
        )
        # kpi with a simple expression summing other multi-valued kpis
        self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report.id,
                description="kpi 4",
                name="k4",
                multi=False,
                expression="k1 + k2 + k3",
            )
        )
        # kpi with 2 constants
        self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report.id,
                description="kpi 3",
                name="k3",
                multi=True,
                expression_ids=[
                    (
                        0,
                        0,
                        dict(
                            name="AccountingNone",
                            subkpi_id=self.report.subkpi_ids[0].id,
                        ),
                    ),
                    (0, 0, dict(name="1.0", subkpi_id=self.report.subkpi_ids[1].id)),
                ],
            )
        )
        # kpi with a NameError (x not defined)
        self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report.id,
                description="kpi 5",
                name="k5",
                multi=True,
                expression_ids=[
                    (0, 0, dict(name="x", subkpi_id=self.report.subkpi_ids[0].id)),
                    (0, 0, dict(name="1.0", subkpi_id=self.report.subkpi_ids[1].id)),
                ],
            )
        )
        # string-type kpi
        self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report.id,
                description="kpi 6",
                name="k6",
                multi=True,
                type=TYPE_STR,
                expression_ids=[
                    (0, 0, dict(name='"bla"', subkpi_id=self.report.subkpi_ids[0].id)),
                    (
                        0,
                        0,
                        dict(name='"blabla"', subkpi_id=self.report.subkpi_ids[1].id),
                    ),
                ],
            )
        )
        # kpi that references another subkpi by name
        self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report.id,
                description="kpi 7",
                name="k7",
                multi=True,
                expression_ids=[
                    (0, 0, dict(name="k3.sk1", subkpi_id=self.report.subkpi_ids[0].id)),
                    (0, 0, dict(name="k3.sk2", subkpi_id=self.report.subkpi_ids[1].id)),
                ],
            )
        )
        # Report 2 : kpi with AccountingNone value
        self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report_2.id,
                description="AccountingNone kpi",
                name="AccountingNoneKPI",
                multi=False,
            )
        )
        # Report 2 : 'classic' kpi with values for each sub-KPI
        self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report_2.id,
                description="Classic kpi",
                name="classic_kpi_r2",
                multi=True,
                expression_ids=[
                    (
                        0,
                        0,
                        dict(
                            name="bale[200%]", subkpi_id=self.report_2.subkpi_ids[0].id
                        ),
                    ),
                    (
                        0,
                        0,
                        dict(
                            name="balp[200%]", subkpi_id=self.report_2.subkpi_ids[1].id
                        ),
                    ),
                ],
            )
        )
        # Report 3 : kpi with wrong tuple length
        self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report_3.id,
                description="Wrong tuple length kpi",
                name="wrongTupleLen",
                multi=False,
                expression="('hello', 'does', 'this', 'work')",
            )
        )
        # Report 3 : 'classic' kpi
        self.env["mis.report.kpi"].create(
            dict(
                report_id=self.report_3.id,
                description="Classic kpi",
                name="classic_kpi_r2",
                multi=True,
                expression_ids=[
                    (
                        0,
                        0,
                        dict(
                            name="bale[200%]", subkpi_id=self.report_3.subkpi_ids[0].id
                        ),
                    ),
                    (
                        0,
                        0,
                        dict(
                            name="balp[200%]", subkpi_id=self.report_3.subkpi_ids[1].id
                        ),
                    ),
                ],
            )
        )
        # create a report instance
        self.report_instance = self.env["mis.report.instance"].create(
            dict(
                name="test instance",
                report_id=self.report.id,
                company_id=self.env.ref("base.main_company").id,
                period_ids=[
                    (
                        0,
                        0,
                        dict(
                            name="p1",
                            mode="relative",
                            type="d",
                            subkpi_ids=[(4, self.report.subkpi_ids[0].id, None)],
                        ),
                    ),
                    (
                        0,
                        0,
                        dict(
                            name="p2",
                            mode="fix",
                            manual_date_from="2014-01-01",
                            manual_date_to="2014-12-31",
                        ),
                    ),
                ],
            )
        )
        # same for report 2
        self.report_instance_2 = self.env["mis.report.instance"].create(
            dict(
                name="test instance 2",
                report_id=self.report_2.id,
                company_id=self.env.ref("base.main_company").id,
                period_ids=[
                    (
                        0,
                        0,
                        dict(
                            name="p3",
                            mode="fix",
                            manual_date_from="2019-01-01",
                            manual_date_to="2019-12-31",
                        ),
                    )
                ],
            )
        )
        # and for report 3
        self.report_instance_3 = self.env["mis.report.instance"].create(
            dict(
                name="test instance 3",
                report_id=self.report_3.id,
                company_id=self.env.ref("base.main_company").id,
                period_ids=[
                    (
                        0,
                        0,
                        dict(
                            name="p4",
                            mode="fix",
                            manual_date_from="2019-01-01",
                            manual_date_to="2019-12-31",
                        ),
                    )
                ],
            )
        )
