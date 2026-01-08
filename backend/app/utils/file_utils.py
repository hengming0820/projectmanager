import os
import uuid
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from datetime import timedelta
from minio import Minio
from minio.error import S3Error
from app.config import settings
import logging
import io
from urllib.parse import urlparse


class FileService:
    def __init__(self):
        # 确保端点不包含协议前缀
        endpoint = settings.MINIO_ENDPOINT.replace('http://', '').replace('https://', '')

        self.minio_client = Minio(
            endpoint,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET
        self._ensure_bucket_exists()
        self.logger = logging.getLogger(__name__)

    def _ensure_bucket_exists(self):
        """确保存储桶存在"""
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
                self.logger.info(f"创建存储桶: {self.bucket_name}")
        except S3Error as e:
            self.logger.error(f"MinIO存储桶操作失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"存储服务初始化失败: {str(e)}"
            )
        except Exception as e:
            self.logger.error(f"连接MinIO失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="无法连接文件存储服务"
            )

    def _validate_file(self, file: UploadFile) -> bool:
        """验证文件"""
        # 检查文件是否存在
        if not file:
            raise HTTPException(status_code=400, detail="未提供文件")

        # 检查文件大小
        max_size = settings.MAX_FILE_SIZE
        if hasattr(file, 'size') and file.size and file.size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制 ({max_size / 1024 / 1024}MB)"
            )

        # 检查文件类型
        allowed_types = [
            "image/jpeg", "image/jpg", "image/png", "image/gif",
            "image/webp", "image/bmp", "image/tiff", "image/svg+xml"
        ]

        if not file.content_type or file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="不支持的文件类型，只允许图片文件 (JPEG, PNG, GIF, WebP, BMP, TIFF, SVG)"
            )

        return True

    async def upload_file(self, file: UploadFile, folder: str = "uploads") -> str:
        """上传文件到MinIO"""
        try:
            self._validate_file(file)

            # 生成唯一文件名
            file_extension = os.path.splitext(file.filename or "file")[1].lower()
            if not file_extension:
                # 根据内容类型推断扩展名
                content_to_extension = {
                    "image/jpeg": ".jpg",
                    "image/png": ".png",
                    "image/gif": ".gif",
                    "image/webp": ".webp",
                    "image/bmp": ".bmp",
                    "image/tiff": ".tiff",
                    "image/svg+xml": ".svg"
                }
                file_extension = content_to_extension.get(file.content_type, ".bin")

            unique_filename = f"{folder}/{uuid.uuid4()}{file_extension}"

            # 读取文件内容
            content = await file.read()
            file_size = len(content)
            data_stream = io.BytesIO(content)

            # 验证文件大小（如果之前无法获取）
            if file_size > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"文件大小超过限制 ({settings.MAX_FILE_SIZE / 1024 / 1024}MB)"
                )

            # 上传文件
            self.logger.info(f"开始上传文件: {unique_filename}, 大小: {file_size} 字节")

            self.minio_client.put_object(
                self.bucket_name,
                unique_filename,
                data_stream,
                file_size,
                content_type=file.content_type
            )

            self.logger.info(f"文件上传成功: {unique_filename}")

            # 返回访问URL
            return self._get_file_url(unique_filename)

        except HTTPException:
            raise
        except S3Error as e:
            self.logger.error(f"MinIO上传失败: {str(e)}")
            raise HTTPException(status_code=500, detail="文件存储服务错误")
        except Exception as e:
            self.logger.error(f"文件上传失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

    def _get_file_url(self, object_name: str) -> str:
        """生成文件访问URL"""
        if settings.MINIO_PRESIGNED_SECONDS and settings.MINIO_PRESIGNED_SECONDS > 0:
            # 生成预签名URL
            url = self.minio_client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=settings.MINIO_PRESIGNED_SECONDS)
            )
            self.logger.info(f"生成预签名URL: 有效期 {settings.MINIO_PRESIGNED_SECONDS}秒")
            return url
        else:
            # 代理或直链 URL
            if getattr(settings, 'MINIO_PROXY_PUBLIC', False):
                # 经由后端代理，避免暴露 MinIO 端口
                return f"/api/files/{object_name}"
            protocol = "https" if settings.MINIO_SECURE else "http"
            public_host = settings.MINIO_PUBLIC_ENDPOINT or settings.MINIO_ENDPOINT
            public_host = public_host.replace('http://', '').replace('https://', '')
            return f"{protocol}://{public_host}/{self.bucket_name}/{object_name}"

    async def upload_annotation_screenshots(self, task_id: str, files: List[UploadFile]) -> List[str]:
        """上传标注截图"""
        urls = []
        for file in files:
            try:
                url = await self.upload_file(file, f"annotations/{task_id}")
                urls.append(url)
            except HTTPException as e:
                self.logger.warning(f"标注截图上传失败: {file.filename}, 错误: {e.detail}")
                # 可以选择继续处理其他文件或抛出异常
                continue
        return urls

    async def upload_review_screenshots(self, task_id: str, files: List[UploadFile]) -> List[str]:
        """上传审核截图"""
        urls = []
        for file in files:
            try:
                url = await self.upload_file(file, f"reviews/{task_id}")
                urls.append(url)
            except HTTPException as e:
                self.logger.warning(f"审核截图上传失败: {file.filename}, 错误: {e.detail}")
                continue
        return urls

    async def delete_file(self, file_url: str) -> bool:
        """删除文件"""
        try:
            # 从URL中提取对象名
            parsed_url = urlparse(file_url)
            path_parts = parsed_url.path.split('/')

            # 查找bucket名称后的路径部分
            if self.bucket_name in path_parts:
                bucket_index = path_parts.index(self.bucket_name)
                object_name = '/'.join(path_parts[bucket_index + 1:])

                self.minio_client.remove_object(self.bucket_name, object_name)
                self.logger.info(f"文件删除成功: {object_name}")
                return True
            else:
                self.logger.warning(f"无法从URL中提取对象名: {file_url}")
                return False

        except S3Error as e:
            if e.code == 'NoSuchKey':
                self.logger.warning(f"文件不存在: {file_url}")
                return False
            else:
                self.logger.error(f"MinIO删除失败: {str(e)}")
                return False
        except Exception as e:
            self.logger.error(f"文件删除失败: {str(e)}")
            return False

    def get_file_info(self, object_name: str) -> Optional[dict]:
        """获取文件信息"""
        try:
            stat = self.minio_client.stat_object(self.bucket_name, object_name)
            return {
                'size': stat.size,
                'content_type': stat.content_type,
                'last_modified': stat.last_modified
            }
        except S3Error:
            return None

    async def upload_avatar(self, user_id: str, file: UploadFile) -> str:
        """上传用户头像，返回访问URL"""
        # 允许常见图片格式
        self._validate_file(file)
        content = await file.read()
        data_stream = io.BytesIO(content)
        object_name = f"avatars/{user_id}.png"
        self.minio_client.put_object(
            self.bucket_name,
            object_name,
            data_stream,
            len(content),
            content_type=file.content_type
        )
        return self._get_file_url(object_name)


# 全局文件服务实例
file_service = FileService()