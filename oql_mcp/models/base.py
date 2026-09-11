import logging

from odoo import models, api
from odoo.addons.mcp_base import mcp_tool

_logger = logging.getLogger(__name__)


class OqlMcpBase(models.AbstractModel):
    _inherit = "base"

    @mcp_tool
    @api.model
    def oql_mcp_query(self, oql: str):
        """Execute OQL search and return records as dicts.
        Attention: You must use LIMIT clause for any query. Use offset together with limit if you need paginated result.

        OQL is a PostgreSQL-like query language for Odoo. It supports dot paths (e.g., `company.name`) and virtual fields (Terms/Aliases).
        OQL Structure: FROM <model> SELECT <fields> WHERE <conditions> [ORDER BY <field> [ASC|DESC], ...] [LIMIT n] [OFFSET n]
        Differences from SQL:
            1. FROM clause is placed at start of a query string.
            2. It uses Odoo domain operators such as 'like', '=like', etc. Be careful about this!!!
                Don't add `%` in comparison string when use operator `like`, `ilike`. If you need to use `%`,
                use `=like`, `=ilike` operator instead.
            3. `id` field will be added to result automatically.
        OQL Example:
            FROM product.product
            SELECT name, default_code, tag_ids.name
            WHERE Brand = 'Danner' and Waterproof and list_price > 1000
            ORDER BY name ASC
            LIMIT 80
            OFFSET 160
        Use `oql_mcp_hint` to find out valid model and field you have access to, or valid candidate values for a field.

        :return: List of record dictionaries.
        """
        return self.oql(oql)

    @mcp_tool
    @api.model
    def oql_mcp_hint(self, hintable_oql: str, verbose: int = 0):
        """Hint OQL at specified hint points.
        :param hintable_oql: Partial OQL with hint points.
          Grammar: 'Partial OQL ?hint_options'
            hint_options: A JSON dict that contains keys:
              name: str. Name for the hint point. It will be used as key in hint result.
              keywords: List[str]. A list of keywords used search for possible candidates.
              limit: int. Max hint count.
              offset: Optional[int]. Used for paging when there are too many hint items.
          e.g.  'FROM product.product SELECT ?{"name": "sel_field", "keywords": ["code", "de"], "limit": 10}'
                'FROM product.?{"name": "model", "keywords": ["te"], "limit": 5}'
                'FROM product.product SELECT id where default_code like ?{"name": "default_code", "keywords": ["danner"], "limit": 40}'
          * Note: hint point can only be placed at the end of a partial OQL.
        :return: {hint_point_name: {hints: [{type: ..., value: ..., desc: ...}]}}
        :param verbose: Verbosity level of hints. Use lower level as priority.
            - 0: list of candidate strings. e.g. ['name', ...]
            - 1: list of candidate dict with value, description. e.g. [{'value': 'name', 'desc': 'Product Name'}, ...]
            - 2: list of candidate dict with value, description, type. e.g. [{'value': 'name', 'desc': 'Product Name', 'type': 'field'}, ...]
        """
        hintx = self.oql_hintx(hintable_oql)
        # Align hint verbosity with `verbose` parameter.
        for obj in hintx.values():
            hints = obj["hints"]
            if verbose == 0:
                hints = [x["value"] for x in hints]
            elif verbose == 1:
                hints = [{
                    "value": x["value"],
                    "desc": x["desc"],
                } for x in hints]
            obj["hints"] = hints
        return hintx
