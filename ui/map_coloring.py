"""Offline SVG rendering for structured map-coloring results."""

from __future__ import annotations

from html import escape

import streamlit.components.v1 as components

from algorithms.map_coloring import MapColoringResult


COLOR_HEX = {
    "Red": "#d66a5f",
    "Green": "#7aa66a",
    "Blue": "#6e91c9",
    "Yellow": "#d6a15f",
}
UNASSIGNED = "#343a37"


def _iter_points(value):
    if isinstance(value, list) and len(value) >= 2 and all(
        isinstance(item, (int, float)) for item in value[:2]
    ):
        yield value[0], value[1]
        return
    if isinstance(value, list):
        for child in value:
            yield from _iter_points(child)


def _geometry_rings(geometry: dict) -> list[list[list[float]]]:
    coordinates = geometry["coordinates"]
    if geometry["type"] == "Polygon":
        return coordinates
    if geometry["type"] == "MultiPolygon":
        return [ring for polygon in coordinates for ring in polygon]
    return []


def _render_thu_duc_svg(result: MapColoringResult, assignment: dict[str, str]) -> str:
    features = result.geojson["features"]
    all_points = [point for feature in features for point in _iter_points(feature["geometry"]["coordinates"])]
    min_x = min(point[0] for point in all_points)
    max_x = max(point[0] for point in all_points)
    min_y = min(point[1] for point in all_points)
    max_y = max(point[1] for point in all_points)
    width, height, padding = 920, 590, 24
    scale = min((width - 2 * padding) / (max_x - min_x), (height - 2 * padding) / (max_y - min_y))

    def project(point):
        x = padding + (point[0] - min_x) * scale
        y = height - padding - (point[1] - min_y) * scale
        return x, y

    shapes: list[str] = []
    labels: list[str] = []
    for feature in features:
        properties = feature["properties"]
        name = properties["name"]
        path_parts = []
        points = list(_iter_points(feature["geometry"]["coordinates"]))
        for ring in _geometry_rings(feature["geometry"]):
            projected = [project(point) for point in ring]
            if not projected:
                continue
            path_parts.append(
                "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in projected) + " Z"
            )
        fill = COLOR_HEX.get(assignment.get(name, ""), UNASSIGNED)
        neighbors = ", ".join(sorted(result.adjacency[name]))
        tooltip = escape(
            f"{properties['full_name']} | Color: {assignment.get(name, 'Unassigned')} | "
            f"Adjacent: {neighbors}"
        )
        shapes.append(
            f'<path d="{" ".join(path_parts)}" fill="{fill}" fill-rule="evenodd" '
            f'stroke="#f4efe5" stroke-width="1.2" vector-effect="non-scaling-stroke">'
            f"<title>{tooltip}</title></path>"
        )
        projected_points = [project(point) for point in points]
        label_x = sum(point[0] for point in projected_points) / len(projected_points)
        label_y = sum(point[1] for point in projected_points) / len(projected_points)
        short_label = name.replace(" ", "\n", 1) if len(name) > 11 else name
        lines = short_label.split("\n")
        tspans = "".join(
            f'<tspan x="{label_x:.1f}" dy="{0 if index == 0 else 13}">{escape(line)}</tspan>'
            for index, line in enumerate(lines)
        )
        labels.append(
            f'<text x="{label_x:.1f}" y="{label_y:.1f}" text-anchor="middle" '
            f'class="ward-label">{tspans}</text>'
        )
    return f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Bản đồ tô màu 12 phường Thủ Đức">{"".join(shapes)}{"".join(labels)}</svg>'


def _render_australia_svg(result: MapColoringResult, assignment: dict[str, str]) -> str:
    positions = {
        "WA": (100, 245), "NT": (285, 115), "SA": (300, 295), "Q": (510, 125),
        "NSW": (525, 300), "V": (465, 435), "T": (590, 515),
    }
    edges = []
    for region, neighbors in result.adjacency.items():
        for neighbor in neighbors:
            if region < neighbor:
                x1, y1 = positions[region]
                x2, y2 = positions[neighbor]
                edges.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    nodes = []
    for region, (x, y) in positions.items():
        fill = COLOR_HEX.get(assignment.get(region, ""), UNASSIGNED)
        nodes.append(
            f'<g><circle cx="{x}" cy="{y}" r="55" fill="{fill}"/><text x="{x}" y="{y + 6}" '
            f'text-anchor="middle" class="graph-label">{region}</text></g>'
        )
    return f'<svg viewBox="0 0 700 590" class="graph-svg">{"".join(edges)}{"".join(nodes)}</svg>'


def render_coloring_map(
    result: MapColoringResult,
    assignment: dict[str, str],
    step_label: str,
) -> None:
    """Render a self-contained map; no tile server or network request is required."""
    svg = (
        _render_thu_duc_svg(result, assignment)
        if result.map_id == "thu-duc-2025"
        else _render_australia_svg(result, assignment)
    )
    legends = "".join(
        f'<span><i style="background:{hex_color}"></i>{escape(name)}</span>'
        for name, hex_color in COLOR_HEX.items()
        if name in set(assignment.values()) or name in {"Red", "Green", "Blue", "Yellow"}
    )
    html = f"""
    <div class="map-shell">
      <div class="map-heading"><strong>{escape(result.map_title)}</strong><small>{escape(step_label)}</small></div>
      <div class="map-stage">{svg}</div>
      <div class="legend">{legends}<span><i style="background:{UNASSIGNED}"></i>Unassigned</span></div>
    </div>
    <style>
      * {{ box-sizing:border-box; }} body {{ margin:0; background:transparent; color:#f4efe5; font-family:'Segoe UI',sans-serif; }}
      .map-shell {{ border:1px solid rgba(214,196,166,.22); border-radius:16px; background:#121514; padding:14px; }}
      .map-heading {{ display:flex; justify-content:space-between; gap:12px; align-items:center; margin-bottom:8px; }}
      .map-heading strong {{ font-size:16px; }} .map-heading small {{ color:#d6a15f; text-align:right; }}
      .map-stage {{ background:linear-gradient(145deg,#17201d,#0b0e0d); border-radius:12px; overflow:hidden; }}
      svg {{ display:block; width:100%; height:auto; max-height:590px; }}
      path {{ transition:fill .18s ease; }} .ward-label {{ fill:#fff; font-size:10px; font-weight:700; paint-order:stroke; stroke:#151817; stroke-width:2.5px; pointer-events:none; }}
      .graph-svg line {{ stroke:#8f9b94; stroke-width:3; }} .graph-svg circle {{ stroke:#f4efe5; stroke-width:2; }}
      .graph-label {{ fill:white; font-size:19px; font-weight:800; }}
      .legend {{ display:flex; flex-wrap:wrap; gap:8px 16px; padding-top:11px; font-size:12px; color:#d2c7b8; }}
      .legend span {{ display:flex; align-items:center; gap:6px; }} .legend i {{ width:12px; height:12px; border-radius:3px; border:1px solid rgba(255,255,255,.35); }}
      @media(max-width:640px) {{ .map-heading {{ align-items:flex-start; flex-direction:column; }} .ward-label {{ font-size:12px; }} }}
    </style>
    """
    components.html(html, height=700, scrolling=False)
