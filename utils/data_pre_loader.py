import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture

from core.database import SessionNotFound, memory_database


class BaseCommand:
    @staticmethod
    async def execute(request):
        session_data = await memory_database.get(request.session_id)
        if session_data is None:
            raise SessionNotFound

        df = pd.read_csv(session_data['filepath'], sep=' ', names=['x', 'y', 'z', 'r', 'g', 'b'])

        clusters_key = f'{request.optimal_clusters}_cluster'
        if (cluster := session_data.get(clusters_key)) is None:
            gmm = GaussianMixture(n_components=request.optimal_clusters, covariance_type='full', random_state=0)
            session_data[clusters_key] = gmm.fit_predict(df)
            await memory_database.set(request.session_id, session_data)
            df['cluster'] = session_data[clusters_key]
        else:
            df['cluster'] = cluster

        return df

    @staticmethod
    def sort_and_group_data(df, request):
        data = df.to_numpy()
        sorted_data = data[data[:, -1].argsort()]
        temp_data = [[] for _ in range(request.optimal_clusters)]
        j = 0
        for i in range(request.optimal_clusters):
            while i == sorted_data[j][-1]:
                j += 1
                if j == len(sorted_data):
                    break
            temp_data[i] = sorted_data[j - 1: j]

        return np.concatenate(temp_data)
