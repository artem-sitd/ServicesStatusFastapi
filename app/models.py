from datetime import datetime, timezone

from fastapi.exceptions import HTTPException
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, select
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(200), nullable=True)

    @classmethod
    async def create_service(cls, new_name_description, session):
        """
        Создает новый сервис в postgresql через classmethod в модели
        """
        new_service = cls(
            name=new_name_description.name, description=new_name_description.description
        )
        session.add(new_service)
        await session.commit()
        return new_service

    @classmethod
    async def check_service(cls, name, session):
        """
        Проверяет наличие такого сервиса в базе
        """
        id_service = select(cls).where(cls.name == name)
        query = await session.execute(id_service)
        id_service_query_result = query.scalars().first()
        return id_service_query_result


class ServiceStatus(Base):
    __tablename__ = "service_statuses"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    status = Column(String(20), nullable=False)
    timestamp = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    service = relationship("Service", back_populates="statuses")

    @classmethod
    async def update_history_status(cls, session, service, status):
        """
        Заливает в базу новый статус у сервиса
        """
        new_status = cls(service_id=service.id, status=status.status)
        session.add(new_status)
        await session.commit()
        return new_status

    @classmethod
    async def select_history_service_by_name(cls, service, session):
        """
        Отдает с базы историю статусов сервиса
        """
        query = (
            select(cls)
            .where(cls.service_id == service.id)
            .order_by(cls.timestamp.desc())
        )
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_sla_service(cls, service, start_time, end_time, session):
        """
        Возвращает SLA указанного сервиса за указанный период (день, месяц, год)
        """
        query = (
            select(cls)
            .where(
                cls.service_id == service.id,
                cls.timestamp <= end_time,
                cls.timestamp >= start_time,
            )
            .order_by(cls.timestamp)
        )
        result = await session.execute(query)
        statuses = result.scalars().all()

        for i in statuses:
            print(i.timestamp)
        if not statuses:
            raise HTTPException(status_code=400)

        # далее обрабатываем вычлененную историю сервиса
        total_time = (end_time - statuses[0].timestamp).total_seconds()
        print(f"totaltime {total_time}")
        downtime = 0

        last_status = None
        last_timestamp = None

        for status in statuses:
            if last_status == "не работает" and status.timestamp:
                downtime += (status.timestamp - last_timestamp).total_seconds()

            last_status = status.status
            last_timestamp = status.timestamp

        if last_status == "не работает":
            downtime += (end_time - last_timestamp).total_seconds()

        uptime = total_time - downtime
        print(f"downtime {downtime}")
        print(f"uptime {uptime}")
        sla = (uptime / total_time) * 100
        return round(sla, 3)


Service.statuses = relationship(
    "ServiceStatus", order_by=ServiceStatus.timestamp, back_populates="service"
)
