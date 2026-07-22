"""请求用例的异步事务边界。"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


async def _commit_or_rollback(db: AsyncSession) -> None:
    try:
        await db.commit()
    except BaseException:
        await db.rollback()
        raise


@asynccontextmanager
async def unit_of_work(
    db: AsyncSession,
    *,
    commit_on: tuple[type[BaseException], ...] = (),
) -> AsyncIterator[None]:
    """统一提交或回滚一次完整用例。

    ``commit_on`` 用于需要在返回领域错误前持久化安全状态的场景，例如
    Refresh Token 复用检测必须提交对整个令牌族的撤销。
    """
    try:
        yield
    except BaseException as exc:
        if isinstance(exc, commit_on):
            await _commit_or_rollback(db)
        else:
            await db.rollback()
        raise
    else:
        await _commit_or_rollback(db)
