import os

import aioredis
import numpy as np
import pandas as pd
import pyvista as pv
from pydantic import BaseModel
from sklearn.mixture import GaussianMixture


class GenerateImageRequest(BaseModel):
    session_id: str
    optimal_clusters: int


class GenerateImageResponse(BaseModel):
    image_path: str


class GenerateImage:
    @staticmethod
    async def execute(request: GenerateImageRequest, redis: aioredis.Redis) -> GenerateImageResponse:
        redis_data = await redis.hgetall(request.session_id)

        if redis_data.get(b'xyz_visualize_filepath') is not None:
            return GenerateImageResponse(image_path=redis_data[b'xyz_visualize_filepath'].decode('utf-8'))

        df = pd.read_csv(redis_data[b'filepath'].decode('utf-8'), sep=' ', names=['x', 'y', 'z', 'r', 'g', 'b'])

        gmm = GaussianMixture(n_components=request.optimal_clusters, covariance_type='full', random_state=0)
        labels = gmm.fit_predict(df)
        df['cluster'] = labels

        data = df.to_numpy()
        x, y, z, cluster = data[:, 0], data[:, 1], data[:, 2], data[:, -1]

        # Создадим точки
        points = np.column_stack((x, y, z))

        # Создадим меш
        mesh = pv.PolyData(points)

        # Добавим информацию о кластерах как массив "cluster"
        mesh['cluster'] = cluster

        # Создадим интерактивную 3D сцену
        p = pv.Plotter(off_screen=True)

        # Добавим точки с соответствующими цветами для каждого кластера
        p.add_points(mesh, scalars='cluster', render_points_as_spheres=True, point_size=5)

        p.window_size = [1024, 768]

        # Отобразим окно сцены
        p.show()

        filepath = f'{request.session_id}_xyz_visualize.png'
        p.screenshot(filepath)

        abs_filepath = os.path.abspath(filepath)

        await redis.hmset(request.session_id, {'xyz_visualize_filepath': abs_filepath})

        return GenerateImageResponse(image_path=abs_filepath)
