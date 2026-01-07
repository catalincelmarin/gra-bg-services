from urllib.parse import parse_qsl
import re

class MCPHelpers:
    _num_re = re.compile(r"^-?\d+$")

    @staticmethod
    def _is_int_str(s: str) -> bool:
        return bool(MCPHelpers._num_re.match(s))

    @staticmethod
    def _coerce_scalar(v: str):
        v_stripped = v.strip()
        if v_stripped == "true":  return True
        if v_stripped == "false": return False
        if v_stripped == "null":  return None
        if v_stripped == "":      return ""
        if MCPHelpers._is_int_str(v_stripped):
            try:
                return int(v_stripped)
            except Exception:
                pass
        # very light float detection
        if "." in v_stripped and not v_stripped.startswith("{") and not v_stripped.startswith("["):
            try:
                return float(v_stripped)
            except Exception:
                pass
        return v

    @staticmethod
    def _insert_path(root: dict, parts: list[str], value: str):
        """
        Insert value into a dict-only tree.
        Numeric segments are kept as STRING KEYS for now.
        """
        cur = root
        for i, part in enumerate(parts):
            last = (i == len(parts) - 1)
            if last:
                # write scalar at leaf
                cur[part] = MCPHelpers._coerce_scalar(value)
                return
            # ensure next container exists and is a dict
            nxt = parts[i + 1]
            if part not in cur or not isinstance(cur[part], dict):
                cur[part] = {}
            cur = cur[part]

    @staticmethod
    def _normalize(node):
        """
        Recursively convert dicts that look like arrays (keys '0'..'n-1')
        into Python lists, and normalize children.
        """
        if isinstance(node, dict):
            # First normalize children
            for k in list(node.keys()):
                node[k] = MCPHelpers._normalize(node[k])

            # Check if keys are an array index set
            if node and all(MCPHelpers._is_int_str(k) for k in node.keys()):
                # are keys contiguous from 0..n-1?
                idxs = sorted(int(k) for k in node.keys())
                if idxs and idxs == list(range(0, idxs[-1] + 1)):
                    return [node[str(i)] for i in idxs]
            return node

        if isinstance(node, list):
            return [MCPHelpers._normalize(x) for x in node]

        # scalar
        return node

    @staticmethod
    def querystring_to_dict(qs: str) -> dict:
        """
        Parse a Strapi/qs-style query string into a nested dict/list structure.
        Strategy:
          1) Build a dict-only tree using bracket parts as keys (including numeric indices as strings).
          2) Normalize dicts with numeric, contiguous keys into lists.
        """
        # Step 1: dict-only build
        root: dict = {}
        for raw_key, raw_val in parse_qsl(qs, keep_blank_values=True):
            # "a[b][0][c]" -> ["a","b","0","c"]
            parts = re.findall(r'([^\[\]]+)', raw_key)
            if not parts:
                continue
            MCPHelpers._insert_path(root, parts, raw_val)

        # Step 2: convert array-like dicts into lists
        return MCPHelpers._normalize(root)
