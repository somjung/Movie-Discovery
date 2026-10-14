"""Round-close mechanical import audit (rules R1-R6) for the Sprint 4 code.

Usage:  python layer_check.py [path/to/src]
Default: ../script-final-project/src (relative to this file).

Checks every module in ``src/`` against the project's layer conventions:

R1/R3  no module imports a module from a layer above it
R2     business-layer modules do not import data-layer services
       (constructor injection only); the only allowed import is an
       exception class defined in the data module
R4     ``requests`` only in the two external-service clients
       (tmdb_client, ai_client)              [Sprint 4 adjustment]
R5     ``sqlite3`` only in movie_store, ``csv`` only in exporter,
       ``json`` only in the JSON-touching modules
       (tmdb_client, ai_client, ai_advisor)  [Sprint 4 adjustment]
R6     no import cycles among the analysed modules

Prints one line per module, the rule summary, and the internal import
edges (so every borderline case stays visible).  Exit code 0 = pass.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

PRESENTATION = {"app", "cli"}
BUSINESS = {"discovery", "watchlist", "ai_advisor"}
DATA = {"tmdb_client", "movie_store", "exporter", "sample_data", "ai_client"}
SHARED = {"config"}
EXPECTED = PRESENTATION | BUSINESS | DATA | SHARED

RANK = {}
RANK.update({name: 3 for name in PRESENTATION})
RANK.update({name: 2 for name in BUSINESS})
RANK.update({name: 1 for name in DATA})
RANK.update({name: 0 for name in SHARED})

ALLOWED_LIBS = {
    "requests": {"tmdb_client", "ai_client"},
    "sqlite3": {"movie_store"},
    "csv": {"exporter"},
    "json": {"tmdb_client", "ai_client", "ai_advisor"},
}


def parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def relative_imports(tree: ast.Module) -> list[tuple[str, list[str], int]]:
    """[(target_module, imported_names, lineno)] for relative imports."""
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level:
            if node.module:
                names = [alias.name for alias in node.names]
                found.append((node.module.split(".")[0], names, node.lineno))
            else:
                for alias in node.names:
                    found.append((alias.name.split(".")[0], [], node.lineno))
    return found


def absolute_imports(tree: ast.Module) -> list[tuple[str, int]]:
    """[(top_level_module, lineno)] for non-relative imports."""
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.append((alias.name.split(".")[0], node.lineno))
        elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
            found.append((node.module.split(".")[0], node.lineno))
    return found


def exception_class_names(path: Path) -> set[str]:
    """Names of classes in this module that subclass Exception."""
    bases = {}
    for node in parse(path).body:
        if isinstance(node, ast.ClassDef):
            parents = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    parents.append(base.id)
                elif isinstance(base, ast.Attribute):
                    parents.append(base.attr)
                else:
                    parents.append("")
            bases[node.name] = parents
    result = set()
    changed = True
    while changed:
        changed = False
        for name, parents in bases.items():
            if name in result:
                continue
            if any(p == "Exception" or p in result for p in parents):
                result.add(name)
                changed = True
    return result


def reaches(graph: dict[str, list[str]], start: str, target: str) -> bool:
    stack, seen = [start], set()
    while stack:
        node = stack.pop()
        if node == target:
            return True
        if node in seen:
            continue
        seen.add(node)
        stack.extend(graph.get(node, ()))
    return False


def layer_of(name: str) -> str:
    if name in PRESENTATION:
        return "presentation"
    if name in BUSINESS:
        return "business"
    if name in DATA:
        return "data"
    if name in SHARED:
        return "shared"
    return "unknown"


def main() -> int:
    here = Path(__file__).resolve().parent
    default_src = here.parent / "script-final-project" / "src"
    src = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else default_src
    paths = {p.stem: p for p in sorted(src.glob("*.py"))
             if p.stem != "__init__"}

    print(f"== mechanical import audit (R1-R6) -- {src}")
    print(f"modules found: {len(paths)} -> {', '.join(sorted(paths))}")
    missing = sorted(EXPECTED - set(paths))
    unknown = sorted(set(paths) - EXPECTED)
    if missing:
        print(f"!! expected but missing: {missing}")
    if unknown:
        print(f"!! not mapped to a layer: {unknown}")

    trees = {name: parse(path) for name, path in paths.items()}
    rel = {name: relative_imports(tree) for name, tree in trees.items()}
    absl = {name: absolute_imports(tree) for name, tree in trees.items()}
    graph = {name: sorted({target for target, _, _ in rel[name]
                           if target in paths}) for name in paths}

    results: list[tuple[str, bool, str]] = []

    def record(label: str, ok: bool, detail: str = "") -> bool:
        results.append((label, ok, detail))
        return ok

    print("\n-- A. direction: no module imports a layer above it --")
    for name in sorted(paths):
        upper = [t for t in graph[name] if RANK[t] > RANK[name]]
        ok = record(f"A direction: {name}", not upper,
                    f"upward: {upper}" if upper else "")
        imports_text = ", ".join(graph[name]) or "-"
        print(f"   {name:13s} ({layer_of(name):12s}) imports: "
              f"{imports_text}  [{'PASS' if ok else 'FAIL'}]")

    print("\n-- B. business layer: data services injected, "
          "only exception classes importable --")
    for name in sorted(BUSINESS & set(paths)):
        bad, notes = [], []
        for target, names, line in rel[name]:
            if target not in DATA:
                continue
            allowed_names = exception_class_names(paths[target])
            offenders = [n for n in names if n not in allowed_names]
            if not names or offenders:
                bad.append(f"imports {target} (line {line})")
            else:
                notes.append(f"{target}.{', '.join(names)}")
        ok = record(f"B business: {name}", not bad, "; ".join(bad))
        tail = (" (allowed error class: " + ", ".join(notes) + ")"
                if notes else "")
        print(f"   {name:13s}: {'PASS' if ok else 'FAIL - ' + '; '.join(bad)}"
              f"{tail}")

    print("\n-- C. external libraries only in their home modules --")
    for lib, allowed in ALLOWED_LIBS.items():
        users = {name for name in paths
                 if any(mod == lib for mod, _ in absl[name])}
        extra = sorted(users - allowed)
        ok = record(f"C lib {lib}:", not extra,
                    f"extra users: {extra}" if extra else "")
        print(f"   {lib:8s} used by: {', '.join(sorted(users)) or '-'}"
              f"  [{'PASS' if ok else 'FAIL'}]")

    print("\n-- D. import cycles --")
    cycles = [(u, v) for u in sorted(graph) for v in graph[u]
              if v == u or reaches(graph, v, u)]
    record("D cycles", not cycles, str(cycles) if cycles else "")
    print(f"   cycles: {cycles or '-'}  "
          f"[{'PASS' if not cycles else 'FAIL'}]")

    edges = sum(len(graph[name]) for name in graph)
    ext = sum(len(absl[name]) for name in absl)
    print(f"\n-- internal edges ({edges}) / external imports ({ext}) --")
    for name in sorted(graph):
        if graph[name]:
            print(f"   {name} -> {', '.join(graph[name])}")

    total = len(results)
    passed = sum(1 for _, ok, _ in results if ok)
    fails = [(label, detail) for label, ok, detail in results if not ok]
    any_upward = any(
        not ok for label, ok, _ in results if label.startswith("A "))
    business_ok = all(ok for label, ok, _ in results
                      if label.startswith("B "))
    cycles_ok = all(ok for label, ok, _ in results
                    if label.startswith("D "))
    lib_ok = {
        lib: all(ok for label, ok, _ in results
                 if label.startswith(f"C lib {lib}:"))
        for lib in ALLOWED_LIBS
    }

    print("\n== summary ==")
    print(f"R1/R3 direction (11 modules): "
          f"{'PASS' if not any_upward else 'FAIL'}")
    print(f"R2 business strictness: {'PASS' if business_ok else 'FAIL'}")
    print(f"R4 requests -> tmdb_client, ai_client: "
          f"{'PASS' if lib_ok['requests'] else 'FAIL'}")
    print(f"R5 sqlite3 / csv / json placement: "
          f"{'PASS' if all(lib_ok[lib] for lib in ('sqlite3', 'csv', 'json')) else 'FAIL'}")
    print(f"R6 no cycles: {'PASS' if cycles_ok else 'FAIL'}")
    print(f"individual checks passed: {passed}/{total}")
    if fails:
        print("failed checks:")
        for label, detail in fails:
            print(f"   - {label} {detail}")
    return 0 if not fails and not missing and not unknown else 1


if __name__ == "__main__":
    raise SystemExit(main())
