"""Generate the draw.io files for ba/PROCESS_FLOW.md (same flows as the Mermaid diagrams).

Usage (PowerShell): python -m scripts.make_drawio

Writes ba/as_is.drawio and ba/to_be.drawio. Open them at https://app.diagrams.net to edit.
"""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

BOX = "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
DECISION = "rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;"
EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;"

# id: (text, shape, column, row)
AS_IS_NODES = {
    "a": ("Sales or revenue looks low in a weekly report", BOX, 0, 0),
    "b": ("Manager asks the data analyst to look into it", BOX, 0, 1),
    "c": ("Analyst pulls data by hand from the analytics tool", BOX, 0, 2),
    "d": ("Do the numbers match other reports?", DECISION, 0, 3),
    "e": ("Debate which number is right (days)", BOX, 1, 3),
    "f": ("Analyst checks a few segments chosen by guess", BOX, 0, 4),
    "g": ("Findings sent by email or slide", BOX, 0, 5),
    "h": ("Cause clear?", DECISION, 0, 6),
    "i": ("Issue left open: no owner, no follow-up", BOX, 1, 6),
    "j": ("Product or marketing decides on a fix", BOX, 0, 7),
    "k": ("Fix released, effect not measured", BOX, 0, 8),
}
AS_IS_EDGES = [
    ("a", "b", ""), ("b", "c", ""), ("c", "d", ""), ("d", "e", "No"), ("e", "c", ""),
    ("d", "f", "Yes"), ("f", "g", ""), ("g", "h", ""), ("h", "i", "No"), ("h", "j", "Yes"),
    ("j", "k", ""),
]

TO_BE_NODES = {
    "a": ("Daily data refresh and reconciliation check", BOX, 1, 0),
    "b": ("Check passed?", DECISION, 1, 1),
    "c": ("Publishing stops, analytics team notified", BOX, 0, 1),
    "d": ("Dashboard updated with refresh time", BOX, 1, 2),
    "e": ("Daily session conversion below the alert rule?", DECISION, 1, 3),
    "f": ("No alert, weekly review only", BOX, 3, 3),
    "g": ("Alert to the metric owner with step and segment that moved most", BOX, 1, 4),
    "h": ("Owner opens the alert in the alert log", BOX, 1, 5),
    "i": ("Owner checks the data quality panel and the funnel by segment", BOX, 1, 6),
    "j": ("Tracking or data issue?", DECISION, 1, 7),
    "k": ("Analytics engineer fixes the tracking", BOX, 0, 7),
    "l": ("Explained by season, promotion or known change?", DECISION, 1, 8),
    "m": ("Log explanation, close alert", BOX, 2, 8),
    "n": ("Owner proposes a fix or an A/B test", BOX, 1, 9),
    "o": ("Re-check on next refresh", BOX, 1, 10),
    "p": ("Conversion back in the usual range?", DECISION, 1, 11),
    "q": ("Weekly review of overdue alerts and data quality trends", BOX, 3, 10),
}
TO_BE_EDGES = [
    ("a", "b", ""), ("b", "c", "No"), ("c", "a", ""), ("b", "d", "Yes"), ("d", "e", ""),
    ("e", "f", "No"), ("e", "g", "Yes"), ("g", "h", ""), ("h", "i", ""), ("i", "j", ""),
    ("j", "k", "Yes"), ("j", "l", "No"), ("l", "m", "Yes"), ("l", "n", "No"), ("k", "o", ""),
    ("n", "o", ""), ("o", "p", ""), ("p", "m", "Yes"), ("p", "g", "No"), ("f", "q", ""),
    ("m", "q", ""),
]


def build_drawio(name: str, nodes: dict, edges: list[tuple[str, str, str]]) -> str:
    """Return draw.io XML for a flowchart. Raises if an edge points to an unknown node."""
    for s, t, _ in edges:
        if s not in nodes or t not in nodes:
            raise ValueError(f"edge {s}->{t} uses an unknown node")
    mxfile = ET.Element("mxfile", host="app.diagrams.net")
    diagram = ET.SubElement(mxfile, "diagram", id=name.lower().replace(" ", "_"), name=name)
    model = ET.SubElement(diagram, "mxGraphModel", dx="1200", dy="900", grid="1", gridSize="10",
                          page="1", pageScale="1", pageWidth="1100", pageHeight="1700")
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")
    for nid, (text, style, col, row) in nodes.items():
        height = 90 if style == DECISION else 70
        cell = ET.SubElement(root, "mxCell", id=f"n_{nid}", value=text, style=style,
                             vertex="1", parent="1")
        ET.SubElement(cell, "mxGeometry", x=str(40 + col * 260), y=str(40 + row * 120),
                      width="200", height=str(height)).set("as", "geometry")
    for i, (s, t, label) in enumerate(edges):
        cell = ET.SubElement(root, "mxCell", id=f"e_{i}", value=label, style=EDGE, edge="1",
                             parent="1", source=f"n_{s}", target=f"n_{t}")
        ET.SubElement(cell, "mxGeometry", relative="1").set("as", "geometry")
    return ET.tostring(mxfile, encoding="unicode")


def main() -> int:
    out = Path("ba")
    (out / "as_is.drawio").write_text(build_drawio("As-is (assumed)", AS_IS_NODES, AS_IS_EDGES),
                                      encoding="utf-8")
    (out / "to_be.drawio").write_text(build_drawio("To-be", TO_BE_NODES, TO_BE_EDGES),
                                      encoding="utf-8")
    print("Wrote ba/as_is.drawio and ba/to_be.drawio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
