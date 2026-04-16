
from __future__ import annotations

import os
import tempfile
from typing import Sequence

import numpy as np

from inpicker.domain.entities import AppState, Region
from inpicker.domain.exceptions import MissingDependencyError
from inpicker.application.use_cases.region_design import RegionDesignService

try:
    from skimage import measure
    SKIMAGE_OK = True
except Exception:
    SKIMAGE_OK = False

try:
    import plotly.graph_objects as go
    PLOTLY_OK = True
except Exception:
    PLOTLY_OK = False


class PlotlyVisualizer:
    def __init__(self, region_service: RegionDesignService):
        self.region_service = region_service

    def _require_plotly(self) -> None:
        if not PLOTLY_OK:
            raise MissingDependencyError('Please install plotly.')

    def _plot_bin_edges(self, fig, state: AppState):
        x, y, z = state.bin_dimensions.x, state.bin_dimensions.y, state.bin_dimensions.z
        edges = [
            [(0, 0, 0), (x, 0, 0)], [(0, y, 0), (x, y, 0)], [(0, 0, z), (x, 0, z)], [(0, y, z), (x, y, z)],
            [(0, 0, 0), (0, y, 0)], [(x, 0, 0), (x, y, 0)], [(0, 0, z), (0, y, z)], [(x, 0, z), (x, y, z)],
            [(0, 0, 0), (0, 0, z)], [(x, 0, 0), (x, 0, z)], [(0, y, 0), (0, y, z)], [(x, y, 0), (x, y, z)],
        ]
        for p1, p2 in edges:
            fig.add_trace(go.Scatter3d(x=[p1[0], p2[0]], y=[p1[1], p2[1]], z=[p1[2], p2[2]], mode='lines', line=dict(color='black', width=3), showlegend=False))

    def open_regions_and_picks(self, state: AppState) -> str:
        self._require_plotly()
        x, y, z = state.bin_dimensions.x, state.bin_dimensions.y, state.bin_dimensions.z
        fig = go.Figure()
        for idx, region in enumerate(state.regions):
            c = region.center
            a = region.approach
            fig.add_trace(go.Scatter3d(x=[c.x], y=[c.y], z=[c.z], mode='markers+text', marker=dict(size=9), text=[region.name], textposition='top center', name=f'Center {region.name}'))
            fig.add_trace(go.Scatter3d(x=[a.x], y=[a.y], z=[a.z], mode='markers', marker=dict(size=8, symbol='diamond'), name=f'Approach {region.name}'))
        if state.picks:
            fig.add_trace(go.Scatter3d(
                x=[p.x for p in state.picks],
                y=[p.y for p in state.picks],
                z=[p.z for p in state.picks],
                mode='markers',
                marker=dict(size=4.5, color=[-1 if p.region is None else p.region for p in state.picks], colorscale='Turbo', opacity=0.95, line=dict(width=1, color='black')),
                name='Picks',
            ))
        self._plot_bin_edges(fig, state)
        fig.update_layout(title='3D Regions + Simulated/Real Picks', scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z', xaxis=dict(range=[0, x]), yaxis=dict(range=[0, y]), zaxis=dict(range=[0, z]), aspectmode='data'))
        path = os.path.join(tempfile.gettempdir(), 'inpicker_regions_picks.html')
        fig.write_html(path, auto_open=True)
        return path

    def open_colored_surfaces(self, state: AppState, resolution: int) -> str:
        self._require_plotly()
        if not SKIMAGE_OK:
            raise MissingDependencyError('Please install scikit-image.')
        if len(state.regions) < 1:
            raise MissingDependencyError('No regions available.')
        bx, by, bz = state.bin_dimensions.x, state.bin_dimensions.y, state.bin_dimensions.z
        n = max(16, int(resolution))
        ny = max(12, int(n * by / max(1.0, bx)))
        nz = max(10, int(n * bz / max(1.0, bx)))
        xs = np.linspace(0, bx, n)
        ys = np.linspace(0, by, ny)
        zs = np.linspace(0, bz, nz)
        X, Y, Z = np.meshgrid(xs, ys, zs, indexing='ij')
        fig = go.Figure()
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        if len(state.regions) == 1:
            label = np.zeros_like(X, dtype=np.int32)
        else:
            costs = []
            for region in state.regions:
                c = region.center
                w = region.weights
                J = w.x * (X - c.x) ** 2 + w.y * (Y - c.y) ** 2 + w.z * (Z - c.z) ** 2
                costs.append(J)
            cost_stack = np.stack(costs, axis=-1)
            label = np.argmin(cost_stack, axis=-1).astype(np.int32)
        for idx, region in enumerate(state.regions):
            mask = (label == idx).astype(np.float32)
            if np.all(mask == 0):
                continue
            try:
                verts, faces, normals, values = measure.marching_cubes(mask, level=0.5, spacing=(xs[1]-xs[0], ys[1]-ys[0], zs[1]-zs[0]))
            except Exception:
                continue
            if len(verts) == 0 or len(faces) == 0:
                continue
            fig.add_trace(go.Mesh3d(x=verts[:, 0], y=verts[:, 1], z=verts[:, 2], i=faces[:, 0], j=faces[:, 1], k=faces[:, 2], color=colors[idx % len(colors)], opacity=0.22, name=f'Surface {region.name}'))
        for idx, region in enumerate(state.regions):
            c = region.center
            a = region.approach
            fig.add_trace(go.Scatter3d(x=[c.x], y=[c.y], z=[c.z], mode='markers+text', marker=dict(size=8, color=colors[idx % len(colors)], symbol='circle'), text=[region.name], textposition='top center', name=f'Center {region.name}'))
            fig.add_trace(go.Scatter3d(x=[a.x], y=[a.y], z=[a.z], mode='markers', marker=dict(size=7, color=colors[idx % len(colors)], symbol='diamond'), name=f'Approach {region.name}'))
        if state.picks:
            fig.add_trace(go.Scatter3d(x=[p.x for p in state.picks], y=[p.y for p in state.picks], z=[p.z for p in state.picks], mode='markers', marker=dict(size=4.5, color=[-1 if p.region is None else p.region for p in state.picks], colorscale='Turbo', opacity=0.95, line=dict(width=1, color='black')), name='Picks'))
        self._plot_bin_edges(fig, state)
        fig.update_layout(title='Colored 3D Region Surfaces + Picks', scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z', xaxis=dict(range=[0, bx]), yaxis=dict(range=[0, by]), zaxis=dict(range=[0, bz]), aspectmode='data'))
        path = os.path.join(tempfile.gettempdir(), 'inpicker_colored_surfaces.html')
        fig.write_html(path, auto_open=True)
        return path
