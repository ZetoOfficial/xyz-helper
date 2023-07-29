import aioredis
import numpy as np
import pandas as pd
import pyvista as pv
from pydantic import BaseModel
from sklearn.mixture import GaussianMixture


class ShowImageRequest(BaseModel):
    session_id: str
    cluster_index: int


class ShowImageResponse(BaseModel):
    image_path: str


class ShowImage:
    @staticmethod
    async def execute(request: ShowImageRequest, redis: aioredis.Redis) -> ShowImageResponse:
        redis_data = await redis.hgetall(request.session_id)

        if redis_data.get(b'xyz_visualize_filepath') is not None:
            return ShowImageResponse(image_path=redis_data[b'xyz_visualize_filepath'].decode('utf-8'))

        df = pd.read_csv(redis_data[b'filepath'].decode('utf-8'), sep=' ', names=['x', 'y', 'z', 'r', 'g', 'b'])

        gmm = GaussianMixture(n_components=request.optimal_clusters, covariance_type='full', random_state=0)
        labels = gmm.fit_predict(df)
        df['cluster'] = labels

        data = df.to_numpy()

        j = 0
        temp = 0
        temp_data = [[] for _ in range(request.optimal_clusters)]
        sorted_data = data[data[:, -1].argsort()]
        for i in request.cluster_index:
            while i == sorted_data[j][-1]:
                j += 1
                if j == len(sorted_data):
                    break
            temp_data[i] = sorted_data[temp:j]
            temp = j

        data = np.concatenate((*temp_data,))
        x, y, z, r, g, b = data[:, 0], data[:, 1], data[:, 2], data[:, 3], data[:, 4], data[:, 5]

        points = np.column_stack((x, y, z))
        colors = np.column_stack((r, g, b))
        point_cloud = pv.PolyData(points)

        point_cloud.point_data['colors'] = colors

        plotter = pv.Plotter(off_screen=True)
        plotter.add_points(point_cloud, render_points_as_spheres=True, point_size=1)
        plotter.window_size = [1024, 768]
        plotter.show()
        filename = f'{request.session_id}_cluster_{"_".join(str(i) for i in request.cluster_index)}.png'
        plotter.screenshot(filename)
