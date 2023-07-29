import multiprocessing
import os.path

import aioredis
import matplotlib.pyplot as plt
import pandas as pd
from joblib import Parallel, delayed
from pydantic import BaseModel
from sklearn.mixture import GaussianMixture


# Находим оптимальное количество кластеров методом локтя
def compute_bic(n_components, data):
    gmm = GaussianMixture(n_components=n_components, covariance_type='full', random_state=42)
    gmm.fit(data)
    bic_score = gmm.bic(data)
    return bic_score


def find_optimal_clusters_parallel(data, max_clusters=10):
    n_components_range = range(1, max_clusters + 1)

    # Use joblib to parallelize the loop
    print('Computing BIC scores...')
    num_cores = multiprocessing.cpu_count()  # Adjust this as needed
    bic_scores = Parallel(n_jobs=num_cores)(
        delayed(compute_bic)(n_components, data) for n_components in n_components_range
    )
    print('Done.')

    return bic_scores


class ElbowRuleGraphicRequest(BaseModel):
    session_id: str


class ElbowRuleGraphicResponse(BaseModel):
    graphic_path: str


class ElbowRuleGraphic:
    @staticmethod
    async def execute(request: ElbowRuleGraphicRequest, redis: aioredis.Redis) -> ElbowRuleGraphicResponse:
        redis_data = await redis.hgetall(request.session_id)

        if redis_data.get(b'elbow_rule_filepath') is not None:
            return ElbowRuleGraphicResponse(graphic_path=redis_data[b'elbow_rule_filepath'].decode('utf-8'))

        df = pd.read_csv(redis_data[b'filepath'].decode('utf-8'), sep=' ', names=['x', 'y', 'z', 'r', 'g', 'b'])

        # Преобразуем RGB в Grayscale
        df['grayscale'] = 0.299 * df['r'] + 0.587 * df['g'] + 0.114 * df['b']

        # Создаем DataFrame из загруженных данных
        data = df[['x', 'y', 'z', 'grayscale']].values

        # Вызываем функцию и строим график
        bic_scores = find_optimal_clusters_parallel(data)

        my_dpi = 96
        plt.figure(figsize=(1024 / my_dpi, 768 / my_dpi), dpi=my_dpi)
        plt.plot(range(1, len(bic_scores) + 1), bic_scores, marker='o')
        plt.xlabel('Количество кластеров')
        plt.ylabel('BIC score')
        plt.title('BIC Score vs. Количество кластеров')
        filepath = f'{request.session_id}_elbow_rule.png'
        plt.savefig(filepath, dpi=my_dpi)
        abs_filepath = os.path.abspath(filepath)

        await redis.hmset(request.session_id, {'elbow_rule_filepath': abs_filepath})

        return ElbowRuleGraphicResponse(graphic_path=abs_filepath)
