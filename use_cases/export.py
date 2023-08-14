from io import BytesIO

import pandas as pd
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from utils.data_pre_loader import BaseCommand


class ExportRequest(BaseModel):
    session_id: str
    optimal_clusters: int
    cluster_indexes: list[int]


def get_public_url(file_path: str) -> str:
    file_path = file_path.lstrip('/')
    return f'/{file_path}'


class Export:
    @staticmethod
    async def execute(request: ExportRequest) -> StreamingResponse:
        df = await BaseCommand.execute(request.session_id, request.optimal_clusters)
        data = BaseCommand.sort_and_group_data(df, request.optimal_clusters, request.cluster_indexes)

        df = pd.DataFrame(data[:, :-1])
        filename = f'{request.session_id}_cluster_{"_".join(str(i) for i in request.cluster_indexes)}.xyz'
        # filepath = f'static/{filename}'
        # df.to_csv(filepath, sep=' ', index=False, header=False)
        # return FileResponse(path=filepath, filename=filename, media_type='multipart/form-data')

        # Create CSV data as bytes
        csv_data = df.to_csv(index=False, sep=' ', header=False).encode()

        # Use BytesIO to simulate a file-like object
        file_like = BytesIO(csv_data)

        return StreamingResponse(
            file_like,
            media_type="multipart/form-data",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
