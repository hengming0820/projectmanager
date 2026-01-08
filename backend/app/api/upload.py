"""
通用文件上传 API（WangEditor/图片等）
与现有 MinIO 文件服务 file_utils.py 一致
"""
from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from app.utils.security import get_current_user
from app.models.user import User
from app.utils.file_utils import file_service
import logging

router = APIRouter(prefix="/common/upload", tags=["文件上传"])
logger = logging.getLogger(__name__)


@router.post("/wangeditor")
async def upload_wangeditor_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    WangEditor 图片上传接口
    返回格式需符合 WangEditor 要求：{ errno: 0, data: { url } }
    """
    try:
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="没有选择文件")

        file_url = await file_service.upload_file(file, folder="wangeditor")

        return {
            "errno": 0,
            "data": {
                "url": file_url,
                "alt": file.filename,
                "href": file_url,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("WangEditor 文件上传失败")
        return {"errno": 1, "message": f"上传失败: {str(e)}"}


@router.post("/images")
async def upload_images(
    files: Optional[List[UploadFile]] = File(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user)
):
    """
    通用图片上传（多文件）
    返回：{ code, message, data: { files: [{original_name,url,size}], count } }
    """
    try:
        # 兼容 Element Plus el-upload 单文件字段名为 'file' 的情况
        upload_list: List[UploadFile] = []
        if files and isinstance(files, list) and len(files) > 0:
            upload_list = files
        elif file is not None:
            upload_list = [file]
        else:
            raise HTTPException(status_code=400, detail="没有选择文件")

        uploaded = []
        for f in upload_list:
            if not f or not f.filename:
                continue
            url = await file_service.upload_file(f, folder="images")
            uploaded.append({
                "original_name": f.filename,
                "url": url,
                "size": getattr(f, "size", 0),
            })

        return {
            "code": 200,
            "message": "上传成功",
            "data": {"files": uploaded, "count": len(uploaded)},
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("图片上传失败")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


