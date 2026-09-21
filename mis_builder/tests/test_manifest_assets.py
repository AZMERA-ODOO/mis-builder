# Copyright 2026 Azmera Consulting
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from pathlib import Path

from odoo.modules.module import get_manifest, get_module_path
from odoo.tests.common import TransactionCase, tagged


@tagged("mis_builder", "post_install")
class TestMisBuilderManifestAssets(TransactionCase):
    def test_manifest_uses_existing_owl_template_asset(self):
        manifest = get_manifest("mis_builder")
        module_path = Path(get_module_path("mis_builder"))
        backend_assets = manifest["assets"]["web.assets_backend"]

        self.assertNotIn("qweb", manifest)
        self.assertIn(
            "mis_builder/static/src/components/mis_report_widget.xml",
            backend_assets,
        )
        self.assertTrue(
            (module_path / "static/src/components/mis_report_widget.xml").is_file()
        )
