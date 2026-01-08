from fastapi import APIRouter, HTTPException, Response
from app.utils.file_utils import file_service
from minio.error import S3Error

router = APIRouter(prefix="/files", tags=["文件代理"])


@router.get("/{path:path}")
async def proxy_file(path: str):
    try:
        # path 是 bucket 内的对象路径，例如 "avatars/uid.png" 或 "uploads/.."
        info = file_service.get_file_info(path)
        if info is None:
            raise HTTPException(status_code=404, detail=f"文件不存在: {path}")

        data = file_service.minio_client.get_object(file_service.bucket_name, path)
        content = data.read()
        data.close()
        data.release_conn()

        content_type = info.get("content_type") or "application/octet-stream"
        return Response(content=content, media_type=content_type)
    except HTTPException:
        # 直接抛出已经定义好的 HTTPException
        raise
    except S3Error as e:
        raise HTTPException(status_code=404, detail=f"文件不存在: {e}")
    except Exception as e:
        # 记录日志但返回 404 而不是 500
        import logging
        logging.getLogger(__name__).error(f"读取文件失败 {path}: {e}")
        raise HTTPException(status_code=404, detail=f"文件不存在")


