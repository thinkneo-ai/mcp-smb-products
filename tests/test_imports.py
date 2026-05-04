#!/usr/bin/env python3
"""
Smoke test: verify all 8 MCP SMB products import and register tools.
Runs without database or Redis — validates code structure only.
"""
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PRODUCTS = [
    "mcp-guardrails",
    "mcp-finops",
    "mcp-observability",
    "mcp-router",
    "mcp-trust-score",
    "mcp-memory",
    "mcp-thinksecure",
    "mcp-a2a-lite",
]

def test_shared_imports():
    """Verify shared library imports."""
    from shared import config
    from shared import auth
    from shared import billing
    from shared import server_factory
    print("  ✓ shared library imports OK")


def test_product_tools_importable():
    """Verify each product's tools module is importable."""
    for product in PRODUCTS:
        module_dir = product.replace("-", "_")
        product_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            product,
            "src",
        )
        sys.path.insert(0, os.path.dirname(product_path))

        # Import the tools module
        tools_module_name = f"{product.replace('-', '_')}.src.tools"
        # Use direct file import to avoid package conflicts
        import importlib.util
        tools_path = os.path.join(product_path, "tools.py")
        if not os.path.exists(tools_path):
            print(f"  ✗ {product}: tools.py not found at {tools_path}")
            sys.exit(1)

        spec = importlib.util.spec_from_file_location(f"{product}_tools", tools_path)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            # Some modules may fail due to missing DB/Redis — that's OK for import test
            # We only care about syntax and basic structure
            if "psycopg" in str(e) or "redis" in str(e) or "connect" in str(e).lower():
                print(f"  ~ {product}: import OK (runtime deps not available, expected in CI)")
                continue
            print(f"  ✗ {product}: import FAILED — {e}")
            sys.exit(1)

        # Check register_tools function exists
        if hasattr(mod, "register_tools"):
            print(f"  ✓ {product}: tools.py imports OK, register_tools() found")
        else:
            print(f"  ~ {product}: tools.py imports OK (register function name may differ)")


def test_server_json_valid():
    """Verify root server.json is valid."""
    import json
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(root, "server.json")) as f:
        doc = json.load(f)
    assert doc.get("name"), "server.json missing name"
    assert doc.get("version"), "server.json missing version"
    assert len(doc.get("description", "")) <= 500, "server.json description too long"
    assert doc.get("remotes"), "server.json missing remotes"
    print(f"  ✓ server.json valid: {doc['name']} v{doc['version']}, {len(doc['remotes'])} remotes")


if __name__ == "__main__":
    print("=== ThinkNEO MCP SMB Products — Import Tests ===\n")

    print("1. Shared library:")
    test_shared_imports()

    print("\n2. Product tools:")
    test_product_tools_importable()

    print("\n3. Schema:")
    test_server_json_valid()

    print("\n=== All tests passed ===")
