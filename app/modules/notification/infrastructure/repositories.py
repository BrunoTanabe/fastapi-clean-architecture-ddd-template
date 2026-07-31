import json

from loguru import logger
from sqlalchemy import cast, func, insert, literal, null, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notification.application.exceptions import NotificationException
from app.modules.notification.application.interfaces import INotificationRepository
from app.modules.notification.application.mappers import (
    entity_model_mapper,
    model_entity_mapper,
    models_notification_list_mapper,
)
from app.modules.notification.domain.entities import (
    Notification,
    NotificationList,
    NotificationPagination,
)
from app.modules.notification.infrastructure.models import NotificationModel
from app.modules.shared.application.exceptions import StandardException
from app.modules.shared.domain.enums import Role, SortOrder
from app.modules.user.infrastructure.models import UserModel


class PostgresNotificationRepository(INotificationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # CREATE
    async def create(self, notification: Notification) -> Notification:
        try:
            logger.info(
                f"Creating notification of type '{notification.notification_type}' for user {notification.user.id} in database."
            )

            db_notification: NotificationModel = entity_model_mapper(notification)

            self.session.add(db_notification)
            await self.session.flush()

            logger.info(
                f"Notification of type '{notification.notification_type}' created successfully for user {notification.user.id}."
            )
            return model_entity_mapper(db_notification)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the create notification repository."
            )
            raise NotificationException()

    async def create_broadcast(self, notification: Notification) -> list[Notification]:
        try:
            if notification.originated_from_broadcast == Role.ADMIN:
                target_roles = [Role.ADMIN]
            elif notification.originated_from_broadcast == Role.MANAGER:
                target_roles = [Role.MANAGER, Role.ADMIN]
            else:
                target_roles = [Role.USER, Role.MANAGER, Role.ADMIN]

            logger.info(
                f"Creating broadcast notification of type '{notification.notification_type}' "
                f"for roles {[r.value for r in target_roles]}."
            )

            t = NotificationModel.__table__

            source = select(
                UserModel.id.label("user_id"),
                cast(
                    literal(notification.notification_type.name),
                    t.c.notification_type.type,
                ).label("notification_type"),
                literal(notification.title).label("title"),
                literal(notification.body).label("body"),
                (
                    literal(str(notification.redirect_url))
                    if notification.redirect_url
                    else null()
                ).label("redirect_url"),
                (
                    cast(literal(json.dumps(notification.metadata)), JSONB)
                    if notification.metadata
                    else null()
                ).label("notification_metadata"),
                literal(notification.originated_from_broadcast.value).label(
                    "originated_from_broadcast"
                ),
            ).where(
                UserModel.role.in_(target_roles),
                UserModel.is_active.is_(True),
            )

            stmt = (
                insert(t)
                .from_select(
                    [
                        t.c.user_id,
                        t.c.notification_type,
                        t.c.title,
                        t.c.body,
                        t.c.redirect_url,
                        t.c.metadata,
                        t.c.originated_from_broadcast,
                    ],
                    source,
                    include_defaults=False,
                )
                .returning(
                    t.c.id,
                    t.c.user_id,
                    t.c.notification_type,
                    t.c.title,
                    t.c.body,
                    t.c.redirect_url,
                    t.c.metadata.label("notification_metadata"),
                    t.c.originated_from_broadcast,
                    t.c.is_read,
                    t.c.read_at,
                    t.c.is_active,
                    t.c.created_at,
                    t.c.updated_at,
                )
            )

            result = await self.session.execute(stmt)
            rows = result.mappings().all()
            models = [NotificationModel(**dict(row)) for row in rows]

            logger.info(
                f"Broadcast notification created for {len(models)} user(s) "
                f"targeting role '{notification.originated_from_broadcast.value}'."
            )
            return [model_entity_mapper(m) for m in models]
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the create_broadcast notification repository."
            )
            raise NotificationException()

    # READ
    async def get_by_id(self, notification: Notification) -> Notification | None:
        try:
            logger.info(f"Getting notification '{notification.id}' from database.")

            model = await self.session.scalar(
                select(NotificationModel).where(
                    NotificationModel.id == notification.id,
                    NotificationModel.is_active.is_(True),
                )
            )

            logger.info(
                f"Notification '{notification.id}' {'found' if model else 'not found'} in database."
            )
            return model_entity_mapper(model) if model else None
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get notification by id repository."
            )
            raise NotificationException()

    async def get_all_by_user(
        self,
        notification: Notification,
        pagination: NotificationPagination,
    ) -> NotificationList:
        try:
            logger.info(
                f"Getting all active notifications for user {notification.user.id} from database."
            )

            col = getattr(NotificationModel, pagination.sort_by.value)
            ordering = (
                col.asc() if pagination.sort_order == SortOrder.ASC else col.desc()
            )

            statement = (
                select(
                    NotificationModel,
                    func.count(NotificationModel.id).over().label("total"),
                )
                .where(
                    NotificationModel.user_id == notification.user.id,
                    NotificationModel.is_active.is_(True),
                )
                .order_by(ordering)
                .offset(pagination.offset)
                .limit(pagination.per_page)
            )

            result = await self.session.execute(statement)
            rows = result.all()

            notification_list = models_notification_list_mapper(rows)

            logger.info(
                f"Retrieved {len(notification_list.items)} of {notification_list.total} active notification(s) for user {notification.user.id}."
            )
            return notification_list
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get all notifications by user repository."
            )
            raise NotificationException()

    # UPDATE
    async def update(self, notification: Notification) -> Notification:
        try:
            logger.info(f"Updating notification '{notification.id}' in database.")

            model = await self.session.get(NotificationModel, notification.id)

            model.is_read = notification.is_read
            model.read_at = notification.read_at
            model.is_active = notification.is_active

            await self.session.flush()

            logger.info(
                f"Notification '{notification.id}' updated successfully in database."
            )
            return model_entity_mapper(model)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the update notification repository."
            )
            raise NotificationException()
