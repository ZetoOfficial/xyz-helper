import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture

from core.database import SessionNotFound, memory_database


class BaseCommand:
    @staticmethod
    async def execute(session_id: str, optimal_clusters: int) -> pd.DataFrame:
        session_data = await memory_database.get(session_id)
        if session_data is None:
            raise SessionNotFound

        df = pd.read_csv(session_data['filepath'], sep=' ', names=['x', 'y', 'z', 'r', 'g', 'b'])

        # gmm = GaussianMixture(n_components=request.optimal_clusters, covariance_type='full', random_state=0)
        # df['cluster'] = gmm.fit_predict(df)

        clusters_key = f'{optimal_clusters}_cluster'
        if (cluster := session_data.get(clusters_key)) is None:
            gmm = GaussianMixture(n_components=optimal_clusters, covariance_type='full', random_state=0)
            session_data[clusters_key] = gmm.fit_predict(df)
            await memory_database.set(session_id, session_data)
            df['cluster'] = session_data[clusters_key]
        else:
            df['cluster'] = cluster

        return df

    @staticmethod
    def sort_and_group_data(df: pd.DataFrame, optimal_clusters: int, indexes: list[int] = None) -> np.ndarray:
        data = df.to_numpy()

        j = 0
        temp = 0
        temp_data = [[] for _ in range(optimal_clusters)]
        sorted_data = data[data[:, -1].argsort()]
        for i in range(optimal_clusters):
            while i == sorted_data[j][-1]:
                j += 1
                if j == len(sorted_data):
                    break
            temp_data[i] = sorted_data[temp:j]
            temp = j

        if indexes:
            temp_data = [temp_data[i] for i in indexes]
        return np.concatenate(temp_data)
