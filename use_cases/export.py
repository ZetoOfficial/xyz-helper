import pandas as pd
from pydantic import BaseModel

from utils.data_pre_loader import BaseCommand


class ExportRequest(BaseModel):
    session_id: str
    optimal_clusters: int
    cluster_indexes: list[int]


class ExportResponse(BaseModel):
    filepath: str


def get_public_url(file_path: str) -> str:
    file_path = file_path.lstrip('/')
    return f'/{file_path}'


class Export:
    @staticmethod
    async def execute(request: ExportRequest) -> ExportResponse:
        df = await BaseCommand.execute(request.session_id, request.optimal_clusters)
        data = BaseCommand.sort_and_group_data(df, request.optimal_clusters, request.cluster_indexes)

        df = pd.DataFrame(data[:, :-1])
        filename = f'{request.session_id}_cluster_{"_".join(str(i) for i in request.cluster_indexes)}.xyz'
        filepath = f'static/{filename}'
        df.to_csv(filepath, sep=' ', index=False, header=False)

        return ExportResponse(filepath=get_public_url(filepath))
