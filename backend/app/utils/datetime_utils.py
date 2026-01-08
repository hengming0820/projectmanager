"""
时间工具模块
提供标准的 UTC 时间获取和处理方法
"""
from datetime import datetime, timezone, timedelta


def utc_now() -> datetime:
    """
    获取当前 UTC 时间（带时区信息）
    
    Returns:
        datetime: 带 UTC 时区信息的 datetime 对象
        
    Example:
        >>> utc_now()
        datetime.datetime(2025, 10, 22, 10, 0, 0, tzinfo=datetime.timezone.utc)
    """
    return datetime.now(timezone.utc)


def local_now() -> datetime:
    """
    获取当前本地时间（带时区信息）
    
    Returns:
        datetime: 带本地时区信息的 datetime 对象
    """
    return datetime.now()


def to_utc(dt: datetime) -> datetime:
    """
    将 naive datetime 或其他时区的 datetime 转换为 UTC
    
    Args:
        dt: 要转换的 datetime 对象
        
    Returns:
        datetime: UTC 时区的 datetime 对象
    """
    if dt.tzinfo is None:
        # 如果是 naive datetime，假定为 UTC
        return dt.replace(tzinfo=timezone.utc)
    else:
        # 如果已有时区信息，转换为 UTC
        return dt.astimezone(timezone.utc)


def to_local(dt: datetime, tz_offset_hours: int = 8) -> datetime:
    """
    将 UTC 时间转换为本地时间
    
    Args:
        dt: UTC datetime 对象
        tz_offset_hours: 时区偏移（小时），默认 +8（中国）
        
    Returns:
        datetime: 本地时区的 datetime 对象
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    local_tz = timezone(timedelta(hours=tz_offset_hours))
    return dt.astimezone(local_tz)


def naive_to_aware_utc(dt: datetime) -> datetime:
    """
    将 naive datetime 转换为 aware UTC datetime
    
    Args:
        dt: naive datetime 对象
        
    Returns:
        datetime: 带 UTC 时区信息的 datetime 对象
    """
    if dt.tzinfo is not None:
        return dt
    return dt.replace(tzinfo=timezone.utc)


def ensure_utc(dt: datetime | None) -> datetime | None:
    """
    确保 datetime 对象是 UTC 时区
    
    Args:
        dt: datetime 对象或 None
        
    Returns:
        datetime: UTC 时区的 datetime 对象，或 None
    """
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        # naive datetime，假定为 UTC
        return dt.replace(tzinfo=timezone.utc)
    else:
        # 已有时区，转换为 UTC
        return dt.astimezone(timezone.utc)


# 为了方便迁移，提供一个兼容性函数
def now() -> datetime:
    """
    获取当前 UTC 时间（兼容性函数）
    建议使用 utc_now() 以明确意图
    
    Returns:
        datetime: 带 UTC 时区信息的 datetime 对象
    """
    return utc_now()

