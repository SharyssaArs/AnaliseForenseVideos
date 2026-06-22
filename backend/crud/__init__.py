from backend.crud.analise_crud import (
    create_analise,
    get_analise_by_hash,
    get_analise_by_task_id,
    get_history_by_user,
    update_analise_status,
)
from backend.crud.log_crud import (
    create_log_processamento,
    get_logs_by_analise_id,
)
from backend.crud.resultado_crud import (
    create_resultado_ia,
    get_resultado_by_analise_id,
)