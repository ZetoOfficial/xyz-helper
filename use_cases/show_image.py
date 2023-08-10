import numpy as np
import pyvista as pv
from pydantic import BaseModel

from utils.data_pre_loader import BaseCommand


class ShowImageRequest(BaseModel):
    session_id: str
    optimal_clusters: int
    cluster_indexes: list[int]


class ShowImageResponse(BaseModel):
    image_path: str


def get_public_url(file_path: str) -> str:
    file_path = file_path.lstrip('/')
    return f'/{file_path}'


class ShowImage:
    @staticmethod
    async def execute(request: ShowImageRequest) -> ShowImageResponse:
        df = await BaseCommand.execute(request.session_id, request.optimal_clusters)
        data = BaseCommand.sort_and_group_data(df, request.optimal_clusters, request.cluster_indexes)

        x, y, z, r, g, b = data[:, :6].T
        points = np.column_stack((x, y, z))
        colors = np.column_stack((r, g, b))
        point_cloud = pv.PolyData(points)
        point_cloud.point_data['colors'] = colors

        plotter = pv.Plotter(off_screen=True)
        plotter.add_points(point_cloud, render_points_as_spheres=True, point_size=1)
        plotter.window_size = [1024, 768]
        plotter.show()
        filename = f'static/{request.session_id}_cluster_{"_".join(str(i) for i in request.cluster_indexes)}.png'
        plotter.screenshot(filename)

        return ShowImageResponse(image_path=get_public_url(filename))
