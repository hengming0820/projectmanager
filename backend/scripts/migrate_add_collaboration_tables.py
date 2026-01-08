#!/usr/bin/env python3
"""
团队协作文档表迁移脚本
创建 collaboration_documents, document_collaborators, document_edit_history, 
document_comments, collaboration_sessions 表
"""

import sys
import os
import uuid
from datetime import datetime
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal

def get_db_dialect():
    """获取数据库方言"""
    return engine.dialect.name

def table_exists(table_name: str) -> bool:
    """检查表是否存在"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def create_collaboration_documents_table():
    """创建 collaboration_documents 表"""
    dialect = get_db_dialect()
    
    if dialect == 'postgresql':
        sql = """
        CREATE TABLE IF NOT EXISTS collaboration_documents (
            id VARCHAR(36) PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            content TEXT DEFAULT '',
            status VARCHAR(20) DEFAULT 'draft',
            priority VARCHAR(20) DEFAULT 'normal',
            owner_id VARCHAR(50) NOT NULL,
            owner_name VARCHAR(100) NOT NULL,
            project_id VARCHAR(50),
            project_name VARCHAR(200),
            category VARCHAR(100),
            tags JSON,
            last_edited_by VARCHAR(100),
            last_edited_at TIMESTAMP,
            view_count INTEGER DEFAULT 0,
            edit_count INTEGER DEFAULT 0,
            version INTEGER DEFAULT 1,
            is_locked BOOLEAN DEFAULT FALSE,
            locked_by VARCHAR(50),
            locked_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        );
        """
    elif dialect == 'mysql':
        sql = """
        CREATE TABLE IF NOT EXISTS collaboration_documents (
            id VARCHAR(36) PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            content LONGTEXT DEFAULT '',
            status VARCHAR(20) DEFAULT 'draft',
            priority VARCHAR(20) DEFAULT 'normal',
            owner_id VARCHAR(50) NOT NULL,
            owner_name VARCHAR(100) NOT NULL,
            project_id VARCHAR(50),
            project_name VARCHAR(200),
            category VARCHAR(100),
            tags JSON,
            last_edited_by VARCHAR(100),
            last_edited_at TIMESTAMP NULL,
            view_count INTEGER DEFAULT 0,
            edit_count INTEGER DEFAULT 0,
            version INTEGER DEFAULT 1,
            is_locked TINYINT(1) DEFAULT 0,
            locked_by VARCHAR(50),
            locked_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        );
        """
    else:  # SQLite
        sql = """
        CREATE TABLE IF NOT EXISTS collaboration_documents (
            id VARCHAR(36) PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            content TEXT DEFAULT '',
            status VARCHAR(20) DEFAULT 'draft',
            priority VARCHAR(20) DEFAULT 'normal',
            owner_id VARCHAR(50) NOT NULL,
            owner_name VARCHAR(100) NOT NULL,
            project_id VARCHAR(50),
            project_name VARCHAR(200),
            category VARCHAR(100),
            tags TEXT,
            last_edited_by VARCHAR(100),
            last_edited_at TIMESTAMP,
            view_count INTEGER DEFAULT 0,
            edit_count INTEGER DEFAULT 0,
            version INTEGER DEFAULT 1,
            is_locked BOOLEAN DEFAULT 0,
            locked_by VARCHAR(50),
            locked_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        );
        """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    print("✅ collaboration_documents 表创建成功")

def create_document_collaborators_table():
    """创建 document_collaborators 表"""
    dialect = get_db_dialect()
    
    if dialect == 'postgresql':
        sql = """
        CREATE TABLE IF NOT EXISTS document_collaborators (
            id VARCHAR(36) PRIMARY KEY,
            document_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            user_name VARCHAR(100) NOT NULL,
            user_avatar VARCHAR(500),
            role VARCHAR(20) DEFAULT 'editor',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES collaboration_documents(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(document_id, user_id)
        );
        """
    elif dialect == 'mysql':
        sql = """
        CREATE TABLE IF NOT EXISTS document_collaborators (
            id VARCHAR(36) PRIMARY KEY,
            document_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            user_name VARCHAR(100) NOT NULL,
            user_avatar VARCHAR(500),
            role VARCHAR(20) DEFAULT 'editor',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES collaboration_documents(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE KEY unique_document_user (document_id, user_id)
        );
        """
    else:  # SQLite
        sql = """
        CREATE TABLE IF NOT EXISTS document_collaborators (
            id VARCHAR(36) PRIMARY KEY,
            document_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            user_name VARCHAR(100) NOT NULL,
            user_avatar VARCHAR(500),
            role VARCHAR(20) DEFAULT 'editor',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES collaboration_documents(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(document_id, user_id)
        );
        """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    print("✅ document_collaborators 表创建成功")

def create_document_edit_history_table():
    """创建 document_edit_history 表"""
    dialect = get_db_dialect()
    
    if dialect == 'postgresql':
        sql = """
        CREATE TABLE IF NOT EXISTS document_edit_history (
            id VARCHAR(36) PRIMARY KEY,
            document_id VARCHAR(50) NOT NULL,
            editor_id VARCHAR(50) NOT NULL,
            editor_name VARCHAR(100) NOT NULL,
            action VARCHAR(20) NOT NULL,
            changes_summary TEXT,
            content_diff TEXT,
            version_before INTEGER,
            version_after INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES collaboration_documents(id) ON DELETE CASCADE,
            FOREIGN KEY (editor_id) REFERENCES users(id)
        );
        """
    elif dialect == 'mysql':
        sql = """
        CREATE TABLE IF NOT EXISTS document_edit_history (
            id VARCHAR(36) PRIMARY KEY,
            document_id VARCHAR(50) NOT NULL,
            editor_id VARCHAR(50) NOT NULL,
            editor_name VARCHAR(100) NOT NULL,
            action VARCHAR(20) NOT NULL,
            changes_summary TEXT,
            content_diff LONGTEXT,
            version_before INTEGER,
            version_after INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES collaboration_documents(id) ON DELETE CASCADE,
            FOREIGN KEY (editor_id) REFERENCES users(id)
        );
        """
    else:  # SQLite
        sql = """
        CREATE TABLE IF NOT EXISTS document_edit_history (
            id VARCHAR(36) PRIMARY KEY,
            document_id VARCHAR(50) NOT NULL,
            editor_id VARCHAR(50) NOT NULL,
            editor_name VARCHAR(100) NOT NULL,
            action VARCHAR(20) NOT NULL,
            changes_summary TEXT,
            content_diff TEXT,
            version_before INTEGER,
            version_after INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES collaboration_documents(id) ON DELETE CASCADE,
            FOREIGN KEY (editor_id) REFERENCES users(id)
        );
        """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    print("✅ document_edit_history 表创建成功")

def create_document_comments_table():
    """创建 document_comments 表"""
    dialect = get_db_dialect()
    
    if dialect == 'postgresql':
        sql = """
        CREATE TABLE IF NOT EXISTS document_comments (
            id VARCHAR(36) PRIMARY KEY,
            document_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            user_name VARCHAR(100) NOT NULL,
            user_avatar VARCHAR(500),
            content TEXT NOT NULL,
            position INTEGER,
            parent_id VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES collaboration_documents(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (parent_id) REFERENCES document_comments(id) ON DELETE CASCADE
        );
        """
    elif dialect == 'mysql':
        sql = """
        CREATE TABLE IF NOT EXISTS document_comments (
            id VARCHAR(36) PRIMARY KEY,
            document_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            user_name VARCHAR(100) NOT NULL,
            user_avatar VARCHAR(500),
            content TEXT NOT NULL,
            position INTEGER,
            parent_id VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES collaboration_documents(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (parent_id) REFERENCES document_comments(id) ON DELETE CASCADE
        );
        """
    else:  # SQLite
        sql = """
        CREATE TABLE IF NOT EXISTS document_comments (
            id VARCHAR(36) PRIMARY KEY,
            document_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            user_name VARCHAR(100) NOT NULL,
            user_avatar VARCHAR(500),
            content TEXT NOT NULL,
            position INTEGER,
            parent_id VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES collaboration_documents(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (parent_id) REFERENCES document_comments(id) ON DELETE CASCADE
        );
        """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    print("✅ document_comments 表创建成功")

def create_collaboration_sessions_table():
    """创建 collaboration_sessions 表"""
    dialect = get_db_dialect()
    
    if dialect == 'postgresql':
        sql = """
        CREATE TABLE IF NOT EXISTS collaboration_sessions (
            id VARCHAR(36) PRIMARY KEY,
            document_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            user_name VARCHAR(100) NOT NULL,
            session_id VARCHAR(100) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            cursor_position INTEGER,
            selection_start INTEGER,
            selection_end INTEGER,
            last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES collaboration_documents(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    elif dialect == 'mysql':
        sql = """
        CREATE TABLE IF NOT EXISTS collaboration_sessions (
            id VARCHAR(36) PRIMARY KEY,
            document_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            user_name VARCHAR(100) NOT NULL,
            session_id VARCHAR(100) NOT NULL,
            is_active TINYINT(1) DEFAULT 1,
            cursor_position INTEGER,
            selection_start INTEGER,
            selection_end INTEGER,
            last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES collaboration_documents(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    else:  # SQLite
        sql = """
        CREATE TABLE IF NOT EXISTS collaboration_sessions (
            id VARCHAR(36) PRIMARY KEY,
            document_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            user_name VARCHAR(100) NOT NULL,
            session_id VARCHAR(100) NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            cursor_position INTEGER,
            selection_start INTEGER,
            selection_end INTEGER,
            last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES collaboration_documents(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    print("✅ collaboration_sessions 表创建成功")

def create_indexes():
    """创建索引"""
    indexes = [
        # collaboration_documents 索引
        "CREATE INDEX IF NOT EXISTS idx_collaboration_documents_owner ON collaboration_documents(owner_id);",
        "CREATE INDEX IF NOT EXISTS idx_collaboration_documents_status ON collaboration_documents(status);",
        "CREATE INDEX IF NOT EXISTS idx_collaboration_documents_priority ON collaboration_documents(priority);",
        "CREATE INDEX IF NOT EXISTS idx_collaboration_documents_project ON collaboration_documents(project_id);",
        "CREATE INDEX IF NOT EXISTS idx_collaboration_documents_category ON collaboration_documents(category);",
        "CREATE INDEX IF NOT EXISTS idx_collaboration_documents_created ON collaboration_documents(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_collaboration_documents_updated ON collaboration_documents(updated_at);",
        
        # document_collaborators 索引
        "CREATE INDEX IF NOT EXISTS idx_document_collaborators_document ON document_collaborators(document_id);",
        "CREATE INDEX IF NOT EXISTS idx_document_collaborators_user ON document_collaborators(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_document_collaborators_role ON document_collaborators(role);",
        
        # document_edit_history 索引
        "CREATE INDEX IF NOT EXISTS idx_document_edit_history_document ON document_edit_history(document_id);",
        "CREATE INDEX IF NOT EXISTS idx_document_edit_history_editor ON document_edit_history(editor_id);",
        "CREATE INDEX IF NOT EXISTS idx_document_edit_history_action ON document_edit_history(action);",
        "CREATE INDEX IF NOT EXISTS idx_document_edit_history_created ON document_edit_history(created_at);",
        
        # document_comments 索引
        "CREATE INDEX IF NOT EXISTS idx_document_comments_document ON document_comments(document_id);",
        "CREATE INDEX IF NOT EXISTS idx_document_comments_user ON document_comments(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_document_comments_parent ON document_comments(parent_id);",
        
        # collaboration_sessions 索引
        "CREATE INDEX IF NOT EXISTS idx_collaboration_sessions_document ON collaboration_sessions(document_id);",
        "CREATE INDEX IF NOT EXISTS idx_collaboration_sessions_user ON collaboration_sessions(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_collaboration_sessions_active ON collaboration_sessions(is_active);",
        "CREATE INDEX IF NOT EXISTS idx_collaboration_sessions_heartbeat ON collaboration_sessions(last_heartbeat);",
    ]
    
    with engine.connect() as conn:
        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
            except Exception as e:
                print(f"⚠️  索引创建可能失败（可能已存在）: {e}")
        conn.commit()
    print("✅ 索引创建完成")

def insert_sample_data():
    """插入示例数据"""
    print("📝 插入示例协作文档数据...")
    
    with engine.connect() as conn:
        # 检查是否已有数据
        result = conn.execute(text("SELECT COUNT(*) as count FROM collaboration_documents"))
        count = result.fetchone()[0]
        
        if count == 0:
            # 获取第一个用户作为示例所有者
            user_result = conn.execute(text("SELECT id, username FROM users LIMIT 1"))
            user = user_result.fetchone()
            
            if user:
                user_id, username = user
                
                sample_documents = [
                    {
                        'id': str(uuid.uuid4()),
                        'title': '项目需求分析文档',
                        'description': '详细分析项目的功能需求和技术需求',
                        'content': '<h1>项目需求分析</h1><p>这是一个示例协作文档，用于团队协作编辑项目需求。</p>',
                        'status': 'active',
                        'priority': 'high',
                        'owner_id': user_id,
                        'owner_name': username,
                        'category': '需求文档',
                        'tags': '["需求分析", "项目管理", "协作"]',
                        'view_count': 5,
                        'edit_count': 3,
                        'version': 1,
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    },
                    {
                        'id': str(uuid.uuid4()),
                        'title': '技术方案设计',
                        'description': '系统架构和技术选型方案',
                        'content': '<h1>技术方案设计</h1><p>本文档用于记录技术方案的设计思路和实现细节。</p>',
                        'status': 'draft',
                        'priority': 'normal',
                        'owner_id': user_id,
                        'owner_name': username,
                        'category': '技术文档',
                        'tags': '["技术方案", "架构设计", "协作"]',
                        'view_count': 2,
                        'edit_count': 1,
                        'version': 1,
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    }
                ]
                
                for doc in sample_documents:
                    # 处理 SQLite 的 tags 字段
                    if get_db_dialect() == 'sqlite':
                        doc['tags'] = doc['tags']  # SQLite 存储为 TEXT
                    
                    sql = text("""
                    INSERT INTO collaboration_documents 
                    (id, title, description, content, status, priority, owner_id, owner_name, 
                     category, tags, view_count, edit_count, version, created_at, updated_at)
                    VALUES 
                    (:id, :title, :description, :content, :status, :priority, :owner_id, :owner_name,
                     :category, :tags, :view_count, :edit_count, :version, :created_at, :updated_at)
                    """)
                    
                    conn.execute(sql, doc)
                
                conn.commit()
                print("✅ 示例协作文档数据插入成功")
            else:
                print("⚠️  没有找到用户数据，跳过示例数据插入")
        else:
            print("ℹ️  协作文档数据已存在，跳过插入")

def verify_migration():
    """验证迁移结果"""
    print("\n🔍 验证迁移结果...")
    
    tables_to_check = [
        'collaboration_documents',
        'document_collaborators', 
        'document_edit_history',
        'document_comments',
        'collaboration_sessions'
    ]
    
    with engine.connect() as conn:
        for table in tables_to_check:
            if table_exists(table):
                result = conn.execute(text(f"SELECT COUNT(*) as count FROM {table}"))
                count = result.fetchone()[0]
                print(f"✅ {table} 表存在，记录数: {count}")
            else:
                print(f"❌ {table} 表不存在")

def main():
    """主函数"""
    print("🚀 开始团队协作文档表迁移...")
    
    try:
        # 创建表
        create_collaboration_documents_table()
        create_document_collaborators_table()
        create_document_edit_history_table()
        create_document_comments_table()
        create_collaboration_sessions_table()
        
        # 创建索引
        create_indexes()
        
        # 插入示例数据
        insert_sample_data()
        
        # 验证结果
        verify_migration()
        
        print("\n🎉 团队协作文档表迁移完成！")
        print("\n📋 下一步操作:")
        print("1. 更新用户角色权限，添加 'CollaborationManagement' 权限")
        print("2. 重新登录以刷新权限缓存")
        print("3. 访问 /project/collaboration 开始使用团队协作功能")
        
    except SQLAlchemyError as e:
        print(f"❌ 数据库操作失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
