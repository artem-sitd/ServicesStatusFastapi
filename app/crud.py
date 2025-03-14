from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from settings import db_settings

from .models import Service, ServiceStatus
from .schemas import (
    ServiceSchema,
    ServiceStatusSchema,
    ServiceStatusUpdate,
    SlaInputSchema,
)

router = APIRouter()


@router.get("/")
def get_index():
    return {"message": "все работает"}


@router.post("/services", response_model=ServiceSchema)
async def create_service(
        service: ServiceSchema, session: AsyncSession = Depends(db_settings.get_session)
):
    """
    Создает новый сервис в postgresql через classmethod в модели
    """
    result = await Service.create_service(service, session)
    return ServiceSchema.from_orm(result)


@router.get("/services", response_model=list[ServiceSchema])
async def get_services(session: AsyncSession = Depends(db_settings.get_session)):
    """
    Отдает список всех сервисов
    """
    query = select(Service).order_by(Service.id)
    result = await session.execute(query)
    result = result.scalars().all()
    return [ServiceSchema.from_orm(service) for service in result]


@router.post("/service/{name}", response_model=ServiceStatusSchema)
async def update_history_service(
        name: str,
        service_status: ServiceStatusUpdate,
        session: AsyncSession = Depends(db_settings.get_session),
):
    """
    Принимает статус сервиса, с указанием его имени - записывает в бд
    """
    # проверяем, что такой сервис есть в базе
    id_service_query_result = await Service.check_service(name, session)
    if not id_service_query_result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"сервис '{name}' на зарегистрирован в системе",
        )
    new_status = await ServiceStatus.update_history_status(
        session, id_service_query_result, service_status
    )
    return ServiceStatusSchema.from_orm(new_status)


@router.get("/service/sla")
async def get_sla(
        sla_info: SlaInputSchema, session: AsyncSession = Depends(db_settings.get_session)
):
    """
    Считает и выводит SLA сервиса по имени, start_time, end_time (передать в json body)
    """
    # проверяем, что такой сервис есть в базе
    id_service_query_result = await Service.check_service(sla_info.name, session)
    if not id_service_query_result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"сервис '{sla_info.name}' на зарегистрирован в системе",
        )
    try:
        sla_service = await ServiceStatus.get_sla_service(
            id_service_query_result, sla_info.start_time, sla_info.end_time, session
        )
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"за указанный период у сервиса {sla_info.name} истории не найдено",
        )

    return {"name": sla_info.name, "sla": f"{sla_service}%"}


@router.get("/service/history/{name}", response_model=list[ServiceStatusSchema])
async def get_history_by_name(
        name: str, session: AsyncSession = Depends(db_settings.get_session)
):
    """
    Показывает историю сервиса, указанного по имени
    """
    # проверяем, что такой сервис есть в базе
    id_service_query_result = await Service.check_service(name, session)
    if not id_service_query_result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"сервис '{name}' на зарегистрирован в системе",
        )
    history_query = await ServiceStatus.select_history_service_by_name(
        id_service_query_result, session
    )
    if not history_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Истории данного сервиса еще нет",
        )
    return [ServiceStatusSchema.from_orm(history) for history in history_query]


@router.get("/services/history")
async def get_all_history(session: AsyncSession = Depends(db_settings.get_session)):
    """
    Показывает все сервисы с последним актуальным статусом
    """
    subquery = (
        select(ServiceStatus)
        .distinct(ServiceStatus.service_id)
        .order_by(ServiceStatus.service_id, ServiceStatus.timestamp.desc())
    )

    result = await session.execute(subquery)
    result = result.scalars().all()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="история не найдена"
        )
    return {"result": result}
