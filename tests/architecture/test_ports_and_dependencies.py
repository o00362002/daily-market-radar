from __future__ import annotations

import ast
import importlib.util
import inspect
import keyword
import unittest
from pathlib import Path
from typing import Protocol

import radar.ports as ports


ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / "src"
RADAR_ROOT = SRC_ROOT / "radar"


# These signatures are the stable behavioral boundary. Concrete implementations
# may expose more helpers, but application services must only require this surface.
PORT_METHODS: dict[str, dict[str, tuple[str, ...]]] = {
    "SourceAdapter": {
        "credentials_status": ("self",),
        "health_check": ("self",),
        "fetch": ("self", "request"),
        "normalize": ("self", "result"),
    },
    "IntelligenceEvaluator": {
        "evaluate": ("self", "request"),
    },
    "DocumentRepository": {
        "save_documents": ("self", "documents"),
        "get_document": ("self", "document_id"),
        "find_by_canonical_url": ("self", "canonical_url"),
        "find_by_content_hash": ("self", "content_hash"),
        "list_recent_documents": ("self", "since"),
    },
    "EventRepository": {
        "save_event": ("self", "event"),
        "get_event": ("self", "event_id"),
        "find_recent_events": ("self", "since"),
        "attach_documents": ("self", "event_id", "document_ids"),
        "save_event_delta": ("self", "event_id", "delta", "observed_at"),
        "list_event_deltas": ("self", "event_id"),
        "update_last_seen": ("self", "event_id", "last_seen_at"),
        "list_active_events": ("self",),
    },
    "ReportRepository": {
        "save_report": ("self", "report"),
        "get_report": ("self", "report_id"),
        "get_report_by_date": ("self", "report_date", "profile"),
        "get_latest_report": ("self", "profile"),
        "list_reports": ("self", "profile"),
    },
    "IndicatorRepository": {
        "save_indicator_observation": ("self", "observation"),
        "list_indicator_observations": ("self", "indicator_id"),
        "get_rolling_window": ("self", "indicator_id", "days"),
    },
    "StateStore": {
        "load": ("self", "key"),
        "save": ("self", "key", "value"),
    },
    "WebArtifactStore": {
        "read": ("self", "path"),
        "commit": ("self", "artifacts"),
    },
    "ReportPublisher": {
        "publish": ("self", "report", "artifacts"),
    },
}

PORT_ATTRIBUTES: dict[str, set[str]] = {
    "SourceAdapter": {"adapter_id", "source_id", "retry_policy", "rate_limit_policy"},
    "IntelligenceEvaluator": {"evaluator_id"},
    "DocumentRepository": set(),
    "EventRepository": set(),
    "ReportRepository": set(),
    "IndicatorRepository": set(),
    "StateStore": set(),
    "WebArtifactStore": set(),
    "ReportPublisher": {"publisher_id"},
}

APPLICATION_FORBIDDEN_IMPORT_PREFIXES = (
    # Concrete radar implementations belong in the composition root.
    "radar.adapters",
    "radar.artifacts.filesystem",
    "radar.composition",
    "radar.evaluators",
    "radar.infrastructure",
    "radar.publishers",
    "radar.repositories",
    "radar.runtime",
    "radar.stores",
    # Provider, persistence, network and filesystem libraries are infrastructure.
    "aiohttp",
    "glob",
    "http.client",
    "httpx",
    "openai",
    "os",
    "pathlib",
    "requests",
    "shutil",
    "socket",
    "sqlite3",
    "subprocess",
    "tempfile",
    "urllib",
)

RUNTIME_FACADE_FORBIDDEN_IMPORT_PREFIXES = (
    "radar.adapters",
    "radar.repositories",
)


def _is_forbidden(module_name: str, prefixes: tuple[str, ...]) -> bool:
    return any(module_name == prefix or module_name.startswith(f"{prefix}.") for prefix in prefixes)


def _module_name(path: Path) -> str | None:
    """Return a Python import name, excluding backup files such as ``models 2.py``."""

    relative = path.relative_to(SRC_ROOT).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    if not parts or any(not part.isidentifier() or keyword.iskeyword(part) for part in parts):
        return None
    return ".".join(parts)


def _canonical_modules() -> dict[str, Path]:
    modules: dict[str, Path] = {}
    for path in sorted(RADAR_ROOT.rglob("*.py")):
        module_name = _module_name(path)
        if module_name is None:
            continue
        if module_name in modules:
            raise AssertionError(f"duplicate canonical module {module_name}: {modules[module_name]} and {path}")
        modules[module_name] = path
    return modules


def _source_package(module_name: str, path: Path) -> str:
    if path.name == "__init__.py":
        return module_name
    return module_name.rpartition(".")[0]


def _declared_imports(path: Path, module_name: str) -> list[tuple[str, int]]:
    """Return resolved import bases for dependency-policy checks."""

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    package = _source_package(module_name, path)
    imports: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend((alias.name, node.lineno) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                relative_name = f"{'.' * node.level}{node.module or ''}"
                try:
                    imported = importlib.util.resolve_name(relative_name, package)
                except (ImportError, ValueError):
                    continue
            else:
                imported = node.module or ""
            if imported:
                imports.append((imported, node.lineno))
    return imports


def _nearest_module(import_name: str, known_modules: set[str]) -> str | None:
    parts = import_name.split(".")
    while parts:
        candidate = ".".join(parts)
        if candidate in known_modules:
            return candidate
        parts.pop()
    return None


def _module_dependencies(path: Path, module_name: str, known_modules: set[str]) -> set[str]:
    """Resolve internal imports to canonical module nodes for cycle checks."""

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    package = _source_package(module_name, path)
    dependencies: set[str] = set()
    for node in ast.walk(tree):
        candidates: list[str] = []
        if isinstance(node, ast.Import):
            candidates.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                relative_name = f"{'.' * node.level}{node.module or ''}"
                try:
                    base = importlib.util.resolve_name(relative_name, package)
                except (ImportError, ValueError):
                    continue
            else:
                base = node.module or ""
            if not base:
                continue
            # Prefer a real imported submodule (``from package import module``),
            # then fall back to the declared import base for imported symbols.
            submodules = [f"{base}.{alias.name}" for alias in node.names if alias.name != "*"]
            candidates.extend(candidate for candidate in submodules if candidate in known_modules)
            if not any(candidate in known_modules for candidate in submodules):
                candidates.append(base)
        for candidate in candidates:
            if not candidate.startswith("radar"):
                continue
            target = _nearest_module(candidate, known_modules)
            if target is not None and target != module_name:
                dependencies.add(target)
    return dependencies


def _find_cycle(graph: dict[str, set[str]]) -> list[str] | None:
    state: dict[str, int] = {node: 0 for node in graph}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        stack.append(node)
        for target in sorted(graph[node]):
            if state[target] == 0:
                cycle = visit(target)
                if cycle is not None:
                    return cycle
            elif state[target] == 1:
                start = stack.index(target)
                return [*stack[start:], target]
        stack.pop()
        state[node] = 2
        return None

    for node in sorted(graph):
        if state[node] == 0:
            cycle = visit(node)
            if cycle is not None:
                return cycle
    return None


def _package_component(module_name: str) -> str:
    parts = module_name.split(".")
    return ".".join(parts[:2]) if len(parts) > 1 else module_name


class PortContractTests(unittest.TestCase):
    def test_all_nine_ports_are_runtime_checkable_protocols_with_stable_surfaces(self) -> None:
        self.assertEqual(set(PORT_METHODS), set(PORT_ATTRIBUTES))
        self.assertEqual(len(PORT_METHODS), 9)

        for port_name, required_methods in PORT_METHODS.items():
            with self.subTest(port=port_name):
                protocol = getattr(ports, port_name)
                self.assertTrue(issubclass(protocol, Protocol), f"{port_name} must inherit Protocol")
                self.assertTrue(getattr(protocol, "_is_protocol", False), f"{port_name} is not a Protocol")
                self.assertTrue(
                    getattr(protocol, "_is_runtime_protocol", False),
                    f"{port_name} must be decorated with @runtime_checkable",
                )

                annotations = getattr(protocol, "__annotations__", {})
                missing_attributes = PORT_ATTRIBUTES[port_name] - set(annotations)
                self.assertFalse(
                    missing_attributes,
                    f"{port_name} is missing required attributes: {sorted(missing_attributes)}",
                )

                stub_namespace: dict[str, object] = {
                    attribute: object() for attribute in PORT_ATTRIBUTES[port_name]
                }
                for method_name, parameter_names in required_methods.items():
                    method = getattr(protocol, method_name, None)
                    self.assertTrue(callable(method), f"{port_name}.{method_name} is missing")
                    self.assertEqual(
                        tuple(inspect.signature(method).parameters),
                        parameter_names,
                        f"{port_name}.{method_name} signature drifted",
                    )
                    stub_namespace[method_name] = lambda *args, **kwargs: None

                structural_stub = type(f"{port_name}StructuralStub", (), stub_namespace)()
                self.assertIsInstance(
                    structural_stub,
                    protocol,
                    f"{port_name} must support runtime structural checks",
                )


class DependencyDirectionTests(unittest.TestCase):
    def test_application_modules_do_not_import_concrete_infrastructure(self) -> None:
        violations: list[str] = []
        application_root = RADAR_ROOT / "application"
        for path in sorted(application_root.rglob("*.py")):
            module_name = _module_name(path)
            if module_name is None:
                continue
            for imported, line in _declared_imports(path, module_name):
                if _is_forbidden(imported, APPLICATION_FORBIDDEN_IMPORT_PREFIXES):
                    violations.append(f"{path.relative_to(ROOT)}:{line} imports {imported}")
        self.assertFalse(
            violations,
            "application modules must depend on ports/contracts, not concrete infrastructure:\n"
            + "\n".join(violations),
        )

    def test_runtime_runs_is_a_compatibility_facade_not_a_concrete_composition_root(self) -> None:
        path = RADAR_ROOT / "runtime" / "runs.py"
        module_name = _module_name(path)
        assert module_name is not None
        violations = [
            f"{path.relative_to(ROOT)}:{line} imports {imported}"
            for imported, line in _declared_imports(path, module_name)
            if _is_forbidden(imported, RUNTIME_FACADE_FORBIDDEN_IMPORT_PREFIXES)
        ]
        self.assertFalse(
            violations,
            "runtime/runs.py must delegate through the composition root:\n" + "\n".join(violations),
        )

    def test_canonical_module_and_package_dependency_graphs_are_acyclic(self) -> None:
        modules = _canonical_modules()
        known_modules = set(modules)
        module_graph = {
            module_name: _module_dependencies(path, module_name, known_modules)
            for module_name, path in modules.items()
        }
        module_cycle = _find_cycle(module_graph)
        self.assertIsNone(
            module_cycle,
            "canonical radar module import cycle: " + " -> ".join(module_cycle or []),
        )

        package_graph: dict[str, set[str]] = {
            _package_component(module_name): set() for module_name in modules
        }
        for source, targets in module_graph.items():
            source_package = _package_component(source)
            for target in targets:
                target_package = _package_component(target)
                if source_package != target_package:
                    package_graph[source_package].add(target_package)
        package_cycle = _find_cycle(package_graph)
        self.assertIsNone(
            package_cycle,
            "canonical radar package import cycle: " + " -> ".join(package_cycle or []),
        )


if __name__ == "__main__":
    unittest.main()
