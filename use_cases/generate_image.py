import numpy as np
import pyvista as pv
from pydantic import BaseModel

from utils.data_pre_loader import BaseCommand


class GenerateImageRequest(BaseModel):
    session_id: str
    optimal_clusters: int


class ClusterImage(BaseModel):
    index: int
    name: str
    path: str


class GenerateImageResponse(BaseModel):
    main_image: str
    cluster_images: list[ClusterImage]


def get_public_url(file_path: str) -> str:
    file_path = file_path.lstrip('/')
    return f'/{file_path}'


class GenerateImage:
    @staticmethod
    async def execute(request: GenerateImageRequest) -> GenerateImageResponse:
        df = await BaseCommand.execute(request.session_id, request.optimal_clusters)
        data = BaseCommand.sort_and_group_data(df, request.optimal_clusters)
        cluster_images = []

        for i in range(request.optimal_clusters):
            x, y, z, r, g, b = data[data[:, -1] == i][:, :6].T
            points = np.column_stack((x, y, z))
            colors = np.column_stack((r, g, b))
            point_cloud = pv.PolyData(points)
            point_cloud.point_data['colors'] = colors

            plotter = pv.Plotter(off_screen=True)
            plotter.window_size = [200, 150]
            plotter.add_points(point_cloud, render_points_as_spheres=True, point_size=1)
            plotter.show()
            filepath = f'static/{request.session_id}_{i}_cluster_xyz_visualize.png'
            plotter.screenshot(filepath)
            cluster_images.append(ClusterImage(index=i, name=f'cluster_{i}', path=get_public_url(filepath)))

        x, y, z, cluster = data[:, 0], data[:, 1], data[:, 2], data[:, -1]
        points = np.column_stack((x, y, z))
        mesh = pv.PolyData(points)
        mesh['cluster'] = cluster

        p = pv.Plotter(off_screen=True)
        p.add_points(mesh, scalars='cluster', render_points_as_spheres=True, point_size=5)
        p.window_size = [1024, 768]
        p.show()
        filepath = f'static/{request.session_id}_xyz_visualize.png'
        p.screenshot(filepath)

        return GenerateImageResponse(main_image=get_public_url(filepath), cluster_images=cluster_images)
