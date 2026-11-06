from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from scripts.make_drawio import AS_IS_EDGES, AS_IS_NODES, TO_BE_EDGES, TO_BE_NODES, build_drawio

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("nodes,edges", [(AS_IS_NODES, AS_IS_EDGES), (TO_BE_NODES, TO_BE_EDGES)])
def test_drawio_xml_is_valid_and_connected(nodes, edges):
    xml = build_drawio("test", nodes, edges)
    root = ET.fromstring(xml)
    assert root.tag == "mxfile"
    cells = {c.get("id"): c for c in root.iter("mxCell")}
    assert "0" in cells and "1" in cells
    vertices = [c for c in cells.values() if c.get("vertex") == "1"]
    edge_cells = [c for c in cells.values() if c.get("edge") == "1"]
    assert len(vertices) == len(nodes) and len(edge_cells) == len(edges)
    for e in edge_cells:
        assert e.get("source") in cells and e.get("target") in cells
    # every node is used by at least one edge
    used = {e.get("source") for e in edge_cells} | {e.get("target") for e in edge_cells}
    assert {v.get("id") for v in vertices} <= used


def test_unknown_node_rejected():
    with pytest.raises(ValueError):
        build_drawio("x", {"a": ("A", "", 0, 0)}, [("a", "zz", "")])


@pytest.mark.parametrize("name", ["as_is.drawio", "to_be.drawio"])
def test_saved_files_parse(name):
    ET.parse(ROOT / "ba" / name)
