import multiprocessing

import matplotlib.pyplot as plt
import pandas as pd
from joblib import Parallel, delayed
from pydantic import BaseModel
from sklearn.mixture import GaussianMixture

from core.database import memory_database, SessionNotFound


# Находим оптимальное количество кластеров методом локтя
def compute_bic(n_components, data):
    gmm = GaussianMixture(n_components=n_components, covariance_type='full', random_state=42)
    gmm.fit(data)
    return gmm.bic(data)


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


def get_public_url(file_path: str) -> str:
    file_path = file_path.lstrip('/')
    return f'/{file_path}'


class ElbowRuleGraphic:
    @staticmethod
    async def execute(request: ElbowRuleGraphicRequest) -> ElbowRuleGraphicResponse:
        session_data = await memory_database.get(request.session_id)
        if not session_data:
            raise SessionNotFound

        if (path := session_data.get('elbow_rule.png')) is not None:
            return ElbowRuleGraphicResponse(graphic_path=get_public_url(path))

        df = pd.read_csv(session_data['filepath'], sep=' ', names=['x', 'y', 'z', 'r', 'g', 'b'])

        # Преобразуем RGB в Grayscale и создаем DataFrame из загруженных данных
        df['grayscale'] = 0.299 * df['r'] + 0.587 * df['g'] + 0.114 * df['b']
        data = df[['x', 'y', 'z', 'grayscale']].values

        # Вызываем функцию и строим график
        bic_scores = find_optimal_clusters_parallel(data)

        my_dpi = 96
        plt.figure(figsize=(1024 / my_dpi, 768 / my_dpi), dpi=my_dpi)
        plt.plot(range(1, len(bic_scores) + 1), bic_scores, marker='o')
        plt.xlabel('Количество кластеров')
        plt.ylabel('BIC score')
        plt.title('BIC Score vs. Количество кластеров')
        filepath = f'static/{request.session_id}_elbow_rule.png'
        plt.savefig(filepath, dpi=my_dpi)

        session_data.update({'elbow_rule.png': filepath})
        await memory_database.set(request.session_id, session_data)

        return ElbowRuleGraphicResponse(graphic_path=get_public_url(filepath))
