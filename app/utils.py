import datetime
from typing import Any, List, Dict, Optional, Annotated
from sqlalchemy.orm import Session
from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime, ForeignKey, 
    Table, Column, insert, delete, update, select, func, text, and_, or_, not_, desc, asc
)

def execute_query_get_list(
    db: Session,
    stmt: Any,
    sort_by: Optional[str] = None,
    page: Optional[int] = None,
    per_page: int = 10,
) -> Dict[str, Any]:
    """
    2.0 风格的通用查询分页封装
    """
    out: Dict[str, Any] = {}
    
    # 排序处理
    if sort_by:
        for field in sort_by.split(","):
            if ":" in field:
                name, order = field.split(":")
                col = text(name)
                stmt = stmt.order_by(desc(col)) if order.lower() == "desc" else stmt.order_by(asc(col))
            else:
                stmt = stmt.order_by(text(field))

    # 分页处理
    if page:
        # 获取总数：2.0 推荐使用 func.count() 配合子查询
        count_stmt = select(func.count()).select_from(stmt.subquery())
        out["count"] = db.execute(count_stmt).scalar_one()
        
        stmt = stmt.offset((page - 1) * per_page).limit(per_page)

    # 执行并转换
    result = db.execute(stmt)
    # 如果查询的是实体对象，需要用 scalars()；如果查询的是特定列，用 mappings()
    # 这里兼容处理：尝试获取映射
    # rows = result.mappings().all()
    # out["data"] = [dict(row) for row in rows]
    out["data"] = result.scalars().all()
    return out