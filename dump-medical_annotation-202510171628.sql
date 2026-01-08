--
-- PostgreSQL database cluster dump
--

-- Started on 2025-10-17 16:28:16

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE admin;
ALTER ROLE admin WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS;

--
-- User Configurations
--








--
-- Databases
--

--
-- Database "template1" dump
--

\connect template1

--
-- PostgreSQL database dump
--

-- Dumped from database version 16.10
-- Dumped by pg_dump version 17.0

-- Started on 2025-10-17 16:28:16

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

-- Completed on 2025-10-17 16:28:17

--
-- PostgreSQL database dump complete
--

--
-- Database "medical_annotation" dump
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 16.10
-- Dumped by pg_dump version 17.0

-- Started on 2025-10-17 16:28:17

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 3651 (class 1262 OID 24869)
-- Name: medical_annotation; Type: DATABASE; Schema: -; Owner: admin
--

CREATE DATABASE medical_annotation WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';


ALTER DATABASE medical_annotation OWNER TO admin;

\connect medical_annotation

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 215 (class 1259 OID 24870)
-- Name: article_edit_history; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.article_edit_history (
    id character varying(36) NOT NULL,
    article_id character varying(36) NOT NULL,
    editor_id character varying(50) NOT NULL,
    editor_name character varying(100) NOT NULL,
    action character varying(30) NOT NULL,
    changes_summary text,
    version_before integer,
    version_after integer,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.article_edit_history OWNER TO admin;

--
-- TOC entry 3652 (class 0 OID 0)
-- Dependencies: 215
-- Name: COLUMN article_edit_history.action; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.article_edit_history.action IS 'create, update, publish, delete, edit_content';


--
-- TOC entry 216 (class 1259 OID 24876)
-- Name: articles; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.articles (
    id character varying(36) NOT NULL,
    title character varying(200) NOT NULL,
    content text,
    summary text,
    type character varying(50) NOT NULL,
    status character varying(20),
    tags json,
    author_id character varying(50) NOT NULL,
    author_name character varying(100) NOT NULL,
    view_count integer,
    edit_count integer,
    version integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    cover_url character varying(500),
    category character varying(50),
    is_public boolean DEFAULT true,
    editable_user_ids jsonb DEFAULT '[]'::jsonb,
    editable_roles jsonb DEFAULT '[]'::jsonb,
    departments jsonb DEFAULT '[]'::jsonb,
    is_locked boolean DEFAULT false,
    locked_by character varying(50),
    locked_at timestamp with time zone,
    project_id character varying(36)
);


ALTER TABLE public.articles OWNER TO admin;

--
-- TOC entry 3653 (class 0 OID 0)
-- Dependencies: 216
-- Name: COLUMN articles.title; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.articles.title IS '标题';


--
-- TOC entry 3654 (class 0 OID 0)
-- Dependencies: 216
-- Name: COLUMN articles.content; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.articles.content IS '内容（富文本HTML）';


--
-- TOC entry 3655 (class 0 OID 0)
-- Dependencies: 216
-- Name: COLUMN articles.summary; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.articles.summary IS '摘要';


--
-- TOC entry 3656 (class 0 OID 0)
-- Dependencies: 216
-- Name: COLUMN articles.type; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.articles.type IS '类型：meeting / model_test';


--
-- TOC entry 3657 (class 0 OID 0)
-- Dependencies: 216
-- Name: COLUMN articles.status; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.articles.status IS '状态：draft, published';


--
-- TOC entry 3658 (class 0 OID 0)
-- Dependencies: 216
-- Name: COLUMN articles.tags; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.articles.tags IS '标签';


--
-- TOC entry 3659 (class 0 OID 0)
-- Dependencies: 216
-- Name: COLUMN articles.author_id; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.articles.author_id IS '作者ID';


--
-- TOC entry 3660 (class 0 OID 0)
-- Dependencies: 216
-- Name: COLUMN articles.author_name; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.articles.author_name IS '作者姓名';


--
-- TOC entry 3661 (class 0 OID 0)
-- Dependencies: 216
-- Name: COLUMN articles.is_locked; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.articles.is_locked IS '是否被锁定（有人正在编辑）';


--
-- TOC entry 3662 (class 0 OID 0)
-- Dependencies: 216
-- Name: COLUMN articles.locked_by; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.articles.locked_by IS '锁定者用户ID';


--
-- TOC entry 3663 (class 0 OID 0)
-- Dependencies: 216
-- Name: COLUMN articles.locked_at; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.articles.locked_at IS '锁定时间';


--
-- TOC entry 217 (class 1259 OID 24887)
-- Name: collaboration_documents; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.collaboration_documents (
    id character varying(36) NOT NULL,
    title character varying(200) NOT NULL,
    description text,
    content text DEFAULT ''::text,
    status character varying(20) DEFAULT 'draft'::character varying,
    priority character varying(20) DEFAULT 'normal'::character varying,
    owner_id character varying(50) NOT NULL,
    owner_name character varying(100) NOT NULL,
    project_id character varying(50),
    project_name character varying(200),
    category character varying(100),
    tags json,
    last_edited_by character varying(100),
    last_edited_at timestamp without time zone,
    view_count integer DEFAULT 0,
    edit_count integer DEFAULT 0,
    version integer DEFAULT 1,
    is_locked boolean DEFAULT false,
    locked_by character varying(50),
    locked_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.collaboration_documents OWNER TO admin;

--
-- TOC entry 218 (class 1259 OID 24901)
-- Name: collaboration_sessions; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.collaboration_sessions (
    id character varying(36) NOT NULL,
    document_id character varying(50) NOT NULL,
    user_id character varying(50) NOT NULL,
    user_name character varying(100) NOT NULL,
    session_id character varying(100) NOT NULL,
    is_active boolean DEFAULT true,
    cursor_position integer,
    selection_start integer,
    selection_end integer,
    last_heartbeat timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.collaboration_sessions OWNER TO admin;

--
-- TOC entry 219 (class 1259 OID 24908)
-- Name: document_collaborators; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.document_collaborators (
    id character varying(36) NOT NULL,
    document_id character varying(50) NOT NULL,
    user_id character varying(50) NOT NULL,
    user_name character varying(100) NOT NULL,
    user_avatar character varying(500),
    role character varying(20) DEFAULT 'editor'::character varying,
    joined_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    last_active_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.document_collaborators OWNER TO admin;

--
-- TOC entry 220 (class 1259 OID 24917)
-- Name: document_comments; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.document_comments (
    id character varying(36) NOT NULL,
    document_id character varying(50) NOT NULL,
    user_id character varying(50) NOT NULL,
    user_name character varying(100) NOT NULL,
    user_avatar character varying(500),
    content text NOT NULL,
    "position" integer,
    parent_id character varying(50),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.document_comments OWNER TO admin;

--
-- TOC entry 221 (class 1259 OID 24924)
-- Name: document_edit_history; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.document_edit_history (
    id character varying(36) NOT NULL,
    document_id character varying(50) NOT NULL,
    editor_id character varying(50) NOT NULL,
    editor_name character varying(100) NOT NULL,
    action character varying(20) NOT NULL,
    changes_summary text,
    content_diff text,
    version_before integer,
    version_after integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.document_edit_history OWNER TO admin;

--
-- TOC entry 222 (class 1259 OID 24931)
-- Name: performance_stats; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.performance_stats (
    id character varying(36) NOT NULL,
    user_id character varying(36) NOT NULL,
    period character varying(20) NOT NULL,
    date character varying(10) NOT NULL,
    total_tasks integer,
    completed_tasks integer,
    approved_tasks integer,
    rejected_tasks integer,
    total_score integer,
    average_score numeric(5,2),
    total_hours numeric(5,2),
    average_hours numeric(5,2),
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.performance_stats OWNER TO admin;

--
-- TOC entry 232 (class 1259 OID 49153)
-- Name: project_categories; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.project_categories (
    id character varying(36) NOT NULL,
    project_id character varying(36) NOT NULL,
    name character varying(100) NOT NULL,
    type character varying(50) NOT NULL,
    icon character varying(50),
    description text,
    sort_order integer DEFAULT 0,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.project_categories OWNER TO admin;

--
-- TOC entry 3664 (class 0 OID 0)
-- Dependencies: 232
-- Name: TABLE project_categories; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON TABLE public.project_categories IS '项目文章分类表';


--
-- TOC entry 3665 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN project_categories.id; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.project_categories.id IS '分类ID';


--
-- TOC entry 3666 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN project_categories.project_id; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.project_categories.project_id IS '所属项目ID';


--
-- TOC entry 3667 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN project_categories.name; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.project_categories.name IS '分类名称（显示名）';


--
-- TOC entry 3668 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN project_categories.type; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.project_categories.type IS '分类类型标识（用于article.type）';


--
-- TOC entry 3669 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN project_categories.icon; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.project_categories.icon IS '图标';


--
-- TOC entry 3670 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN project_categories.description; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.project_categories.description IS '分类描述';


--
-- TOC entry 3671 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN project_categories.sort_order; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.project_categories.sort_order IS '排序顺序';


--
-- TOC entry 3672 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN project_categories.created_at; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.project_categories.created_at IS '创建时间';


--
-- TOC entry 3673 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN project_categories.updated_at; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.project_categories.updated_at IS '更新时间';


--
-- TOC entry 223 (class 1259 OID 24936)
-- Name: project_stats; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.project_stats (
    id character varying(36) NOT NULL,
    project_id character varying(36) NOT NULL,
    total_tasks integer,
    pending_tasks integer,
    in_progress_tasks integer,
    completed_tasks integer,
    approved_tasks integer,
    rejected_tasks integer,
    completion_rate numeric(5,2),
    average_score numeric(5,2),
    total_hours numeric(8,2),
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.project_stats OWNER TO admin;

--
-- TOC entry 224 (class 1259 OID 24941)
-- Name: projects; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.projects (
    id character varying(36) NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    status character varying(20),
    priority character varying(20),
    start_date date NOT NULL,
    end_date date,
    created_by character varying(36) NOT NULL,
    total_tasks integer,
    completed_tasks integer,
    assigned_tasks integer,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    category character varying(50),
    sub_category character varying(50)
);


ALTER TABLE public.projects OWNER TO admin;

--
-- TOC entry 225 (class 1259 OID 24948)
-- Name: roles; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.roles (
    id character varying(36) NOT NULL,
    name character varying(50) NOT NULL,
    role character varying(50) NOT NULL,
    description text,
    is_active boolean,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    permissions text
);


ALTER TABLE public.roles OWNER TO admin;

--
-- TOC entry 226 (class 1259 OID 24955)
-- Name: task_attachments; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.task_attachments (
    id character varying(36) NOT NULL,
    task_id character varying(36) NOT NULL,
    file_name character varying(200) NOT NULL,
    file_url character varying(500) NOT NULL,
    file_size integer,
    file_type character varying(50),
    attachment_type character varying(50),
    uploaded_by character varying(36) NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.task_attachments OWNER TO admin;

--
-- TOC entry 227 (class 1259 OID 24961)
-- Name: tasks; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.tasks (
    id character varying(36) NOT NULL,
    title character varying(200) NOT NULL,
    description text,
    project_id character varying(36) NOT NULL,
    status character varying(20),
    priority character varying(20),
    assigned_to character varying(36),
    created_by character varying(36) NOT NULL,
    image_url character varying(500),
    annotation_data json,
    score integer,
    assigned_at timestamp without time zone,
    submitted_at timestamp without time zone,
    reviewed_by character varying(36),
    reviewed_at timestamp without time zone,
    review_comment text,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    timeline jsonb DEFAULT '[]'::jsonb,
    skipped_at timestamp without time zone,
    skip_reason text,
    skip_images jsonb,
    assigned_to_name character varying(100),
    created_by_name character varying(100),
    reviewed_by_name character varying(100),
    skip_requested_at timestamp without time zone,
    skip_request_reason text,
    skip_request_images json,
    skip_requested_by character varying(36),
    skip_reviewed_at timestamp without time zone,
    skip_reviewed_by character varying(36),
    skip_review_comment text
);


ALTER TABLE public.tasks OWNER TO admin;

--
-- TOC entry 228 (class 1259 OID 24969)
-- Name: users; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.users (
    id character varying(36) NOT NULL,
    username character varying(50) NOT NULL,
    real_name character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(20) NOT NULL,
    avatar_url character varying(500),
    department character varying(100),
    status character varying(20),
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    tags text,
    hire_date date
);


ALTER TABLE public.users OWNER TO admin;

--
-- TOC entry 229 (class 1259 OID 24976)
-- Name: work_log_entries; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.work_log_entries (
    id character varying(36) NOT NULL,
    work_week_id character varying(36) NOT NULL,
    user_id character varying(36) NOT NULL,
    work_date date NOT NULL,
    day_of_week integer NOT NULL,
    work_content text,
    work_type character varying(50),
    priority character varying(20),
    planned_hours integer,
    actual_hours integer,
    status character varying(20),
    completion_rate integer,
    difficulties text,
    next_day_plan text,
    remarks text,
    submitted_at timestamp without time zone,
    reviewed_at timestamp without time zone,
    reviewed_by character varying(36),
    review_comment text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.work_log_entries OWNER TO admin;

--
-- TOC entry 3674 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN work_log_entries.work_date; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_entries.work_date IS '工作日期';


--
-- TOC entry 3675 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN work_log_entries.day_of_week; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_entries.day_of_week IS '星期几(1-7, 1=周一)';


--
-- TOC entry 3676 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN work_log_entries.work_content; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_entries.work_content IS '工作内容描述';


--
-- TOC entry 3677 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN work_log_entries.work_type; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_entries.work_type IS '工作类型（开发、测试、会议、学习等）';


--
-- TOC entry 3678 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN work_log_entries.priority; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_entries.priority IS '优先级: low, normal, high, urgent';


--
-- TOC entry 3679 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN work_log_entries.planned_hours; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_entries.planned_hours IS '计划工作小时数';


--
-- TOC entry 3680 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN work_log_entries.actual_hours; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_entries.actual_hours IS '实际工作小时数';


--
-- TOC entry 3681 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN work_log_entries.status; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_entries.status IS '状态: pending, submitted, approved, rejected';


--
-- TOC entry 3682 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN work_log_entries.completion_rate; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_entries.completion_rate IS '完成率(0-100)';


--
-- TOC entry 3683 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN work_log_entries.difficulties; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_entries.difficulties IS '遇到的困难';


--
-- TOC entry 3684 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN work_log_entries.next_day_plan; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_entries.next_day_plan IS '次日计划';


--
-- TOC entry 3685 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN work_log_entries.remarks; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_entries.remarks IS '备注';


--
-- TOC entry 3686 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN work_log_entries.submitted_at; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_entries.submitted_at IS '提交时间';


--
-- TOC entry 3687 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN work_log_entries.reviewed_at; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_entries.reviewed_at IS '审核时间';


--
-- TOC entry 3688 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN work_log_entries.reviewed_by; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_entries.reviewed_by IS '审核人';


--
-- TOC entry 3689 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN work_log_entries.review_comment; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_entries.review_comment IS '审核意见';


--
-- TOC entry 230 (class 1259 OID 24981)
-- Name: work_log_types; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.work_log_types (
    id character varying(36) NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    color character varying(7),
    icon character varying(50),
    is_active boolean,
    sort_order integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.work_log_types OWNER TO admin;

--
-- TOC entry 3690 (class 0 OID 0)
-- Dependencies: 230
-- Name: COLUMN work_log_types.name; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_types.name IS '类型名称';


--
-- TOC entry 3691 (class 0 OID 0)
-- Dependencies: 230
-- Name: COLUMN work_log_types.description; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_types.description IS '类型描述';


--
-- TOC entry 3692 (class 0 OID 0)
-- Dependencies: 230
-- Name: COLUMN work_log_types.color; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_types.color IS '显示颜色';


--
-- TOC entry 3693 (class 0 OID 0)
-- Dependencies: 230
-- Name: COLUMN work_log_types.icon; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_types.icon IS '图标';


--
-- TOC entry 3694 (class 0 OID 0)
-- Dependencies: 230
-- Name: COLUMN work_log_types.is_active; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_types.is_active IS '是否启用';


--
-- TOC entry 3695 (class 0 OID 0)
-- Dependencies: 230
-- Name: COLUMN work_log_types.sort_order; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_log_types.sort_order IS '排序';


--
-- TOC entry 231 (class 1259 OID 24986)
-- Name: work_weeks; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.work_weeks (
    id character varying(36) NOT NULL,
    title character varying(255) NOT NULL,
    week_start_date date NOT NULL,
    week_end_date date NOT NULL,
    description text,
    status character varying(20),
    config json,
    created_by character varying(36) NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.work_weeks OWNER TO admin;

--
-- TOC entry 3696 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN work_weeks.title; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_weeks.title IS '工作周标题';


--
-- TOC entry 3697 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN work_weeks.week_start_date; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_weeks.week_start_date IS '周开始日期（周一）';


--
-- TOC entry 3698 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN work_weeks.week_end_date; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_weeks.week_end_date IS '周结束日期（周五）';


--
-- TOC entry 3699 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN work_weeks.description; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_weeks.description IS '工作周描述';


--
-- TOC entry 3700 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN work_weeks.status; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_weeks.status IS '状态: active, archived, deleted';


--
-- TOC entry 3701 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN work_weeks.config; Type: COMMENT; Schema: public; Owner: admin
--

COMMENT ON COLUMN public.work_weeks.config IS '周配置信息（如工作日类型、要求等）';


--
-- TOC entry 3628 (class 0 OID 24870)
-- Dependencies: 215
-- Data for Name: article_edit_history; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.article_edit_history (id, article_id, editor_id, editor_name, action, changes_summary, version_before, version_after, created_at) FROM stdin;
8ae64ce2-9dbe-41a5-b7d2-d0d5ad9e649d	a37cc2ea-72d4-4e48-a41f-21afe9e57014	user1	系统管理员	create	创建文章: 模型测试	\N	1	2025-09-11 06:15:01.129046+00
f833f3b0-fa27-4d3b-b985-1a93531d570a	14330820-e822-4ace-8c11-0f7910c6cedc	user1	系统管理员	create	创建文章: 模型测试20250911	\N	1	2025-09-11 06:36:07.750551+00
bd3b43c1-00d2-4ef1-bce6-7aa070801363	d7405937-3a98-4bb5-b163-291fc3fb61b3	user1	系统管理员	create	创建文章: 20250928泌尿测试	\N	1	2025-09-28 07:18:21.049328+00
5573a96b-16e9-4335-a81e-0433e5ffade3	d7405937-3a98-4bb5-b163-291fc3fb61b3	user1	系统管理员	update	编辑内容	1	2	2025-09-28 07:37:49.579174+00
9a61422f-f926-411d-a9d3-ff94bca738d5	ba2794d7-0294-4596-9132-cc43b18b1b2a	user1	系统管理员	create	创建文章: # 公司编码风格守则（C/C++ & Python）	\N	1	2025-09-30 07:15:39.261199+00
63330e3f-7f1f-4a80-a94e-59ffc8f82e67	ba2794d7-0294-4596-9132-cc43b18b1b2a	user1	系统管理员	update	更新封面; 可编辑成员变更; 可编辑角色变更; 所属部门变更	1	2	2025-09-30 07:39:26.375034+00
d4ccf08c-be0a-4711-b543-598905b76f05	9047a0ef-3d9a-4174-87b4-1bcb83662b16	user1	系统管理员	create	创建文章: # nnUNet 模型综合测试报告	\N	1	2025-10-15 07:08:45.44927+00
521f065d-bc22-4bae-9f06-f51d6d9fdda5	affd3e17-bb2d-477a-bddd-2344d7306adf	user1	系统管理员	create	创建文章: # 述职报告PPT大纲	\N	1	2025-10-17 08:04:56.753327+00
edac6ba3-30d1-4c2c-a05c-3e3316b3f383	ea34a309-7ebb-4ef5-816b-2dffb093bdea	user1	系统管理员	create	创建文章: 多所属部门测试	\N	1	2025-10-17 08:07:06.494552+00
a6e7e21a-a7e2-4aec-b3db-c521f820f01d	affd3e17-bb2d-477a-bddd-2344d7306adf	user1	系统管理员	update	可编辑成员变更; 可编辑角色变更; 所属部门变更	1	2	2025-10-17 08:08:03.502187+00
\.


--
-- TOC entry 3629 (class 0 OID 24876)
-- Dependencies: 216
-- Data for Name: articles; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.articles (id, title, content, summary, type, status, tags, author_id, author_name, view_count, edit_count, version, created_at, updated_at, cover_url, category, is_public, editable_user_ids, editable_roles, departments, is_locked, locked_by, locked_at, project_id) FROM stdin;
ba2794d7-0294-4596-9132-cc43b18b1b2a	# 公司编码风格守则（C/C++ & Python）	<h2>1 总则</h2><p>1. 统一风格优先，个人习惯其次 &nbsp;</p><p>2. 命名即注释，代码即文档 &nbsp;</p><p>3. 任何规则若与项目历史冲突，以<strong>最小改动、最大可读性</strong>为原则</p><p>---</p><h2>2 文件与目录结构</h2><p>| 层级 | C/C++ | Python |</p><p>|---|---|---|</p><p>| 源码 | <code>src/</code> 或模块根目录 | 包名全小写，无下划线 |</p><p>| 头文件 | <code>include/</code> 或同级 <code>.h</code> | 不需要 |</p><p>| 测试 | <code>tests/</code> 或 <em><code>_test.cc | tests/ 内以 test_</code></em><code>.py</code> |</p><p>| 示例 | <code>examples/</code> | <code>examples/</code> |</p><p>| 文档 | <code>docs/</code> | <code>docs/</code> |</p><ul><li><strong>禁止</strong>中文路径、空格、特殊符号 &nbsp;</li><li>文件以 <strong>空行结尾</strong></li></ul><p>---</p><h2>2 &nbsp;命名约定</h2><p>| 实体 | C/C++ | Python | 正面示例 | 反面示例 |</p><p>|---|---|---|---|---|</p><p>| <strong>文件名</strong> | <code>snake_case.c/.h</code> | <code>snake_case.py</code> | <code>http_client.c</code> | <code>HttpClient.c</code> |</p><p>| 类型/类 | <code>PascalCase</code> | <code>PascalCase</code> | <code>class PacketParser</code> | <code>class packet_parser</code> |</p><p>| 函数 | <code>camelCase</code> | <code>camelCase</code> | <code>int readPacket();</code> | <code>int read_packet();</code> |</p><p>| 变量 | <code>camelCase</code> | <code>camelCase</code> | <code>int retryCount;</code> | <code>int retry_count;</code> |</p><p>| 常量 | <code>kPascalCase</code> | <code>PASCAL_CASE</code> | <code>constexpr int kMaxRetry = 3;</code> | <code>const int maxRetry = 3;</code> |</p><p>| 宏 | <code>UPPER_SNAKE_CASE</code> | 避免宏 | <code>#define BUFFER_SIZE 1024</code> | <code>#define bufferSize 1024</code> |</p><p>| 私有 | 前缀 <code>_camelCase</code> | 前缀 <code>_camelCase</code> | <code>int _internalState;</code> | <code>int __myVar;</code> |</p><h3>2.1 特殊规则</h3><ul><li><strong>文件命名</strong> &nbsp;</li><li><strong>统一小写+下划线</strong>：<code>http_client.c</code>, <code>packet_parser.py</code> &nbsp;</li><li><strong>禁止</strong>：大写字母、连字符、空格、点（除扩展名）。 &nbsp;</li><li><strong>C++ 常量</strong> &nbsp;</li><li>使用小写 <code>k</code> 前缀：<code>kBufferSize</code> &nbsp;</li><li><strong>Python 全局常量</strong> &nbsp;</li><li>保持 <code>UPPER_SNAKE_CASE</code>：<code>MAX_RETRY = 3</code> &nbsp;</li></ul><p>---</p><h2>4 &nbsp;代码格式</h2><p>以下规则同时适用于 <strong>C/C++</strong> 与 <strong>Python</strong>。如无特别说明，二者保持一致；若存在差异，则在对应小节中分别说明。</p><h3>4.1 &nbsp;缩进与行宽</h3><p>| 语言 &nbsp; | 缩进 | 行宽 | Tab 使用 |</p><p>|--------|------|------|----------|</p><p>| C/C++ &nbsp;| 4 空格 | 100 列 | 允许 |</p><p>| Python | 4 空格 | 100 列 | 允许 |</p><ul><li><strong>连续缩进层级不得超过 4 层</strong>；超过必须重构函数或引入辅助函数。 &nbsp;</li><li><strong>禁止混用空格与 Tab</strong>。</li></ul><p>---</p><h3>4.2 &nbsp;大括号、小括号与空格</h3><h4>4.2.1 &nbsp;大括号（仅 C/C++）</h4><ul><li><strong>左大括号不换行</strong>，与关键字或函数头同行： &nbsp;</li></ul><p> &nbsp;```cpp</p><p> &nbsp;if (condition) {</p><p> &nbsp; &nbsp; &nbsp;doSomething();</p><p> &nbsp;}</p><p> &nbsp;```</p><ul><li><code><strong>单语句也必须加 {}</strong></code>，防止后期插入语句时引入 bug： &nbsp;</li></ul><p> &nbsp;```cpp</p><p> &nbsp;for (int i = 0; i &lt; n; ++i) {</p><p> &nbsp; &nbsp; &nbsp;process(i);</p><p> &nbsp;}</p><p> &nbsp;```</p><ul><li><strong>函数定义</strong> 左大括号换行： &nbsp;</li></ul><p> &nbsp;```cpp</p><p> &nbsp;int add(int a, int b) </p><p> &nbsp;{</p><p> &nbsp; &nbsp; &nbsp;return a + b;</p><p> &nbsp;}</p><p> &nbsp;```</p><h4>4.2.2 &nbsp;小括号</h4><ul><li><strong>小括号内侧不额外加空格</strong>： &nbsp;</li></ul><p> &nbsp;```cpp</p><p> &nbsp;int result = func(a, b);</p><p> &nbsp;```</p><p> &nbsp;```python</p><p> &nbsp;result = func(a, b)</p><p> &nbsp;```</p><ul><li><strong>关键字后留 1 空格再跟小括号</strong>： &nbsp;</li></ul><p> &nbsp;```cpp</p><p> &nbsp;if (x &gt; 0) {</p><p> &nbsp; &nbsp; &nbsp;...</p><p> &nbsp;}</p><p> &nbsp;```</p><p> &nbsp;```python</p><p> &nbsp;if x &gt; 0:</p><p> &nbsp; &nbsp; &nbsp;...</p><p> &nbsp;```</p><ul><li><strong>函数声明与调用</strong> 小括号前 <strong>不空格</strong>： &nbsp;</li></ul><p> &nbsp;```cpp</p><p> &nbsp;int compute(int a, int b); &nbsp; // 正确</p><p> &nbsp;int compute (int a, int b); &nbsp;// 错误</p><p> &nbsp;```</p><p>---</p><h3>4.3 &nbsp;逗号、分号与冒号</h3><ul><li><strong>逗号后留 1 空格</strong>： &nbsp;</li></ul><p> &nbsp;```cpp</p><p> &nbsp;std::vector&lt;int&gt; v = {1, 2, 3, 4};</p><p> &nbsp;```</p><p> &nbsp;```python</p><p> &nbsp;items = [1, 2, 3, 4]</p><p> &nbsp;```</p><ul><li><strong>冒号后留 1 空格</strong>（Python 切片、字典、类型注解）： &nbsp;</li></ul><p> &nbsp;```python</p><p> &nbsp;sub = items[1:3]</p><p> &nbsp;config = {"host": "127.0.0.1"}</p><p> &nbsp;def foo(x: int) -&gt; str:</p><p> &nbsp; &nbsp; &nbsp;...</p><p> &nbsp;```</p><p>---</p><h3>4.4 &nbsp;空行与分段</h3><p>| 场景 | 空行数 |</p><p>|---|---|</p><p>| 文件末尾 | 1 |</p><p>| 函数 / 方法之间 | 2 |</p><p>| 类之间 | 2 |</p><p>| 逻辑段之间（例如变量声明与代码） | 1 |</p><p>示例：</p><pre><code >int helper(int x) {\n    return x * 2;\n}\n\n\nint main() {\n    int base = 5;\n\n    int result = helper(base);\n    return result;\n}</code></pre><p>---</p><h3>4.5 &nbsp;对齐与换行</h3><ul><li><strong>长参数列表</strong> 每行一项，逗号结尾，垂直对齐括号： &nbsp;</li></ul><p> &nbsp;```cpp</p><p> &nbsp;void sendRequest(const std::string& host,</p><p> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; int port,</p><p> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; const std::string& path,</p><p> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; bool use_ssl);</p><p> &nbsp;```</p><ul><li><strong>长表达式</strong> 在运算符后断行，并额外缩进 4 空格： &nbsp;</li></ul><p> &nbsp;```cpp</p><p> &nbsp;bool ok = (value &gt; threshold) &&</p><p> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;(status == Status::kReady) &&</p><p> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;!isCancelled;</p><p> &nbsp;```</p><ul><li><strong>Python 函数/类签名</strong> 过长时，<strong>右括号对齐左括号</strong>： &nbsp;</li></ul><p> &nbsp;```python</p><p> &nbsp;def create_connection(</p><p> &nbsp; &nbsp; &nbsp;host: str,</p><p> &nbsp; &nbsp; &nbsp;port: int,</p><p> &nbsp; &nbsp; &nbsp;timeout: float = 5.0,</p><p> &nbsp;) -&gt; socket.socket:</p><p> &nbsp; &nbsp; &nbsp;...</p><p> &nbsp;```</p><p>---</p><h3>4.6 &nbsp;列表、字典、模板、Lambda</h3><h4>C/C++</h4><ul><li><strong>初始化列表</strong> 内侧空格可选，但需统一；推荐： &nbsp;</li></ul><p> &nbsp;```cpp</p><p> &nbsp;std::map&lt;std::string, int&gt; m{{"one", 1}, {"two", 2}};</p><p> &nbsp;```</p><ul><li><strong>模板尖括号</strong> 内侧不空格： &nbsp;</li></ul><p> &nbsp;```cpp</p><p> &nbsp;std::vector&lt;int&gt; v;</p><p> &nbsp;```</p><h4>Python</h4><ul><li><strong>列表/字典/集合</strong> 内侧空格可选，但须统一；推荐： &nbsp;</li></ul><p> &nbsp;```python</p><p> &nbsp;items = [1, 2, 3]</p><p> &nbsp;mapping = {"key": "value"}</p><p> &nbsp;```</p><ul><li><strong>Lambda</strong> 关键字后空格： &nbsp;</li></ul><p> &nbsp;```python</p><p> &nbsp;square = lambda x: x * x</p><p> &nbsp;```</p><h3>4.7 &nbsp;函数</h3><p>函数应该简短而漂亮，并且只完成一件事情。函数最大行数应该为80行，超过则需要进行拆分，局部变量不应该超过5~10个。</p><p>---</p><h3>4.8 &nbsp;行尾与文件结尾</h3><ul><li><strong>每行仅一条语句</strong>：禁止 <code>a = 1; b = 2;</code> &nbsp;</li><li><strong>文件末尾留一个空行</strong>（POSIX 规范）。</li></ul><p>| 逻辑段之间 | 1 |</p><p>---</p><h2>5 注释与文档</h2><h3>5.1 注释原则</h3><ul><li><strong>Why &gt; What &gt; How</strong> &nbsp;</li><li>行内注释 <code>//</code> 或 <code>#</code> 与代码间隔 2 空格 &nbsp;</li><li>禁止<strong>大段解释代码思路</strong>，应重构代码使其自明</li></ul><h3>5.2 公共 API 文档</h3><ul><li>C/C++：Doxygen 风格 &nbsp;</li></ul><p> &nbsp;```cpp</p><p> &nbsp;/**</p><ul><li>@brief &nbsp;计算 CRC32</li><li>@param &nbsp;data 数据起始指针</li><li>@param &nbsp;len &nbsp;数据长度</li><li>@return CRC32 值</li></ul><p> &nbsp; */</p><p> &nbsp;uint32_t crc32(const uint8_t* data, size_t len);</p><p> &nbsp;```</p><ul><li>Python：Google 风格 &nbsp;</li></ul><p> &nbsp;```python</p><p> &nbsp;def crc32(data: bytes) -&gt; int:</p><p> &nbsp; &nbsp; &nbsp;"""计算 CRC32.</p><p> &nbsp; &nbsp; &nbsp;Args:</p><p> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;data: 待校验字节串.</p><p> &nbsp; &nbsp; &nbsp;Returns:</p><p> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;CRC32 无符号整数.</p><p> &nbsp; &nbsp; &nbsp;"""</p><p> &nbsp;```</p><h3>5.3 文件头注释（可选）</h3><pre><code >// Copyright 2025 ACME Corp.\n// Licensed under MIT.</code></pre><p>---</p><p>---</p><h2>6 国际化与字符编码</h2><ul><li><strong>源文件 UTF-8 无 BOM</strong> &nbsp;</li><li>用户可见字符串全部英文；如需中文，使用国际化框架（gettext、Qt tr 等） &nbsp;</li><li>禁止硬编码中文日志</li></ul><p>---</p><h2>7 弃用与删除</h2><ul><li>弃用接口标记 &nbsp;</li><li>C/C++：<code>[[deprecated("use new_api()")]]</code> &nbsp;</li><li>Python：<code>warnings.warn("...", DeprecationWarning, stacklevel=2)</code> &nbsp;</li><li>保留 <strong>2 个版本</strong> 后删除</li></ul><p>---</p><h2>附：禁止清单</h2><p>| 禁止项 | 原因 |</p><p>|---|---|</p><p>| 全局 using namespace | 污染命名空间 |</p><p>| <code>#define</code> 宏函数 | 用 <code>inline</code> / <code>constexpr</code> |</p><p>| 裸指针拥有资源（C++） | 用智能指针 |</p><p>| 可变默认参数 <code>def f(a=[])</code> | 陷阱 |</p><p>| 单字母变量（除循环索引） | 可读性差 |</p><p>---</p>		model_test	published	[]	user1	系统管理员	44	0	2	2025-09-30 07:15:39.261199+00	2025-10-11 09:15:18.859185+00	/api/files/images/d6d48a36-d4eb-46de-b5a4-5337138783d5.png	胸肺	t	["user6", "user5", "user3"]	["admin", "reviewer"]	["研发部标注团队", "研发部影像标注团队"]	f	\N	\N	\N
d7405937-3a98-4bb5-b163-291fc3fb61b3	20250928泌尿测试	<p><img src="/api/files/wangeditor/1da96a1f-4cfa-46d9-ae02-edd2338e7db9.png" alt="漏检.png" data-href="/api/files/wangeditor/1da96a1f-4cfa-46d9-ae02-edd2338e7db9.png" style="width: 310.66px;height: 173.90px;"/></p><p><span style="color: rgb(0, 0, 255);"># 代码风格与Git使用规范<br></span></p><p><span style="color: rgb(24, 28, 33);">本项目包含公司统一的代码风格规范和Git使用指南，旨在确保团队协作的一致性和代码质量。<br></span></p><p><span style="color: rgb(0, 0, 255);">## 📋 目录<br></span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">🎆 新员工入职技术引导</span><span style="color: rgb(163, 21, 21);">](#-新员工入职技术引导)</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp;- </span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">1. 代码仓库与版本控制 (Gitea)</span><span style="color: rgb(163, 21, 21);">](#1-代码仓库与版本控制-gitea)</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp;- </span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">2. 核心项目：xxjz_nnUNet</span><span style="color: rgb(163, 21, 21);">](#2-核心项目xxjz_nnunet)</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp;- </span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">3. 工作留痕与日志</span><span style="color: rgb(163, 21, 21);">](#3-工作留痕与日志)</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp;- </span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">4. 沟通与响应 (飞书)</span><span style="color: rgb(163, 21, 21);">](#4-沟通与响应-飞书)</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp;- </span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">5. 服务器使用规范</span><span style="color: rgb(163, 21, 21);">](#5-服务器使用规范)</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp;- </span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">总结与下一步</span><span style="color: rgb(163, 21, 21);">](#总结与下一步)</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">📖 核心文档</span><span style="color: rgb(163, 21, 21);">](#-核心文档)</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">🚀 项目模板使用</span><span style="color: rgb(163, 21, 21);">](#-项目模板使用)</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp;- </span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">C/C++ 项目模板</span><span style="color: rgb(163, 21, 21);">](#cc-项目模板)</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp;- </span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">Python 项目模板</span><span style="color: rgb(163, 21, 21);">](#python-项目模板)</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">📊 项目负责人指南</span><span style="color: rgb(163, 21, 21);">](#-项目负责人指南)</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">📊 规范覆盖范围</span><span style="color: rgb(163, 21, 21);">](#-规范覆盖范围)</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">🛠️ 推荐工具</span><span style="color: rgb(163, 21, 21);">](#️-推荐工具)</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">📞 联系方式</span><span style="color: rgb(163, 21, 21);">](#-联系方式)</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">⚙️ 缩进与格式化策略</span><span style="color: rgb(163, 21, 21);">](#️-缩进与格式化策略重要)<br></span></p><p><span style="color: rgb(0, 0, 255);">---<br></span></p><p><span style="color: rgb(0, 0, 255);">## 🎆 新员工入职技术引导<br></span></p><p><span style="color: rgb(24, 28, 33);">欢迎加入团队！本章节旨在帮助您快速熟悉公司的技术环境、开发流程和规范，请仔细阅读并遵循。<br></span></p><p><span style="color: rgb(0, 0, 255);">### 1. 代码仓库与版本控制 (Gitea)<br></span></p><p><span style="color: rgb(24, 28, 33);">公司的代码托管平台使用 Gitea。<br></span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**Gitea 地址：** http://192.168.140.100:8088/</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**请立即执行：** 使用公司分配的账户登录上述地址。<br></span></p><p><span style="color: rgb(0, 0, 255);">#### 首要任务：阅读核心文档<br></span></p><p><span style="color: rgb(24, 28, 33);">登录后，您的首要任务是仔细阅读 </span><span style="color: rgb(0, 17, 136);">`CodeDoc`</span><span style="color: rgb(24, 28, 33);"> 项目中的文档，这是所有开发工作的基础规范。<br></span></p><p><span style="color: rgb(0, 0, 255);">1. </span><span style="color: rgb(24, 28, 33);">找到名为 </span><span style="color: rgb(0, 17, 136);">`CodeDoc`</span><span style="color: rgb(24, 28, 33);"> 的仓库。</span></p><p><span style="color: rgb(0, 0, 255);">2. </span><span style="color: rgb(24, 28, 33);">仔细阅读其中的：</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">**《编码风格规范》**：了解公司要求的代码书写、命名、注释等格式。</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">**《Git使用文档》**：掌握公司规定的 Git 工作流、分支管理策略和提交规范。<br></span></p><p><span style="color: rgb(24, 28, 33);">**`请务必在开始任何代码工作前完成阅读，并严格遵循其中的规定。`**<br></span></p><p><span style="color: rgb(0, 0, 255);">### 2. 核心项目：xxjz_nnUNet<br></span></p><p><span style="color: rgb(0, 17, 136);">`xxjz_nnUNet`</span><span style="color: rgb(24, 28, 33);"> 是公司当前暂行模型训练和测试的核心项目。<br></span></p><p><span style="color: rgb(0, 0, 255);">#### 关键操作指南<br></span></p><p><span style="color: rgb(0, 0, 255);">1. </span><span style="color: rgb(24, 28, 33);">**分支规定：**</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">**所有开发、变更、操作都必须在 `develop` 分支上进行。**</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">**严禁** 直接向 </span><span style="color: rgb(0, 17, 136);">`main`</span><span style="color: rgb(24, 28, 33);"> 或 </span><span style="color: rgb(0, 17, 136);">`master`</span><span style="color: rgb(24, 28, 33);"> 分支提交代码。<br></span></p><p><span style="color: rgb(0, 0, 255);">2. </span><span style="color: rgb(24, 28, 33);">**访问账户（暂行策略）：**</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">该项目**暂时**通过公共账户 </span><span style="color: rgb(0, 17, 136);">`xxjz_code_public`</span><span style="color: rgb(24, 28, 33);"> 进行推送等操作。</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">**账户：** </span><span style="color: rgb(0, 17, 136);">`xxjz_code_public`</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">**密码：** </span><span style="color: rgb(0, 17, 136);">`xxjz8888`</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">**请注意：** 此访问方式为**暂行策略**，后续将会更改（如改为个人账户+SSH密钥等方式）。请关注团队通知，届时需按新规操作。<br></span></p><p><span style="color: rgb(0, 0, 255);">3. </span><span style="color: rgb(24, 28, 33);">**提交信息规范 (Commit Message)：**</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">该项目有严格的提交信息格式限制。</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">**请务必仔细阅读项目根目录下的 `README.md` 文件**，其中详细规定了提交信息的格式（例如，必须包含任务类型、模块名、摘要等）。</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">不符合规范的提交可能会被拒绝。<br></span></p><p><span style="color: rgb(0, 0, 255);">#### 操作示例<br></span></p><p><span style="color: rgb(163, 21, 21);">```bash</span></p><p><span style="color: rgb(24, 28, 33);"># 1. 克隆项目</span></p><p><span style="color: rgb(24, 28, 33);">git clone http://192.168.140.100:8088/xxjz/xxjz_nnUNet.git<br></span></p><p><span style="color: rgb(24, 28, 33);"># 2. 进入目录并切换到 develop 分支</span></p><p><span style="color: rgb(24, 28, 33);">cd xxjz_nnUNet</span></p><p><span style="color: rgb(24, 28, 33);">git checkout develop<br></span></p><p><span style="color: rgb(24, 28, 33);"># 3. 【进行你的开发工作...】<br></span></p><p><span style="color: rgb(24, 28, 33);"># 4. 添加更改和提交 (请严格按照README中的格式书写提交信息)</span></p><p><span style="color: rgb(24, 28, 33);">git add .</span></p><p><span style="color: rgb(24, 28, 33);">git commit -m "feat(model): 添加了新的数据预处理逻辑"<br></span></p><p><span style="color: rgb(24, 28, 33);"># 5. 推送至远程 develop 分支 (使用提供的账户密码,main分支已开启分支保护)</span></p><p><span style="color: rgb(24, 28, 33);">git push origin develop</span></p><p><span style="color: rgb(163, 21, 21);">```<br></span></p><p><span style="color: rgb(0, 0, 255);">### 3. 工作留痕与日志<br></span></p><p><span style="color: rgb(24, 28, 33);">**强烈要求具备工作留痕意识**，这是高效协作、进度汇报和问题追溯的基础。<br></span></p><p><span style="color: rgb(0, 0, 255);">1. </span><span style="color: rgb(24, 28, 33);">**工作日志：**</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">**必须**形成每日工作日志的习惯。</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">**记录内容：** 当日工作计划、完成事项、遇到的问题、解决方案、明日计划等。</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">**工具：** 不限。</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">**目的：** 方便个人复盘、每周例行汇报时快速生成周报，并让团队Leader清晰了解你的进度和瓶颈。<br></span></p><p><span style="color: rgb(0, 0, 255);">2. </span><span style="color: rgb(24, 28, 33);">**代码留痕：**</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">清晰且有意义的 **Git提交信息** 是代码层面最重要的工作留痕。</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">代码中的复杂逻辑必须添加**注释**，说明为什么这么做（Why），而不仅仅是做了什么（What）。<br></span></p><p><span style="color: rgb(0, 0, 255);">### 4. 沟通与响应 (飞书)<br></span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">公司使用 **飞书 (Lark)** 作为主要内部沟通工具。</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**重要：** 当您在飞书上收到消息或通知时，请养成**及时阅读并回复**的习惯（即使仅回复"收到"），以确保信息畅通和团队协作效率。<br></span></p><p><span style="color: rgb(0, 0, 255);">### 5. 服务器使用规范<br></span></p><p><span style="color: rgb(24, 28, 33);">公司配备的训练服务器为 **国产海光八卡服务器**。<br></span></p><p><span style="color: rgb(0, 0, 255);">#### 使用须知<br></span></p><p><span style="color: rgb(0, 0, 255);">1. </span><span style="color: rgb(24, 28, 33);">**权限申请：**</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">**若有使用需求，必须首先联系 `zmh`**，申请账号和权限。未经允许不得擅自连接或使用。<br></span></p><p><span style="color: rgb(0, 0, 255);">2. </span><span style="color: rgb(24, 28, 33);">**环境限制：**</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">服务器上的深度学习环境是固定的，**严禁私自更新、安装或更改** </span><span style="color: rgb(0, 17, 136);">`torch`</span><span style="color: rgb(24, 28, 33);"> (PyTorch) 及其配套版本（如 </span><span style="color: rgb(0, 17, 136);">`torchvision`</span><span style="color: rgb(24, 28, 33);">, </span><span style="color: rgb(0, 17, 136);">`torchaudio`</span><span style="color: rgb(24, 28, 33);">）。</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">**`numpy` 版本最高仅支持到 `1.26.x`**。在服务器上或为服务器环境开发时，请确保代码兼容此版本，避免使用更高版本的特性。</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp; - </span><span style="color: rgb(24, 28, 33);">如有强烈的环境变更需求，需向 </span><span style="color: rgb(0, 17, 136);">`zmh`</span><span style="color: rgb(24, 28, 33);"> 提出申请并说明理由。<br></span></p><p><span style="color: rgb(0, 0, 255);">#### 建议<br></span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">在本地开发时，建议使用 </span><span style="color: rgb(0, 17, 136);">`conda`</span><span style="color: rgb(24, 28, 33);"> 或 </span><span style="color: rgb(0, 17, 136);">`venv`</span><span style="color: rgb(24, 28, 33);"> 创建虚拟环境，并配置与服务器兼容的库版本，以避免环境不一致导致的问题。<br></span></p><p><span style="color: rgb(0, 0, 255);">### 总结与下一步<br></span></p><p><span style="color: rgb(0, 0, 255);">1. </span><span style="color: rgb(24, 28, 33);">**登录** Gitea </span><span style="color: rgb(0, 17, 136);">`http://192.168.140.100:8088/`</span><span style="color: rgb(24, 28, 33);">。</span></p><p><span style="color: rgb(0, 0, 255);">2. </span><span style="color: rgb(24, 28, 33);">**阅读** </span><span style="color: rgb(0, 17, 136);">`CodeDoc`</span><span style="color: rgb(24, 28, 33);"> 项目中的编码规范和Git文档。</span></p><p><span style="color: rgb(0, 0, 255);">3. </span><span style="color: rgb(24, 28, 33);">**克隆** </span><span style="color: rgb(0, 17, 136);">`xxjz_nnUNet`</span><span style="color: rgb(24, 28, 33);"> 项目，**切换**到 </span><span style="color: rgb(0, 17, 136);">`develop`</span><span style="color: rgb(24, 28, 33);"> 分支，**阅读**其 </span><span style="color: rgb(0, 17, 136);">`README.md`</span><span style="color: rgb(24, 28, 33);"> 中的提交规范。注意账户策略为**暂行**。</span></p><p><span style="color: rgb(0, 0, 255);">4. </span><span style="color: rgb(24, 28, 33);">**建立**工作日志习惯，**强化**工作留痕意识。</span></p><p><span style="color: rgb(0, 0, 255);">5. </span><span style="color: rgb(24, 28, 33);">在飞书上**活跃起来**，及时回复消息。</span></p><p><span style="color: rgb(0, 0, 255);">6. </span><span style="color: rgb(24, 28, 33);">需要跑实验时，**联系 `zmh`** 申请服务器权限，并注意**环境版本限制**。<br></span></p><p><span style="color: rgb(24, 28, 33);">祝您工作顺利！如有任何疑问，请及时在团队中沟通。<br></span></p><p><span style="color: rgb(0, 0, 255);">---<br></span></p><p><span style="color: rgb(0, 0, 255);">## 📖 核心文档<br></span></p><p><span style="color: rgb(0, 0, 255);">### [编码风格.md](./编码风格.md) - C/C++和Python代码规范</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**基础规范**：命名约定、代码格式、注释规范</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**高级指导**：错误处理、性能优化、代码审查检查清单</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**工具配置**：开发环境和代码检查工具设置</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**在线查看**：</span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">C/C++风格规范</span><span style="color: rgb(163, 21, 21);">](http://192.168.140.100:8088/xxjz/cpp_template)<br></span></p><p><span style="color: rgb(0, 0, 255);">### [git使用文档.md](./git使用文档.md) - Git工作流和最佳实践</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**基础操作**：Gitea平台使用、分支管理策略</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**团队协作**：提交规范、冲突解决、代码审查</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**高级功能**：CI/CD集成、Git Hooks、安全管理<br></span></p><p><span style="color: rgb(0, 0, 255);">---<br></span></p><p><span style="color: rgb(0, 0, 255);">## 🚀 项目模板使用<br></span></p><p><span style="color: rgb(0, 0, 255);">### C/C++ 项目模板</span></p><p><span style="color: rgb(24, 28, 33);">位于 </span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">cpp_template</span><span style="color: rgb(163, 21, 21);">](./cpp_template/)</span><span style="color: rgb(24, 28, 33);"> 目录，包含：</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**CMake 构建系统**：C++17标准，支持测试</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**clang-format 配置**：符合公司编码规范</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**pre-commit 钩子**：自动代码格式化</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**项目结构**：src/、tests/、include/ 标准布局<br></span></p><p><span style="color: rgb(24, 28, 33);">**快速开始**：</span></p><p><span style="color: rgb(163, 21, 21);">```bash</span></p><p><span style="color: rgb(24, 28, 33);"># 复制模板</span></p><p><span style="color: rgb(24, 28, 33);">cp -r cpp_template my_cpp_project</span></p><p><span style="color: rgb(24, 28, 33);">cd my_cpp_project<br></span></p><p><span style="color: rgb(24, 28, 33);"># 安装钩子</span></p><p><span style="color: rgb(24, 28, 33);">pip install pre-commit</span></p><p><span style="color: rgb(24, 28, 33);">pre-commit install<br></span></p><p><span style="color: rgb(24, 28, 33);"># 构建和测试</span></p><p><span style="color: rgb(24, 28, 33);">cmake -S . -B build -DCMAKE_BUILD_TYPE=Release</span></p><p><span style="color: rgb(24, 28, 33);">cmake --build build -j</span></p><p><span style="color: rgb(24, 28, 33);">ctest --test-dir build</span></p><p><span style="color: rgb(163, 21, 21);">```<br></span></p><p><span style="color: rgb(0, 0, 255);">### Python 项目模板</span></p><p><span style="color: rgb(24, 28, 33);">位于 </span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">python_style</span><span style="color: rgb(163, 21, 21);">](./python_style/)</span><span style="color: rgb(24, 28, 33);"> 目录，包含：</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**pyproject.toml**：现代Python项目配置</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**black + isort + ruff**：代码格式化和检查</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**pre-commit 配置**：自动质量检查</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**src 布局**：标准的Python包结构</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**在线查看**：</span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">Python风格规范</span><span style="color: rgb(163, 21, 21);">](http://192.168.140.100:8088/xxjz/python_style)<br></span></p><p><span style="color: rgb(24, 28, 33);">**快速开始**：</span></p><p><span style="color: rgb(163, 21, 21);">```bash</span></p><p><span style="color: rgb(24, 28, 33);"># 复制模板</span></p><p><span style="color: rgb(24, 28, 33);">cp -r python_style my_python_project</span></p><p><span style="color: rgb(24, 28, 33);">cd my_python_project<br></span></p><p><span style="color: rgb(24, 28, 33);"># 重命名包名</span></p><p><span style="color: rgb(24, 28, 33);">mv src/your_project_name src/my_python_project<br></span></p><p><span style="color: rgb(24, 28, 33);"># 安装工具和钩子</span></p><p><span style="color: rgb(24, 28, 33);">pip install -U pip pre-commit black isort ruff</span></p><p><span style="color: rgb(24, 28, 33);">pre-commit install<br></span></p><p><span style="color: rgb(24, 28, 33);"># 运行检查和测试</span></p><p><span style="color: rgb(24, 28, 33);">pre-commit run --all-files</span></p><p><span style="color: rgb(24, 28, 33);">pytest</span></p><p><span style="color: rgb(163, 21, 21);">```<br></span></p><p><span style="color: rgb(0, 0, 255);">---<br></span></p><p><span style="color: rgb(0, 0, 255);">## 📊 项目负责人指南<br></span></p><p><span style="color: rgb(0, 0, 255);">### 日常管理</span></p><p><span style="color: rgb(0, 0, 255);">1. </span><span style="color: rgb(24, 28, 33);">**确保团队遵循规范**：定期检查代码质量和风格一致性</span></p><p><span style="color: rgb(0, 0, 255);">2. </span><span style="color: rgb(24, 28, 33);">**配置项目工具**：在新项目中集成代码检查工具</span></p><p><span style="color: rgb(0, 0, 255);">3. </span><span style="color: rgb(24, 28, 33);">**代码审查流程**：建立并执行PR审查标准</span></p><p><span style="color: rgb(0, 0, 255);">4. </span><span style="color: rgb(24, 28, 33);">**规范培训**：定期组织团队培训和规范更新<br></span></p><p><span style="color: rgb(0, 0, 255);">### 新人入职支持</span></p><p><span style="color: rgb(0, 0, 255);">1. </span><span style="color: rgb(24, 28, 33);">**分配账号权限**：协助新员工获取必要的系统访问权</span></p><p><span style="color: rgb(0, 0, 255);">2. </span><span style="color: rgb(24, 28, 33);">**指导学习**：确保新人完成入职检查清单</span></p><p><span style="color: rgb(0, 0, 255);">3. </span><span style="color: rgb(24, 28, 33);">**答疑解惑**：及时回应新人在规范和工具使用上的问题</span></p><p><span style="color: rgb(0, 0, 255);">4. </span><span style="color: rgb(24, 28, 33);">**进度跟踪**：定期检查新人的适应情况和工作质量<br></span></p><p><span style="color: rgb(0, 0, 255);">## 📊 规范覆盖范围<br></span></p><p><span style="color: rgb(0, 0, 255);">| 语言/工具 | 覆盖程度 | 说明 |</span></p><p><span style="color: rgb(0, 0, 255);">|-----------|----------|------|</span></p><p><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> **C/C++** </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> ✅ 完整 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> 命名、格式、性能、安全 </span><span style="color: rgb(0, 0, 255);">|</span></p><p><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> **Python** </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> ✅ 完整 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> PEP8兼容，团队定制 </span><span style="color: rgb(0, 0, 255);">|</span></p><p><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> **Git** </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> ✅ 完整 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> Git</span><span style="color: rgb(0, 0, 255);">-</span><span style="color: rgb(24, 28, 33);">Flow + Gitea集成 </span><span style="color: rgb(0, 0, 255);">|</span></p><p><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> **代码审查** </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> ✅ 完整 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> 检查清单和流程 </span><span style="color: rgb(0, 0, 255);">|</span></p><p><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> **工具配置** </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> ✅ 完整 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> IDE、格式化、静态分析 </span><span style="color: rgb(0, 0, 255);">|<br></span></p><p><span style="color: rgb(0, 0, 255);">## 🛠️ 推荐工具<br></span></p><p><span style="color: rgb(0, 0, 255);">### 代码格式化</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**C/C++**: clang-format（项目已包含 </span><span style="color: rgb(163, 21, 21);">[</span><span style="color: rgb(24, 28, 33);">.clang-format</span><span style="color: rgb(163, 21, 21);">](./.clang-format)</span><span style="color: rgb(24, 28, 33);"> 配置文件）</span></p><p><span style="color: rgb(163, 21, 21);"> &nbsp;```bash</span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;# 格式化单个文件</span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;clang-format -i filename.cpp<br></span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;# 格式化所有C/C++文件</span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;clang-format -i *.cpp *.h<br></span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;# 检查格式（不修改文件）</span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;clang-format --dry-run --Werror *.cpp *.h</span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;</span><span style="color: rgb(163, 21, 21);">```</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**Python**: black + isort</span></p><p><span style="color: rgb(163, 21, 21);"> &nbsp;```bash</span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;# 安装工具</span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;pip install black isort<br></span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;# 格式化Python文件</span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;black .</span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;isort .</span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;</span><span style="color: rgb(163, 21, 21);">```</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**通用**: EditorConfig（在项目根目录创建 </span><span style="color: rgb(0, 17, 136);">`.editorconfig`</span><span style="color: rgb(24, 28, 33);"> 文件）<br></span></p><p><span style="color: rgb(0, 0, 255);">### 静态分析</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**C/C++**: cppcheck, clang-static-analyzer</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**Python**: pylint, mypy</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**通用**: SonarQube<br></span></p><p><span style="color: rgb(0, 0, 255);">### Git工具</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**GUI**: SourceTree, GitKraken</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**命令行**: Git官方客户端</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**IDE集成**: VS Code, CLion, PyCharm<br></span></p><p><span style="color: rgb(0, 0, 255);">## 📞 联系方式<br></span></p><p><span style="color: rgb(0, 0, 255);">### 技术支持</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**代码规范问题**：联系开发团队负责人</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**Git使用问题**：参考文档或咨询技术主管</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**工具配置问题**：查看推荐工具章节或寻求技术支持<br></span></p><p><span style="color: rgb(0, 0, 255);">### 权限申请</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**Gitea账号**：联系 **zmh** 获取访问权限</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**服务器权限**：联系 **zmh** 申请训练服务器账号<br></span></p><p><span style="color: rgb(0, 0, 255);">### 紧急联系</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**飞书群组**：加入团队技术交流群</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">**工作时间**：周一至周五 9:00-18:00<br></span></p><p><span style="color: rgb(0, 0, 255);">---<br></span></p><p><span style="color: rgb(0, 0, 255);">## 📅 更新记录<br></span></p><p><span style="color: rgb(0, 0, 255);">| 版本 | 日期 | 更新内容 | 更新人 |</span></p><p><span style="color: rgb(0, 0, 255);">|------|------|----------|--------|</span></p><p><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> v2.1 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> 2024</span><span style="color: rgb(0, 0, 255);">-</span><span style="color: rgb(24, 28, 33);">01 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> 整合入职引导，优化文档结构 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> 系统更新 </span><span style="color: rgb(0, 0, 255);">|</span></p><p><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> v2.0 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> 2024</span><span style="color: rgb(0, 0, 255);">-</span><span style="color: rgb(24, 28, 33);">01 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> 新增项目模板和工具配置说明 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> 系统更新 </span><span style="color: rgb(0, 0, 255);">|</span></p><p><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> v1.2 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> 2024</span><span style="color: rgb(0, 0, 255);">-</span><span style="color: rgb(24, 28, 33);">01 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> 增强Git文档，添加CI/CD和安全章节 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> 系统更新 </span><span style="color: rgb(0, 0, 255);">|</span></p><p><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> v1.1 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> 2024</span><span style="color: rgb(0, 0, 255);">-</span><span style="color: rgb(24, 28, 33);">01 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> 完善编码风格，新增性能优化指导 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> 系统更新 </span><span style="color: rgb(0, 0, 255);">|</span></p><p><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> v1.0 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> 2024</span><span style="color: rgb(0, 0, 255);">-</span><span style="color: rgb(24, 28, 33);">01 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> 初始版本，基础编码风格和Git规范 </span><span style="color: rgb(0, 0, 255);">|</span><span style="color: rgb(24, 28, 33);"> 系统创建 </span><span style="color: rgb(0, 0, 255);">|<br></span></p><p><span style="color: rgb(0, 0, 255);">---<br></span></p><p><span style="color: rgb(24, 28, 33);">*本文档持续更新中，如有建议或问题，请及时反馈给团队负责人。*<br></span></p><p><span style="color: rgb(0, 0, 255);">---<br></span></p><p><span style="color: rgb(0, 128, 0);">&gt;</span><span style="color: rgb(24, 28, 33);"> 💡 **提示**：本规范旨在提高代码质量和团队协作效率，如有疑问或建议，欢迎通过合并请求或邮件反馈。<br></span></p><p><span style="color: rgb(24, 28, 33);">此仓库主要保存星像的编码风格，使用文档等说明文档<br></span></p><p><span style="color: rgb(0, 0, 255);">## ⚙️ 缩进与格式化策略（重要）</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">C/C++：使用 Tab 进行缩进（宽度 4 列），仅用于缩进；行尾对齐使用空格。</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">Python：严格使用 4 空格缩进（遵循 PEP8），禁止 Tab。</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">严禁在同一文件中混用空格与 Tab 进行缩进。</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">已提供 </span><span style="color: rgb(0, 17, 136);">`.clang-format`</span><span style="color: rgb(24, 28, 33);"> 与将新增的 </span><span style="color: rgb(0, 17, 136);">`.editorconfig`</span><span style="color: rgb(24, 28, 33);"> 以统一各编辑器行为。<br></span></p><p><span style="color: rgb(0, 0, 255);">## 🧰 额外工程配置</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(0, 17, 136);">`.editorconfig`</span><span style="color: rgb(24, 28, 33);">：统一缩进、行宽、编码、换行符（将新增）。</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(0, 17, 136);">`.gitattributes`</span><span style="color: rgb(24, 28, 33);">：标准化行结尾（LF），防止 CRLF 漂移（将新增）。</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">保护分支与 PR 流程：请遵循 </span><span style="color: rgb(0, 17, 136);">`git使用文档.md`</span><span style="color: rgb(24, 28, 33);"> 中的受保护分支与合并请求规范。<br></span></p><p><span style="color: rgb(0, 0, 255);">### 如何启用这些配置</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">EditorConfig（.editorconfig）</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp;- </span><span style="color: rgb(24, 28, 33);">VS Code: 安装 EditorConfig 插件并启用；建议设置 </span><span style="color: rgb(0, 17, 136);">`"editor.detectIndentation": false`</span><span style="color: rgb(24, 28, 33);">。</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp;- </span><span style="color: rgb(24, 28, 33);">JetBrains: 默认支持，确保 Settings → Editor → Code Style → Enable EditorConfig 已开启。</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp;- </span><span style="color: rgb(24, 28, 33);">Visual Studio: 2022+ 原生支持。</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">Git 属性（.gitattributes）</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp;- </span><span style="color: rgb(24, 28, 33);">首次引入或更新后，执行一次标准化：</span></p><p><span style="color: rgb(163, 21, 21);"> &nbsp; &nbsp;```bash</span></p><p><span style="color: rgb(163, 21, 21);"> &nbsp; &nbsp;git add --renormalize .</span></p><p><span style="color: rgb(163, 21, 21);"> &nbsp; &nbsp;git commit -m "chore: normalize line endings via .gitattributes"</span></p><p><span style="color: rgb(163, 21, 21);"> &nbsp; &nbsp;```</span></p><p><span style="color: rgb(0, 0, 255);"> &nbsp;- </span><span style="color: rgb(24, 28, 33);">Windows 环境建议：</span></p><p><span style="color: rgb(163, 21, 21);"> &nbsp; &nbsp;```bash</span></p><p><span style="color: rgb(163, 21, 21);"> &nbsp; &nbsp;git config --global core.autocrlf false</span></p><p><span style="color: rgb(163, 21, 21);"> &nbsp; &nbsp;git config --global core.eol lf</span></p><p><span style="color: rgb(163, 21, 21);"> &nbsp; &nbsp;```<br></span></p><p><span style="color: rgb(0, 0, 255);">### Python 代码风格执行（pyproject + pre-commit）</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">本仓库已提供 </span><span style="color: rgb(0, 17, 136);">`pyproject.toml`</span><span style="color: rgb(24, 28, 33);">（Black/Isort/Ruff/NBQA）与 </span><span style="color: rgb(0, 17, 136);">`.pre-commit-config.yaml`</span><span style="color: rgb(24, 28, 33);">。</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">本地启用（一次性）：</span></p><p><span style="color: rgb(163, 21, 21);"> &nbsp;```bash</span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;pip install pre-commit</span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;pre-commit install</span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;</span><span style="color: rgb(163, 21, 21);">```</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">手动对全仓库执行一次：</span></p><p><span style="color: rgb(163, 21, 21);"> &nbsp;```bash</span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;pre-commit run --all-files</span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;</span><span style="color: rgb(163, 21, 21);">```</span></p><p><span style="color: rgb(0, 0, 255);">- </span><span style="color: rgb(24, 28, 33);">CI 检查（非破坏性）：</span></p><p><span style="color: rgb(163, 21, 21);"> &nbsp;```bash</span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;black --check .</span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;isort --check-only .</span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;ruff check .</span></p><p><span style="color: rgb(24, 28, 33);"> &nbsp;</span><span style="color: rgb(163, 21, 21);">```<br></span></p>		model_test	published	[]	user1	系统管理员	35	1	2	2025-09-28 07:18:21.049328+00	2025-10-11 07:51:58.779454+00	http://192.168.200.20:9000/medical-annotations/images/8a472975-a2cf-4eef-b0d8-b6892a9f8991.png	泌尿	t	[]	[]	[]	f	\N	\N	\N
a37cc2ea-72d4-4e48-a41f-21afe9e57014	模型测试	<p>ffff<img src="http://localhost:9000/medical-annotations/wangeditor/bba0d2bb-4c7f-45c7-b1e4-82217b8c34de.png" alt="image.png" data-href="http://localhost:9000/medical-annotations/wangeditor/bba0d2bb-4c7f-45c7-b1e4-82217b8c34de.png" style="width: 87.01px;height: 61.81px;"/></p>	fff	model_test	published	[]	user1	系统管理员	25	0	1	2025-09-11 06:15:01.129046+00	2025-10-11 07:52:01.043486+00	\N	\N	t	[]	[]	[]	f	\N	\N	\N
14330820-e822-4ace-8c11-0f7910c6cedc	模型测试20250911	<p>封面上传错误，有误<img src="http://localhost:9000/medical-annotations/wangeditor/8c132576-2139-478f-99d6-d7c9fae9b7a4.png" alt="image.png" data-href="http://localhost:9000/medical-annotations/wangeditor/8c132576-2139-478f-99d6-d7c9fae9b7a4.png" style=""/></p>		model_test	published	[]	user1	系统管理员	21	0	1	2025-09-11 06:36:07.750551+00	2025-10-11 07:52:02.810441+00		资源	t	[]	[]	[]	f	\N	\N	\N
9047a0ef-3d9a-4174-87b4-1bcb83662b16	# nnUNet 模型综合测试报告	<h2>1. 概述</h2><p>本报告基于nnUNet模型在泌尿系统数据集上的验证集和测试集性能评估结果，提供了全面的模型性能分析。测试涵盖了11个关键器官的分割任务，采用5折交叉验证方法确保结果的可靠性。</p><h3>1.1 测试环境</h3><ul><li><strong>生成时间</strong>: 2025-09-19</li><li><strong>测试数据集</strong>: 泌尿系统数据集（UrinaryDatasets_20）</li><li><strong>验证方法</strong>: 5折交叉验证</li><li><strong>评估指标</strong>: Dice系数、IoU、TP/FP/FN/TN</li></ul><h3>1.2 数据集概况</h3><ul><li><strong>验证集器官数量</strong>: 11个</li><li><strong>测试集器官数量</strong>: 11个</li><li><strong>总测试样本数</strong>: 203个</li><li><strong>数据匹配率</strong>: 100%</li></ul><h2>2. 器官分割性能对比</h2><h3>2.1 验证集 vs 测试集性能概览</h3><p>| 器官 | 验证集Dice | 测试集Dice | 验证集IoU | 测试集IoU | 性能差异 |</p><p>|------|------------|------------|-----------|-----------|----------|</p><p>| 肾脏 (Kidney) | 90.50% | 90.57% | - | 83.39% | +0.07% |</p><p>| 膀胱 (Bladder) | 89.20% | 88.45% | - | 79.37% | -0.75% |</p><p>| 肾动脉 (RenalArtery) | 25.68% | 25.20% | - | 14.52% | -0.48% |</p><p>| 肾静脉 (RenalVein) | 42.30% | 41.85% | - | 26.52% | -0.45% |</p><p>| 淋巴结 (LymphNode) | 25.68% | 24.20% | - | 13.85% | -1.48% |</p><p>| 肾囊肿 (RenalCyst) | 78.90% | 78.12% | - | 64.08% | -0.78% |</p><p>| 输尿管 (Ureter) | 35.40% | 34.88% | - | 21.15% | -0.52% |</p><p>| 肾占位 (RenalOccupation) | 65.20% | 64.75% | - | 47.85% | -0.45% |</p><p>| 肾上腺 (Adrenal) | 72.10% | 71.68% | - | 55.82% | -0.42% |</p><p>| 积液 (Collection) | 58.30% | 57.92% | - | 40.75% | -0.38% |</p><p>| 腰大肌 (PsoasMajor) | 94.50% | 94.17% | - | 89.08% | -0.33% |</p><h3>2.2 性能等级分类</h3><h4>优秀性能 (Dice &gt; 85%)</h4><ul><li><strong>肾脏 (Kidney)</strong>: 验证集90.50% → 测试集90.57% ✓</li><li><strong>膀胱 (Bladder)</strong>: 验证集89.20% → 测试集88.45% ↓</li><li><strong>腰大肌 (PsoasMajor)</strong>: 验证集94.50% → 测试集94.17% ↓</li></ul><h4>良好性能 (Dice 65%-85%)</h4><ul><li><strong>肾囊肿 (RenalCyst)</strong>: 验证集78.90% → 测试集78.12% ↓</li><li><strong>肾上腺 (Adrenal)</strong>: 验证集72.10% → 测试集71.68% ↓</li><li><strong>肾占位 (RenalOccupation)</strong>: 验证集65.20% → 测试集64.75% ↓</li></ul><h4>中等性能 (Dice 40%-65%)</h4><ul><li><strong>积液 (Collection)</strong>: 验证集58.30% → 测试集57.92% ↓</li><li><strong>肾静脉 (RenalVein)</strong>: 验证集42.30% → 测试集41.85% ↓</li></ul><h4>待改进性能 (Dice &lt; 40%)</h4><ul><li><strong>输尿管 (Ureter)</strong>: 验证集35.40% → 测试集34.88% ↓</li><li><strong>肾动脉 (RenalArtery)</strong>: 验证集25.68% → 测试集25.20% ↓</li><li><strong>淋巴结 (LymphNode)</strong>: 验证集25.68% → 测试集24.20% ↓</li></ul><h2>3. 详细性能分析</h2><h3>3.1 测试集统计指标</h3><h4>高性能器官详细分析</h4><p><strong>肾脏 (Kidney)</strong></p><ul><li>平均Dice: 90.57%</li><li>平均IoU: 83.39%</li><li>标准差: 0.46%</li><li>性能稳定性: 优秀</li></ul><p><strong>腰大肌 (PsoasMajor)</strong></p><ul><li>平均Dice: 94.17%</li><li>平均IoU: 89.08%</li><li>标准差: 0.04%</li><li>性能稳定性: 极佳</li></ul><p><strong>膀胱 (Bladder)</strong></p><ul><li>平均Dice: 88.45%</li><li>平均IoU: 79.37%</li><li>标准差: 0.52%</li><li>性能稳定性: 良好</li></ul><h4>挑战性器官分析</h4><p><strong>淋巴结 (LymphNode)</strong></p><ul><li>平均Dice: 24.20%</li><li>平均IoU: 13.85%</li><li>主要挑战: 小目标检测、形状不规则</li></ul><p><strong>肾动脉 (RenalArtery)</strong></p><ul><li>平均Dice: 25.20%</li><li>平均IoU: 14.52%</li><li>主要挑战: 细小血管结构、对比度低</li></ul><p><strong>输尿管 (Ureter)</strong></p><ul><li>平均Dice: 34.88%</li><li>平均IoU: 21.15%</li><li>主要挑战: 管状结构、连续性分割</li></ul><h3>3.2 模型泛化能力评估</h3><h4>泛化性能指标</h4><ul><li><strong>平均性能下降</strong>: 0.54%</li><li><strong>最大性能下降</strong>: 1.48% (淋巴结)</li><li><strong>性能提升器官</strong>: 1个 (肾脏)</li><li><strong>性能稳定器官</strong>: 10个</li></ul><h4>泛化能力评级</h4><ul><li><strong>优秀泛化</strong> (性能差异 &lt; 0.5%): 6个器官</li><li><strong>良好泛化</strong> (性能差异 0.5%-1.0%): 4个器官 &nbsp;</li><li><strong>一般泛化</strong> (性能差异 &gt; 1.0%): 1个器官</li></ul><h2>4. 技术指标统计</h2><h3>4.1 整体性能统计</h3><ul><li><strong>验证集平均Dice</strong>: 61.52%</li><li><strong>测试集平均Dice</strong>: 60.98%</li><li><strong>整体性能下降</strong>: 0.54%</li><li><strong>测试集平均IoU</strong>: 46.85%</li></ul><h3>4.2 性能分布</h3><ul><li><strong>Dice &gt; 80%</strong>: 3个器官 (27.3%)</li><li><strong>Dice 60%-80%</strong>: 3个器官 (27.3%)</li><li><strong>Dice 40%-60%</strong>: 2个器官 (18.2%)</li><li><strong>Dice &lt; 40%</strong>: 3个器官 (27.3%)</li></ul><h3>4.3 稳定性分析</h3><p>基于5折交叉验证结果，各器官性能标准差均小于1%，表明模型训练稳定，结果可靠。</p><h2>5. 结论与建议</h2><h3>5.1 主要发现</h3><p>1. <strong>模型整体性能优秀</strong>: 大器官（肾脏、膀胱、腰大肌）分割精度超过88%</p><p>2. <strong>泛化能力良好</strong>: 验证集到测试集平均性能下降仅0.54%</p><p>3. <strong>小目标挑战</strong>: 淋巴结、血管等小结构分割仍需改进</p><p>4. <strong>性能稳定</strong>: 5折交叉验证结果一致性高</p><h3>5.2 优化建议</h3><p>1. <strong>针对小目标优化</strong>: </p><ul><li>增加小目标样本数量</li><li>采用多尺度训练策略</li><li>优化损失函数权重</li></ul><p>2. <strong>血管结构改进</strong>:</p><ul><li>引入血管增强预处理</li><li>采用专门的血管分割网络</li><li>增加血管标注精度</li></ul><p>3. <strong>数据增强策略</strong>:</p><ul><li>增加形变增强</li><li>优化对比度增强</li><li>引入混合增强技术</li></ul><h3>5.3 模型部署建议</h3><p>基于当前性能表现，建议：</p><ul><li><strong>肾脏、膀胱、腰大肌</strong>: 可直接用于临床辅助诊断</li><li><strong>肾囊肿、肾上腺、肾占位</strong>: 适合作为初筛工具</li><li><strong>血管、淋巴结</strong>: 需要专家复核确认</li></ul><p>---</p><p><strong>报告生成时间</strong>: 2025-01-27 &nbsp;</p><p><strong>数据来源</strong>: nnUNet验证集和测试集评估结果 &nbsp;</p><p><strong>评估标准</strong>: Dice系数、IoU、混淆矩阵指标</p>		model_test	published	[]	user1	系统管理员	4	0	1	2025-10-15 07:08:45.44927+00	2025-10-15 07:29:42.705155+00		泌尿	t	[]	["admin"]	["研发部"]	f	\N	\N	proj2025403
affd3e17-bb2d-477a-bddd-2344d7306adf	# 述职报告PPT大纲	<h2>P1 述职报告</h2><p>封面页：包含报告标题、述职人姓名、日期</p><h2>P2 目录</h2><p>1. 数据处理插件开发工作</p><p>2. 模型训练工作</p><p>3. 芯片适配工作</p><p>4. 生产软件与GMP认证相关工作</p><p>5. 未来工作计划</p><h2>P3 数据处理插件开发概述</h2><p>本节重点介绍3个核心插件的开发背景与应用价值</p><h2>P4 Slicer插件1：nrrd转nii</h2><p>开发目的：解决医学影像格式转换需求</p><p>核心功能：支持批量NRRD文件转NIfTI格式，保留元数据</p><h2>P5 Slicer插件1：技术实现</h2><p>实现原理：基于ITK库的IO模块，采用多线程处理架构</p><p>使用示例：展示3步操作流程与转换前后对比图</p><h2>P6 Slicer插件2：nrrd转stl+体积计算</h2><p>开发目的：满足3D打印与量化分析需求</p><p>核心功能：格式转换+自动计算并导出体积信息（mm³）</p><h2>P7 Slicer插件2：技术实现</h2><p>实现原理：结合VTK表面重建与Marching Cubes算法</p><p>使用示例：展示肿瘤模型转换效果与体积数据报表</p><h2>P8 独立软件：dicom转nii</h2><p>开发目的：提供独立运行的DICOM序列转换工具</p><p>功能特点：支持DICOMDIR解析、多序列合并、压缩选项</p><h2>P9 模型训练工作概述</h2><p>研究框架：基于UNet++架构的医学影像分割方案</p><p>关键环节：参数调优（学习率0.001）、数据增强（弹性形变）</p><h2>P10 胸肺模型训练</h2><p>训练标签（5类）：</p><ul><li>气管</li><li>左右肺叶</li><li>肺结节</li><li>胸主动脉</li></ul><p>性能指标：Dice系数0.89±0.03</p><h2>P11 泌尿模型训练</h2><p>训练标签（11类）：</p><ul><li>肾脏（左右）</li><li>输尿管（左右）</li><li>膀胱</li><li>前列腺/子宫</li><li>肿瘤区域（5子类）</li></ul><p>性能指标：平均Dice系数0.85±0.04</p><h2>P12 K100_AI芯片适配</h2><p>芯片概况：K100_AI卡专为高性能推理设计，为海光的第三代DCU，在第二代K100上优化了推理的性能。</p><p>适配挑战：适配的主要工作在于将模型所用的所有运行库和依赖环境替换为使用海光生态下的库和依赖（如DTK，migraphx）。</p><p>适配过程：开始适配-&gt;单卡训练-&gt;多卡训练-&gt;推理-&gt;服务化</p><h2>P13 Z100L适配与部署</h2><p>芯片概况：Z100L卡为海光的第一代DCU</p><p>适配挑战：将海光修复后的最新版本的migraphx和dtk部署到Z100L卡上。</p><p>适配过程：开始适配-&gt;单卡训练-&gt;多卡训练-&gt;推理-&gt;服务化</p><h2>P14 测试结果对比</h2><p>性能测试1</p><p>| 测试项 | 设备 | sw_batch | 推理时间（s） | 显存占用 | DCU(GPU)使用率 |</p><p>| --- | --- | --- | --- | --- | --- |</p><p>| MigraphX推理框架测试 | 海光K100_AI (显存64G) | 1 | 32.184 | 6% | 33% |</p><p>| MigraphX推理框架测试 | 海光K100_AI (显存64G) | 2 | 30.143 | 10% | 33% |</p><p>| MigraphX推理框架测试 | 海光K100_AI (显存64G) | 4 | 29.746 | 14% | 47% |</p><p>| MigraphX推理框架测试 | 海光K100_AI (显存64G) | 6 | 29.225 | 19% | 51% |</p><p>| MigraphX推理框架测试 | 海光K100_AI (显存64G) | 8 | 353.351 | 20% | 30% |</p><p>| Onnxruntime推理框架测试 (ROCMExecutionProvider) | 海光K100_AI (显存64G) | 2 | 67.55 | 21~23% | 11~16% |</p><p>| Onnxruntime推理框架测试 (ROCMExecutionProvider) | 海光Z100 (显存16G) | 2 | 128.44 | 42% | 100% |</p><p>| Onnxruntime推理框架测试 | 英伟达RTX4090D | 2 | 11.12 | 22% | 100% |</p><p>性能测试2</p><p>| 设备 | 数据尺度 | 预处理时间 | 推理时间 | 后处理时间 |</p><p>| --- | --- | --- | --- | --- |</p><p>| 海光CPU | (512,512,312) | 40~44s | 28~30s | 16~18s |</p><p>| Z100 | (512,512,312) | 15~16s | 128.44s | 2~4s |</p><p>| K100_AI | (512,512,312) | 21~23s | - | 8~10s |</p><h2>P14 客户机部署</h2><p>目的：基于之前田博所使用的Docker容器化方案，实现在基于nvidia卡的windos客户机上部署模型的推理服务，</p><p>实现效果：生产人员点击.bat的windows脚本文件半自动化的部署环境</p><h2>P15 生产软件工具开发</h2><p>软件生产工具：自动化构建流水线，支持C++/Python混合编译</p><p>磁盘加密工具：AES-256加密算法，满足GMP数据安全要求</p><h2>P16 软件修复工具</h2><p>开发目的：解决生产环境中软件崩溃的快速恢复问题</p><p>核心功能：自动日志分析、关键文件备份与一键修复</p><h2>P17 未来工作计划</h2><p>1. 服务优化：热加载+预加载双机制实现</p><p>2. 模型扩展：泌尿二期/肝胆模型研发</p><p>3. 工程化：代码规范体系建设（C++/Python）</p><h2>P18 感谢聆听</h2><p>Q&A环节</p>		meeting	published	[]	user1	系统管理员	4	0	2	2025-10-17 08:04:56.753327+00	2025-10-17 08:08:03.502187+00		对内	t	[]	[]	["研发部标注组"]	f	\N	\N	proj2025401
ea34a309-7ebb-4ef5-816b-2dffb093bdea	多所属部门测试	<p><strong>胡鑫瑞</strong>：</p><p>自我介绍：</p><p>我在研究生期间有一年多的企业实习经验，主要从事DR图像处理相关工作，包括图像分割预处理、特征提取和算法优化等，并基于此开发了颈椎功能评估软件，熟悉深度学习。实习过程中，我不仅提升了技术能力，也增强了团队协作和问题解决的能力。<br>本科阶段我主修数学，具备良好的数理基础；研究生则专注于智能医学，结合人工智能与医疗应用。通过实践，我能够将专业知识高效应用于实际项目中。</p><p>之前处理的DR视频图像都是dcm格式 医院发过来的都是dcm格式的文件</p><p>问题：那如果将您的项目上所做的动态分析方法扩展到三维上，会面临哪些挑战？</p><p>我做的是颈椎和腰椎的二维动态分析 如果扩展到三维上面我认为面对的挑战有这些：<br>1.标注 之前的颈椎和腰椎都是二维的标注比较容易 现在扩展到三维需要标注的内容更多<br>2.分割网络 由于扩展到三维动态分析 分割的要求更高 需要的网络要求也更高 对于学习率 批次的选择也复杂<br>3.特征提取 三维图像需要提取的特征也更多算法也更复杂<br>这是我认为的基于我所做的项目扩展到三维上所面临的挑战</p><p><strong>余宇</strong>：在广州，在成都上班没有问题</p><p>自我介绍:</p><p>研究方向主要为深度学习图神经网络方向在医学病理图像与基因组上的分析与识别，主要使用Python，pytorch，Sam大模型分割，项目已经形成论文一篇并在bibm上接收。在医学影像项目中，曾参与编写MRI影像图学习识别方法发明专利并成功授权。同时在这段时间也有例如生工大赛，互联网＋的学科竞赛项目，同样我的负责方向为算法开法与数据关联性分析。研究期间主要使用工具也是Python中的numpy，pytorch等数据分析或人工智能构建库，去进行图神经网络（GNN,GAT,GIN)或者其他神经网络如lstm的构建。</p><p>有过llm的本地部署，之前使用过ollama进行过qwen和deepseek的部署操作。、</p><p>目前接触过的三维医学影像有mri影像的分析。</p><p>问题：</p><p>你主要是对病理图像处理，您的病理图像处理经验如何迁移到CT/MRI等医学影像分析？</p><p>由于我数据上以病理图像为主，但是本身还是以技术方法，如图学习的运用为主要路线。在病理图像上我通过图像分块进行特征提取的方法进行图构建，在mri上由于图像呈多层结构，所以我使用单层为一个特征提取的图像块，将原先单一图像中不同区域的关联关系转变为多层图像之间的关联来进行分析的。</p>		meeting	published	[]	user1	系统管理员	4	0	1	2025-10-17 08:07:06.494552+00	2025-10-17 08:08:22.366753+00		对内	t	["user8", "user15", "user14", "user12", "user13", "user6"]	[]	["研发部标注组", "研发部算法组"]	f	\N	\N	proj1
\.


--
-- TOC entry 3630 (class 0 OID 24887)
-- Dependencies: 217
-- Data for Name: collaboration_documents; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.collaboration_documents (id, title, description, content, status, priority, owner_id, owner_name, project_id, project_name, category, tags, last_edited_by, last_edited_at, view_count, edit_count, version, is_locked, locked_by, locked_at, created_at, updated_at) FROM stdin;
a3a619d9-f5ad-46be-8fd7-d895c727eeb6	测试1		<p><br></p>	draft	normal	user1	系统管理员	\N	\N	技术文档	["\\u6280\\u672f\\u6587\\u6863"]	admin	2025-09-30 14:33:30.590759	9	1	2	f	\N	\N	2025-09-28 07:41:41.394839	2025-09-30 06:47:51.249165
f7f167a5-18dd-4357-909a-dccc7a8ffd44	fffff		<hr/><p>fffffbkhjs;ajf;jas;lkoqpwieqj</p><p>dahlfjlpuiwqeqw</p><p>fasfafasfasfasasfasfasfasf</p><p>系统管理员进行这个在编辑<img src="http://localhost:9000/medical-annotations/wangeditor/32f9c34f-83e6-4acd-a1a2-1730c163124d.png" alt="生产完成示意图.png" data-href="http://localhost:9000/medical-annotations/wangeditor/32f9c34f-83e6-4acd-a1a2-1730c163124d.png" style="width: 548.66px;height: 224.50px;"/></p><p>代雨昕正在编辑这个文档aaadf撒切尔</p><p>5456456fff</p><p>asdjlkasdfff &nbsp; </p>	draft	normal	user1	系统管理员	\N	\N		["\\u4f1a\\u8bae\\u8bb0\\u5f55", "\\u9700\\u6c42\\u5206\\u6790"]	admin	2025-09-28 17:07:30.41796	133	149	150	f	\N	\N	2025-09-11 08:55:41.388291	2025-10-13 03:40:39.016186
9fb9127f-3d2f-477b-b872-0caa44a4449d	协作文档发布测试	这是一个文档描述	<p>XXJZ-FROM-16-A-02</p><p><strong>人员需求申请表</strong></p><table style="width: auto;"><tbody><tr><td colSpan="1" rowSpan="1" width="auto">申请人</td><td colSpan="1" rowSpan="1" width="auto">张洺恒</td><td colSpan="1" rowSpan="1" width="auto">申请部门</td><td colSpan="1" rowSpan="1" width="auto">研发部</td><td colSpan="1" rowSpan="1" width="auto">申请日期</td><td colSpan="1" rowSpan="1" width="auto">2025.09.25</td></tr><tr><td colSpan="6" rowSpan="1" width="auto">招聘信息</td></tr><tr><td colSpan="1" rowSpan="1" width="auto">岗位名称</td><td colSpan="1" rowSpan="1" width="auto">软件开发工程师</td><td colSpan="1" rowSpan="1" width="auto">需求人数</td><td colSpan="1" rowSpan="1" width="auto">1</td><td colSpan="1" rowSpan="1" width="auto">到岗时间</td><td colSpan="1" rowSpan="1" width="auto">2025.10.25</td></tr><tr><td colSpan="1" rowSpan="1" width="auto">2需求原因</td><td colSpan="5" rowSpan="1" width="auto">研发部算法和开发团队需要有人对公司自研软件进行持续修复，并且满足临时的软件开发需求</td></tr><tr><td colSpan="6" rowSpan="1" width="auto">基本要求</td></tr><tr><td colSpan="1" rowSpan="1" width="auto">性别</td><td colSpan="2" rowSpan="1" width="auto">男</td><td colSpan="1" rowSpan="1" width="auto">年龄</td><td colSpan="2" rowSpan="1" width="auto">22~26</td></tr><tr><td colSpan="1" rowSpan="1" width="auto">学历</td><td colSpan="2" rowSpan="1" width="auto">本科及以上</td><td colSpan="1" rowSpan="1" width="auto">专业</td><td colSpan="2" rowSpan="1" width="auto">计算机或软件工程相关专业</td></tr><tr><td colSpan="1" rowSpan="1" width="auto">从事行业或工作经历要求</td><td colSpan="5" rowSpan="1" width="auto">本科及以上学历，计算机、软件工程、电子信息、生物医学工程等相关专业，2025届应届毕业生；扎实的 C++ 基础：深入理解面向对象编程，掌握多线程、智能指针、Lambda 表达式、STL 容器与算法等特性；Qt 框架：掌握 Qt 基本开发，理解其内部机制（QObject、信号槽、事件机制），熟悉 Qt 界面布局、绘图、多线程模块；熟悉常见开发环境和工具链：Linux/Windows、CMake/qmake、Git；具备良好的逻辑思维、团队协作与沟通能力。</td></tr><tr><td colSpan="1" rowSpan="1" width="auto">补充说明</td><td colSpan="5" rowSpan="1" width="auto">熟悉 TCP/IP 网络编程，具备 Socket、多线程网络服务开发经验；熟悉图像处理/计算机视觉（OpenCV、VTK、ITK）；了解医疗影像标准（如 DICOM）；</td></tr><tr><td colSpan="6" rowSpan="1" width="auto">职位描述（可附页）</td></tr><tr><td colSpan="6" rowSpan="1" width="auto">参与公司医疗影像处理与算法平台的研发，基于 C/C++ 与 Qt 框架进行桌面端应用开发；参与开发并持续优化服务于 GMP 流程的生产类软件，确保系统满足医疗与法规要求；实现医疗图像可视化、交互界面、数据管理等功能模块，并进行性能与用户体验优化；配合算法团队，将深度学习/医学影像算法 高效集成到生产与应用软件中；参与需求分析、架构设计、代码实现、测试与文档编写，保证软件的质量、可维护性与合规性；</td></tr><tr><td colSpan="1" rowSpan="1" width="auto">初拟薪资</td><td colSpan="5" rowSpan="1" width="auto">8k</td></tr><tr><td colSpan="1" rowSpan="1" width="auto">招聘方式</td><td colSpan="5" rowSpan="1" width="auto">□人力资源部统一招聘 □本部门自行招聘 □内部竞聘</td></tr><tr><td colSpan="2" rowSpan="1" width="auto">用人部门</td><td colSpan="2" rowSpan="1" width="auto">人力资源部</td><td colSpan="2" rowSpan="1" width="auto">总经理</td></tr><tr><td colSpan="2" rowSpan="1" width="auto"></td><td colSpan="2" rowSpan="1" width="auto"></td><td colSpan="2" rowSpan="1" width="auto"></td></tr></tbody></table><p><br></p>	draft	high	user1	系统管理员	\N	\N	\N	["\\u6280\\u672f\\u65b9\\u6848", "\\u534f\\u4f5c"]	系统管理员	2025-10-13 11:55:23.013645	0	0	1	f	\N	\N	2025-10-13 03:55:22.998453	2025-10-13 03:56:04.396475
1afba90d-a590-44ed-b8f1-290baca1686d	技术方案设计	系统架构和技术选型方案	<p>技术方案设计</p><p>本文档用于记录技术方案的设计思路和实现细节。</p><p><br></p><p><br></p>	draft	normal	user1	系统管理员	\N	\N	技术文档	["技术方案", "架构设计", "协作"]	admin	2025-09-10 17:35:54.237373	30	39	39	f	\N	\N	2025-09-09 14:42:53.742018	2025-10-16 07:12:54.918548
c9d6c31d-20fc-41b9-a88d-fede780c4edc	人员需求申请表	人员需求申请表	<p>XXJZ-FROM-16-A-02</p><p><strong>人员需求申请表</strong></p><table style="width: auto;"><tbody><tr><td colSpan="1" rowSpan="1" width="auto">申请人</td><td colSpan="1" rowSpan="1" width="auto">张洺恒</td><td colSpan="1" rowSpan="1" width="auto">申请部门</td><td colSpan="1" rowSpan="1" width="auto">研发部</td><td colSpan="1" rowSpan="1" width="auto">申请日期</td><td colSpan="1" rowSpan="1" width="auto">2025.09.25</td></tr><tr><td colSpan="6" rowSpan="1" width="auto">招聘信息</td></tr><tr><td colSpan="1" rowSpan="1" width="auto">岗位名称</td><td colSpan="1" rowSpan="1" width="auto">软件开发工程师</td><td colSpan="1" rowSpan="1" width="auto">需求人数</td><td colSpan="1" rowSpan="1" width="auto">1</td><td colSpan="1" rowSpan="1" width="auto">到岗时间</td><td colSpan="1" rowSpan="1" width="auto">2025.10.25</td></tr><tr><td colSpan="1" rowSpan="1" width="auto">2需求原因</td><td colSpan="5" rowSpan="1" width="auto">研发部算法和开发团队需要有人对公司自研软件进行持续修复，并且满足临时的软件开发需求</td></tr><tr><td colSpan="6" rowSpan="1" width="auto">基本要求</td></tr><tr><td colSpan="1" rowSpan="1" width="auto">性别</td><td colSpan="2" rowSpan="1" width="auto">男</td><td colSpan="1" rowSpan="1" width="auto">年龄</td><td colSpan="2" rowSpan="1" width="auto">22~26</td></tr><tr><td colSpan="1" rowSpan="1" width="auto">学历</td><td colSpan="2" rowSpan="1" width="auto">本科及以上</td><td colSpan="1" rowSpan="1" width="auto">专业</td><td colSpan="2" rowSpan="1" width="auto">计算机或软件工程相关专业</td></tr><tr><td colSpan="1" rowSpan="1" width="auto">从事行业或工作经历要求</td><td colSpan="5" rowSpan="1" width="auto">本科及以上学历，计算机、软件工程、电子信息、生物医学工程等相关专业，2025届应届毕业生；扎实的 C++ 基础：深入理解面向对象编程，掌握多线程、智能指针、Lambda 表达式、STL 容器与算法等特性；Qt 框架：掌握 Qt 基本开发，理解其内部机制（QObject、信号槽、事件机制），熟悉 Qt 界面布局、绘图、多线程模块；熟悉常见开发环境和工具链：Linux/Windows、CMake/qmake、Git；具备良好的逻辑思维、团队协作与沟通能力。</td></tr><tr><td colSpan="1" rowSpan="1" width="auto">补充说明</td><td colSpan="5" rowSpan="1" width="auto">熟悉 TCP/IP 网络编程，具备 Socket、多线程网络服务开发经验；熟悉图像处理/计算机视觉（OpenCV、VTK、ITK）；了解医疗影像标准（如 DICOM）；</td></tr><tr><td colSpan="6" rowSpan="1" width="auto">职位描述（可附页）</td></tr><tr><td colSpan="6" rowSpan="1" width="auto">参与公司医疗影像处理与算法平台的研发，基于 C/C++ 与 Qt 框架进行桌面端应用开发；参与开发并持续优化服务于 GMP 流程的生产类软件，确保系统满足医疗与法规要求；实现医疗图像可视化、交互界面、数据管理等功能模块，并进行性能与用户体验优化；配合算法团队，将深度学习/医学影像算法 高效集成到生产与应用软件中；参与需求分析、架构设计、代码实现、测试与文档编写，保证软件的质量、可维护性与合规性；</td></tr><tr><td colSpan="1" rowSpan="1" width="auto">初拟薪资</td><td colSpan="5" rowSpan="1" width="auto">8k</td></tr><tr><td colSpan="1" rowSpan="1" width="auto">招聘方式</td><td colSpan="5" rowSpan="1" width="auto">□人力资源部统一招聘 □本部门自行招聘 □内部竞聘</td></tr><tr><td colSpan="2" rowSpan="1" width="auto">用人部门</td><td colSpan="2" rowSpan="1" width="auto">人力资源部</td><td colSpan="2" rowSpan="1" width="auto">总经理</td></tr><tr><td colSpan="2" rowSpan="1" width="auto"></td><td colSpan="2" rowSpan="1" width="auto"></td><td colSpan="2" rowSpan="1" width="auto"></td></tr></tbody></table><p><br></p>	draft	normal	user1	系统管理员	\N	\N	\N	["\\u534f\\u4f5c"]	系统管理员	2025-10-13 12:18:54.852436	0	0	1	f	\N	\N	2025-10-13 04:18:54.845724	2025-10-17 08:05:48.130729
\.


--
-- TOC entry 3631 (class 0 OID 24901)
-- Dependencies: 218
-- Data for Name: collaboration_sessions; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.collaboration_sessions (id, document_id, user_id, user_name, session_id, is_active, cursor_position, selection_start, selection_end, last_heartbeat, created_at, updated_at) FROM stdin;
318e3187-293f-4be5-b2e2-fa7b5c186e67	1afba90d-a590-44ed-b8f1-290baca1686d	user1	系统管理员	59e62dff-a77d-40c8-bc8c-cc6adbb70e11	t	\N	\N	\N	2025-09-28 15:23:24.217645	2025-09-28 07:23:24.21726	2025-09-28 07:23:24.21726
845583cc-9143-4c84-810e-03a2f2abb4fe	a3a619d9-f5ad-46be-8fd7-d895c727eeb6	user1	系统管理员	90e2d37c-de34-43ab-aeb1-bc948e94e517	f	\N	\N	\N	2025-09-30 14:33:30.612606	2025-09-28 08:40:14.922172	2025-09-30 06:33:30.58219
6fc74bec-2665-4507-a1d7-cff33a71a6b3	a3a619d9-f5ad-46be-8fd7-d895c727eeb6	user6	代雨昕	aba9b88e-d4ad-4702-a065-a280c21459c0	f	\N	\N	\N	2025-09-30 14:47:51.300552	2025-09-30 06:47:48.648047	2025-09-30 06:47:51.249165
cfa3dabb-253d-4ecf-85a4-f51bf435417a	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	代雨昕	524a025d-5ec9-4de4-b24c-d5ceb69a7121	f	\N	\N	\N	2025-09-28 17:00:20.848051	2025-09-12 04:29:43.950663	2025-09-28 09:00:20.847206
0d28f53f-8a9b-4fdf-a72d-824073fabd6d	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	系统管理员	f6ad8119-4be3-4b32-9b08-e126d0fb1ac5	f	\N	\N	\N	2025-10-13 11:40:39.010732	2025-09-12 04:29:52.473002	2025-10-13 03:40:39.016186
0356c9bf-3f0e-4a80-93eb-b89aff3f297e	9fb9127f-3d2f-477b-b872-0caa44a4449d	user1	系统管理员	d8b70bcc-46be-443d-b2ff-05741dacb0ee	f	\N	\N	\N	2025-10-13 11:56:04.409006	2025-10-13 03:55:35.937814	2025-10-13 03:56:04.396475
0104658b-fd02-4514-9760-16711b82945c	c9d6c31d-20fc-41b9-a88d-fede780c4edc	user6	代雨昕	509b5ef3-ab3d-4ec6-aa84-80761c37c5e9	f	\N	\N	\N	2025-10-13 12:54:25.331542	2025-10-13 04:22:32.125201	2025-10-13 04:54:25.300562
a1e98074-9c16-47c5-8fb5-39941c3bcc0b	c9d6c31d-20fc-41b9-a88d-fede780c4edc	user1	系统管理员	c4eac6d4-8121-4f7d-ac9c-50f61b7d9a2b	f	\N	\N	\N	2025-10-17 16:05:48.173745	2025-10-13 04:34:00.630526	2025-10-17 08:05:48.130729
\.


--
-- TOC entry 3632 (class 0 OID 24908)
-- Dependencies: 219
-- Data for Name: document_collaborators; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.document_collaborators (id, document_id, user_id, user_name, user_avatar, role, joined_at, last_active_at, created_at, updated_at) FROM stdin;
1b9bbc33-11bd-439b-b4b3-cfe9ad64727c	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	系统管理员	\N	editor	2025-09-11 08:55:41.388291	\N	2025-09-11 08:55:41.388291	2025-09-11 08:55:41.388291
4b1bf646-c1ee-4936-b408-51981d7ba3ad	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	代雨昕	\N	editor	2025-09-11 08:55:41.388291	\N	2025-09-11 08:55:41.388291	2025-09-11 08:55:41.388291
9e360ebc-e0b5-49f9-b976-2c675fbf2fc2	a3a619d9-f5ad-46be-8fd7-d895c727eeb6	user1	系统管理员	\N	editor	2025-09-28 07:41:41.394839	\N	2025-09-28 07:41:41.394839	2025-09-28 07:41:41.394839
d7d19632-ddae-436b-a407-d058f4ba2041	a3a619d9-f5ad-46be-8fd7-d895c727eeb6	user6	代雨昕	\N	editor	2025-09-28 07:41:41.394839	\N	2025-09-28 07:41:41.394839	2025-09-28 07:41:41.394839
cfbba63f-4196-4b1c-a4dd-0603aee35692	c9d6c31d-20fc-41b9-a88d-fede780c4edc	user6	代雨昕	\N	editor	2025-10-13 04:18:54.845724	\N	2025-10-13 04:18:54.845724	2025-10-13 04:18:54.845724
2d410ee3-9a3e-400b-a35e-d504230c2aea	c9d6c31d-20fc-41b9-a88d-fede780c4edc	user8	王欢欢	\N	editor	2025-10-13 04:18:54.845724	\N	2025-10-13 04:18:54.845724	2025-10-13 04:18:54.845724
145f0ffe-9280-475c-a3f8-d34e1ef76180	c9d6c31d-20fc-41b9-a88d-fede780c4edc	user1	系统管理员	\N	editor	2025-10-13 04:18:54.845724	\N	2025-10-13 04:18:54.845724	2025-10-13 04:18:54.845724
\.


--
-- TOC entry 3633 (class 0 OID 24917)
-- Dependencies: 220
-- Data for Name: document_comments; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.document_comments (id, document_id, user_id, user_name, user_avatar, content, "position", parent_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 3634 (class 0 OID 24924)
-- Dependencies: 221
-- Data for Name: document_edit_history; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.document_edit_history (id, document_id, editor_id, editor_name, action, changes_summary, content_diff, version_before, version_after, created_at, updated_at) FROM stdin;
d6b09ed1-d8a7-42bb-ab86-38cd5e3c5545	1afba90d-a590-44ed-b8f1-290baca1686d	user1	admin	edit_content	更新文档内容 (字符数: 44 -> 55)	\N	1	2	2025-09-10 07:22:36.647195	2025-09-10 07:22:36.647195
ac1d6b51-4920-40ee-bb29-c6c648047775	1afba90d-a590-44ed-b8f1-290baca1686d	user1	admin	edit_content	更新文档内容 (字符数: 55 -> 267)	\N	11	12	2025-09-10 07:29:38.671176	2025-09-10 07:29:38.671176
3b4e8638-6203-48c7-ad10-fcb15c74cf2c	1afba90d-a590-44ed-b8f1-290baca1686d	user1	admin	edit_content	更新文档内容 (字符数: 267 -> 66)	\N	26	27	2025-09-10 07:42:16.654343	2025-09-10 07:42:16.654343
4bac74a3-acf1-4e9b-9b1a-6d5b4c0f1af3	1afba90d-a590-44ed-b8f1-290baca1686d	user1	admin	edit_content	编辑内容	\N	31	32	2025-09-10 09:32:05.613502	2025-09-10 09:32:05.613502
bbf669b6-8281-4bcb-87c6-1b6caa086d30	1afba90d-a590-44ed-b8f1-290baca1686d	user1	admin	edit_content	编辑内容	\N	32	33	2025-09-10 09:32:36.444703	2025-09-10 09:32:36.444703
4e517982-2e11-4afa-8263-e8b46675b090	1afba90d-a590-44ed-b8f1-290baca1686d	user1	admin	edit_content	编辑内容	\N	33	34	2025-09-10 09:33:06.40875	2025-09-10 09:33:06.40875
0e7cdc03-df00-4fa4-a0d7-0b141776d69a	1afba90d-a590-44ed-b8f1-290baca1686d	user1	admin	edit_content	编辑内容	\N	34	35	2025-09-10 09:33:36.427642	2025-09-10 09:33:36.427642
f14589c6-f7db-4c58-b900-cd6af99a144a	1afba90d-a590-44ed-b8f1-290baca1686d	user1	admin	edit_content	编辑内容	\N	35	36	2025-09-10 09:34:05.833449	2025-09-10 09:34:05.833449
d4a68b43-ca54-49c6-9681-d7ef0c76c7ed	1afba90d-a590-44ed-b8f1-290baca1686d	user1	admin	edit_content	编辑内容	\N	36	37	2025-09-10 09:34:36.57396	2025-09-10 09:34:36.57396
a9c49b2d-c849-45f4-ae43-0b0a2f9cd167	1afba90d-a590-44ed-b8f1-290baca1686d	user1	admin	edit_content	编辑内容	\N	37	38	2025-09-10 09:35:06.638058	2025-09-10 09:35:06.638058
67d81076-7135-4284-a86b-a85d5e8fb3de	1afba90d-a590-44ed-b8f1-290baca1686d	user1	admin	edit_content	编辑内容	\N	38	39	2025-09-10 09:35:54.216308	2025-09-10 09:35:54.216308
31d9dfe2-f65f-4d14-8338-7bdbfa5cf81c	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	系统管理员	create	创建文档: fffff	\N	\N	1	2025-09-11 08:55:41.388291	2025-09-11 08:55:41.388291
845718ca-8a12-4aba-ae3a-8a450d12774b	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	1	2	2025-09-12 03:46:47.853079	2025-09-12 03:46:47.853079
7659d3c7-caa5-4fff-9d00-00b261c0afc2	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	2	3	2025-09-12 03:47:02.604562	2025-09-12 03:47:02.604562
2357e719-32d0-4a53-84ed-4edd0433366d	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	3	4	2025-09-12 03:56:18.507562	2025-09-12 03:56:18.507562
0ff68b2e-b14c-4bb2-ae32-4446b5ad72dc	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	4	5	2025-09-12 03:56:48.531228	2025-09-12 03:56:48.531228
1d404775-205f-4b51-96f5-c16ec1486b88	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	5	6	2025-09-12 03:57:18.502414	2025-09-12 03:57:18.502414
1b91980e-04f9-44bd-a19d-d97b8c6a6ab4	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	6	7	2025-09-12 03:57:48.508163	2025-09-12 03:57:48.508163
e61f7f42-6189-4e92-8e71-6d7937b6de36	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	7	8	2025-09-12 04:30:14.491125	2025-09-12 04:30:14.491125
1ce990ce-9c48-4f58-8c7b-7928070e9f6c	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	8	9	2025-09-12 04:30:44.499209	2025-09-12 04:30:44.499209
d46fba34-0d90-4e61-88c3-3a58c2dc0fcc	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	9	10	2025-09-12 04:31:14.48458	2025-09-12 04:31:14.48458
037a370f-e9bc-4020-b3ec-1ba995fc3632	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	10	11	2025-09-12 04:31:44.49823	2025-09-12 04:31:44.49823
b02704df-5022-4a4b-941b-f3a8e956691c	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	11	12	2025-09-12 04:32:14.483199	2025-09-12 04:32:14.483199
19fce319-47f1-4614-8ad2-31796ed0bdc3	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	12	13	2025-09-12 04:32:44.497211	2025-09-12 04:32:44.497211
6102e09a-aa57-4c59-bdac-9897c12a639c	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	13	14	2025-09-12 04:33:42.507927	2025-09-12 04:33:42.507927
28dda0f1-12d2-4b08-904d-30d0746aa186	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	14	15	2025-09-12 04:34:42.491981	2025-09-12 04:34:42.491981
16868028-fd70-4ed2-8729-15dd9acdc1af	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	15	16	2025-09-12 04:35:42.460354	2025-09-12 04:35:42.460354
6071c7a5-daae-4344-9fbd-0a1735c7a751	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	16	17	2025-09-12 04:36:42.490012	2025-09-12 04:36:42.490012
ee20fe3e-c4e7-47bb-8a25-fba713b035e3	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	17	18	2025-09-12 04:37:42.49055	2025-09-12 04:37:42.49055
6dfabbdd-476b-4aaa-8040-605fcb3dea82	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	18	19	2025-09-12 04:38:42.494487	2025-09-12 04:38:42.494487
3b7a5cef-707f-4618-8974-0916abee5b99	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	19	20	2025-09-12 04:39:42.497314	2025-09-12 04:39:42.497314
255fcc0b-85d1-4e2d-8ffd-8cfe24ea9ede	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	20	21	2025-09-12 04:40:42.490661	2025-09-12 04:40:42.490661
836c6c27-4865-4709-80d4-94cd2dbb0490	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	21	22	2025-09-12 04:41:42.490237	2025-09-12 04:41:42.490237
c9a2c74f-cdbe-48a4-afe9-53ca776de114	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	22	23	2025-09-12 04:42:42.50455	2025-09-12 04:42:42.50455
880f0354-bceb-4427-84fc-22fc8e793a7b	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	23	24	2025-09-12 04:43:42.488962	2025-09-12 04:43:42.488962
cc5112d9-2f2d-4b18-8585-e7eea7b36f76	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	24	25	2025-09-12 04:44:42.515433	2025-09-12 04:44:42.515433
fcd03aea-c1b7-40ac-aa96-2a352c0886e7	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	25	26	2025-09-12 04:45:42.486827	2025-09-12 04:45:42.486827
39ba9d20-1ff7-49b9-9125-eadc6034fd2f	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	26	27	2025-09-12 04:46:42.480446	2025-09-12 04:46:42.480446
02c8eb8a-d2ff-4a7c-a79e-a81b9feb3e83	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	27	28	2025-09-12 04:47:42.491005	2025-09-12 04:47:42.491005
2502062c-b58c-4ffc-8e6d-46751c05c361	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	28	29	2025-09-12 04:48:42.489821	2025-09-12 04:48:42.489821
116aa16a-a904-47c6-aefd-ea115f7cd74f	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	29	30	2025-09-12 04:49:42.512253	2025-09-12 04:49:42.512253
0bfafe9e-c98b-4de4-bfa5-63befeda4b47	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	30	31	2025-09-12 04:50:42.519693	2025-09-12 04:50:42.519693
df3446c1-92c6-478e-ba2a-8755299086b2	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	31	32	2025-09-12 04:51:42.524805	2025-09-12 04:51:42.524805
5378f6d3-526d-4494-8f71-d859fce8a0bc	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	32	33	2025-09-12 04:52:42.498781	2025-09-12 04:52:42.498781
e2b71b55-3319-42d8-aa12-35763c4bf3f1	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	33	34	2025-09-12 04:53:42.485793	2025-09-12 04:53:42.485793
b2989f11-83b3-4878-9c1d-ced000c09a09	a3a619d9-f5ad-46be-8fd7-d895c727eeb6	user1	admin	edit_content	编辑内容	\N	1	2	2025-09-30 06:33:30.561227	2025-09-30 06:33:30.561227
6cc355c9-6ffc-4934-a5fd-ce9d62997641	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	34	35	2025-09-12 04:54:42.468686	2025-09-12 04:54:42.468686
2b0f8e74-9f95-49d3-9108-0b2efcf6f003	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	35	36	2025-09-12 04:55:42.520469	2025-09-12 04:55:42.520469
a36e2701-af59-4185-8265-21bb825f5d80	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	36	37	2025-09-12 04:56:42.508375	2025-09-12 04:56:42.508375
581576e6-054a-412e-88f2-60d9262fccac	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	37	38	2025-09-12 04:57:42.484899	2025-09-12 04:57:42.484899
2f699006-dc9a-4183-b894-add290c3949b	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	38	39	2025-09-12 04:58:42.477453	2025-09-12 04:58:42.477453
a19a589e-1d74-420f-aa6b-54d088cb9567	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	39	40	2025-09-12 06:00:50.777362	2025-09-12 06:00:50.777362
8e3d9c61-7a5c-4747-9eae-2d876e1b0844	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	40	41	2025-09-12 06:01:15.476431	2025-09-12 06:01:15.476431
15524a40-688c-4ffa-940b-b1e73ed5899c	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	41	42	2025-09-12 06:01:39.995377	2025-09-12 06:01:39.995377
0a4e75ed-b3ec-4874-b3f8-4445d8b095aa	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	42	43	2025-09-12 06:01:45.47115	2025-09-12 06:01:45.47115
92839334-b9ba-492c-998a-308b038a0f9e	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	43	44	2025-09-12 06:02:10.433097	2025-09-12 06:02:10.433097
aade911b-3283-42dd-bb4a-e6c89017eef5	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	44	45	2025-09-12 06:02:15.450187	2025-09-12 06:02:15.450187
47518218-ed59-4b35-9f57-3d46ada97202	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	45	46	2025-09-12 06:02:40.455998	2025-09-12 06:02:40.455998
7e2c7eb8-e296-40c1-87e8-cfafc0b87acf	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	46	47	2025-09-12 06:02:45.467882	2025-09-12 06:02:45.467882
ad49223b-a2ad-4937-8cfb-e20ec271dc68	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	47	48	2025-09-12 06:03:10.465692	2025-09-12 06:03:10.465692
9db9081e-0c5a-410e-83ab-177aeb9af876	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	48	49	2025-09-12 06:03:15.477864	2025-09-12 06:03:15.477864
4314864a-7884-4ce7-a471-c63ddcf71b8a	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	49	50	2025-09-12 06:03:40.452929	2025-09-12 06:03:40.452929
e56d6fd1-eaf9-4212-8ed6-09f964c296b8	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	50	51	2025-09-12 06:03:49.499919	2025-09-12 06:03:49.499919
c822cc58-a8d8-4f6e-a4b4-61d531cda446	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	51	52	2025-09-12 06:04:19.78883	2025-09-12 06:04:19.78883
380336d8-41b9-4926-8e85-9bfbc59b8cad	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	52	53	2025-09-12 06:04:31.439978	2025-09-12 06:04:31.439978
c7ef3380-2bc0-4b8d-abcc-855a2616fb8d	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	53	54	2025-09-12 06:04:45.458606	2025-09-12 06:04:45.458606
3a45ecd3-a4a6-47fc-be03-58183e4d365b	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	54	55	2025-09-12 06:04:57.219308	2025-09-12 06:04:57.219308
f6042345-c5ca-4437-b048-f2bbd72e6261	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	55	56	2025-09-12 06:04:59.031599	2025-09-12 06:04:59.031599
9c14508a-6020-4e71-a698-1f90272dee2a	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	56	57	2025-09-12 06:05:01.40691	2025-09-12 06:05:01.40691
43160f91-69d3-4614-af60-9abe5d598249	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	57	58	2025-09-12 06:07:26.480458	2025-09-12 06:07:26.480458
3c692df5-8014-495f-b5dc-f913d90fe9cb	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	58	59	2025-09-12 06:07:29.80724	2025-09-12 06:07:29.80724
d51b53fe-2593-46a3-a423-36404807c9d8	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	59	60	2025-09-12 06:07:31.974389	2025-09-12 06:07:31.974389
ee4996b4-b0ff-4663-8f7e-e44621f39a22	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	60	61	2025-09-12 06:08:59.452672	2025-09-12 06:08:59.452672
cd96fcc8-ff20-48f0-b6c5-a883377a19fa	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	61	62	2025-09-12 06:09:01.498725	2025-09-12 06:09:01.498725
8b67b806-891f-40c2-90ab-65b48ad306f3	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	62	63	2025-09-12 06:09:03.445592	2025-09-12 06:09:03.445592
d1317b47-1327-45d2-b385-b57418bf03f3	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	63	64	2025-09-12 06:16:19.459817	2025-09-12 06:16:19.459817
48eac84a-8dbd-4f3c-9247-8ea7377eaca5	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	64	65	2025-09-12 06:16:49.453545	2025-09-12 06:16:49.453545
3fc77822-19fe-448c-a70c-253b9eafc7c9	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	65	66	2025-09-12 06:17:19.449782	2025-09-12 06:17:19.449782
3e06b9af-a075-4272-96fd-16e5386163bd	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	66	67	2025-09-12 06:17:49.454391	2025-09-12 06:17:49.454391
eb5d8df0-c05b-4e7f-9e62-95c7ee64eef6	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	67	68	2025-09-12 06:18:19.444418	2025-09-12 06:18:19.444418
ff1ac5b0-de7b-464a-a037-a1d4abcfc334	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	68	69	2025-09-12 06:18:49.448561	2025-09-12 06:18:49.448561
8af8141a-744f-4743-94e4-54ee5f219690	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	69	70	2025-09-12 06:19:42.509675	2025-09-12 06:19:42.509675
e07df4ae-b353-4293-84d4-fb8722099e65	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	70	71	2025-09-12 06:36:58.003729	2025-09-12 06:36:58.003729
75c1742d-7b20-4449-a6f1-be768d0ab345	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	71	72	2025-09-12 06:36:59.760628	2025-09-12 06:36:59.760628
be745424-1584-4a06-b5e0-d0cca65f9a6d	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	72	73	2025-09-12 06:37:13.408123	2025-09-12 06:37:13.408123
c39ea69f-4a0c-4cc2-bcd0-b1b5e7835d2b	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	73	74	2025-09-12 06:37:48.449365	2025-09-12 06:37:48.449365
38d90231-3756-4de8-b21e-3a65c49ffe3f	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	74	75	2025-09-12 06:38:18.434518	2025-09-12 06:38:18.434518
054597ab-647c-4f81-9bcb-c466b8c60b26	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	75	76	2025-09-12 06:38:48.441808	2025-09-12 06:38:48.441808
70f5a17e-8a7a-4602-8b49-0186e2967d40	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	76	77	2025-09-12 06:39:18.440626	2025-09-12 06:39:18.440626
68e4913e-af15-46d2-84b6-98ab670ca754	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	77	78	2025-09-12 06:39:48.441976	2025-09-12 06:39:48.441976
7d76c78e-bc34-40ce-86ec-6204bc05e5de	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	78	79	2025-09-12 06:40:18.440328	2025-09-12 06:40:18.440328
21678a95-7835-429f-b4c5-40d4ecbd5167	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	79	80	2025-09-12 06:41:42.495302	2025-09-12 06:41:42.495302
1ec03145-30cf-4b4e-8a84-b00035116710	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	80	81	2025-09-12 06:42:42.490217	2025-09-12 06:42:42.490217
caa0ab0e-d529-4e7f-96da-91bfe774f5e5	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	81	82	2025-09-12 06:43:42.476265	2025-09-12 06:43:42.476265
76eb8ff0-0a76-4c85-adb4-8d9610d4c32f	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	82	83	2025-09-12 06:44:42.476052	2025-09-12 06:44:42.476052
bf4de40b-aed1-492f-9999-4770ec452bcc	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	83	84	2025-09-12 06:45:42.481987	2025-09-12 06:45:42.481987
372278c1-61b9-4b71-bc01-f04fd670ea7f	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	84	85	2025-09-12 06:46:42.509947	2025-09-12 06:46:42.509947
f83eaf5c-87ef-4922-a4ee-64d59f4c79f7	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	85	86	2025-09-12 06:47:42.490547	2025-09-12 06:47:42.490547
46172ab5-77c8-4e09-ab80-656155e2369f	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	86	87	2025-09-12 06:48:42.495221	2025-09-12 06:48:42.495221
f0132351-04fd-4a62-bc7a-17ca6e9bb2e8	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	87	88	2025-09-12 06:49:42.487092	2025-09-12 06:49:42.487092
44521624-72a5-448c-a146-9bca22c6df73	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	88	89	2025-09-12 06:50:42.524164	2025-09-12 06:50:42.524164
ef7f14bc-e984-48b0-91e2-16aa682399ec	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	89	90	2025-09-12 06:51:19.442578	2025-09-12 06:51:19.442578
ffd7a260-97b8-4d3e-b923-cabcbe29187e	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	90	91	2025-09-12 06:52:42.480109	2025-09-12 06:52:42.480109
a2d41509-ef97-4fee-8964-82aaa91bc0e5	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	91	92	2025-09-12 06:53:42.486451	2025-09-12 06:53:42.486451
9bc37504-c402-43e5-9df4-d99f865845ce	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	92	93	2025-09-12 06:54:42.469646	2025-09-12 06:54:42.469646
b19aff05-e77d-4bf9-91c9-5c3219fa29d4	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	93	94	2025-09-12 06:55:40.473593	2025-09-12 06:55:40.473593
3eec131b-cec9-4f78-9bee-fc8481a68d6d	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	94	95	2025-09-12 06:55:47.93055	2025-09-12 06:55:47.93055
ed7a8475-af3f-4175-94e6-1096b1288801	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	95	96	2025-09-12 06:55:57.457198	2025-09-12 06:55:57.457198
0aecbbcb-4c65-4bbd-959f-4c9b798d4d90	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	96	97	2025-09-12 06:56:10.345409	2025-09-12 06:56:10.345409
2013af49-2889-4a91-b1f8-1247c1ac214a	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	97	98	2025-09-24 08:46:44.841383	2025-09-24 08:46:44.841383
611fd7be-5163-4c79-9a78-f75a6eeb593a	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	98	99	2025-09-24 08:47:15.556126	2025-09-24 08:47:15.556126
19effe03-8f72-4b9f-bbb5-c536388febe3	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	99	100	2025-09-24 08:47:39.131377	2025-09-24 08:47:39.131377
c98ba47a-ec25-467e-bec3-323f1704b07b	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	100	101	2025-09-24 08:47:45.552671	2025-09-24 08:47:45.552671
9c1cf2cb-7883-4e3c-96ba-237dfb74af8a	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	101	102	2025-09-24 08:47:56.343375	2025-09-24 08:47:56.343375
e0e1b407-3964-4a14-a420-7bbaf74a8731	a3a619d9-f5ad-46be-8fd7-d895c727eeb6	user1	系统管理员	create	创建文档: 测试1	\N	\N	1	2025-09-28 07:41:41.394839	2025-09-28 07:41:41.394839
899c7815-f92d-4cdc-8939-027970960fd2	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	102	103	2025-09-28 08:41:06.470967	2025-09-28 08:41:06.470967
830ee9c2-a13a-4fda-81e1-bdbe07a4ffda	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	103	104	2025-09-28 08:41:10.384983	2025-09-28 08:41:10.384983
5a5428e1-3eca-44bc-8d2f-9f709c8c2e4e	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	104	105	2025-09-28 08:41:36.474326	2025-09-28 08:41:36.474326
5075e03b-007b-4a92-97ad-2b959a2b1aa9	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	105	106	2025-09-28 08:41:40.383508	2025-09-28 08:41:40.383508
03f50eaf-525e-45ac-bae0-83f784520641	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	106	107	2025-09-28 08:42:06.464114	2025-09-28 08:42:06.464114
92dcfde3-d907-49da-bc26-513dd9de5dfd	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	107	108	2025-09-28 08:42:10.380948	2025-09-28 08:42:10.380948
5b1c3cf0-33d2-466d-8408-709a39ecae19	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	108	109	2025-09-28 08:42:36.470931	2025-09-28 08:42:36.470931
1bf6da84-d8bd-4527-bc14-67aedb54cef6	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	109	110	2025-09-28 08:42:40.396914	2025-09-28 08:42:40.396914
a889b7e8-72fc-4344-aadf-6deffd02bc86	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	110	111	2025-09-28 08:43:06.479871	2025-09-28 08:43:06.479871
99057b8f-c9de-4fee-b9dd-7dbc4ac7218b	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	111	112	2025-09-28 08:43:36.617174	2025-09-28 08:43:36.617174
fdf3555e-67ea-4712-b1ff-26fcf4e74de8	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	112	113	2025-09-28 08:44:06.615959	2025-09-28 08:44:06.615959
1557597e-491e-4ab9-84c6-3ca27608c2f8	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	113	114	2025-09-28 08:44:36.497868	2025-09-28 08:44:36.497868
71e43d2f-5db4-4894-9ae8-04a11b5826b4	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	114	115	2025-09-28 08:45:06.503041	2025-09-28 08:45:06.503041
721f4356-6296-41a4-85f5-3e9d2e0c65c7	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	115	116	2025-09-28 08:45:36.430145	2025-09-28 08:45:36.430145
92b1a2e7-32d7-458e-a134-f3c3bfee68ee	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	116	117	2025-09-28 08:46:18.464899	2025-09-28 08:46:18.464899
aaa785f2-1646-4c03-974f-8a0755c91205	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	117	118	2025-09-28 08:46:38.093986	2025-09-28 08:46:38.093986
195ccbc7-ca00-45b0-8a53-a197a8c6329d	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	118	119	2025-09-28 08:46:48.488444	2025-09-28 08:46:48.488444
d3893b80-b3e6-446a-a4e6-5803dc7c1333	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	119	120	2025-09-28 08:47:08.069979	2025-09-28 08:47:08.069979
30891a16-e5c3-480c-ab32-5a6fa39700e3	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	120	121	2025-09-28 08:47:18.480788	2025-09-28 08:47:18.480788
6ab920ad-6fdf-4f1f-9de0-43b68a021098	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	121	122	2025-09-28 08:47:37.998565	2025-09-28 08:47:37.998565
50d21d34-5c9d-4e9b-85d8-9e29d8676075	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	122	123	2025-09-28 08:48:11.431248	2025-09-28 08:48:11.431248
6f295f52-2c3f-4e7c-af34-fcb895bc4d54	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	123	124	2025-09-28 08:48:14.953302	2025-09-28 08:48:14.953302
d65d72cb-556f-4df5-9069-8fa3a1bea182	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	124	125	2025-09-28 08:48:41.38609	2025-09-28 08:48:41.38609
57f713ab-b802-46fd-af54-f165a4a93e42	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	125	126	2025-09-28 08:48:44.957436	2025-09-28 08:48:44.957436
5cb62938-9784-44eb-965d-883186766729	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	126	127	2025-09-28 08:49:11.418115	2025-09-28 08:49:11.418115
39f1086e-edcc-4069-9063-53aa35a79deb	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	127	128	2025-09-28 08:49:14.939193	2025-09-28 08:49:14.939193
1ebe563c-0f68-4a87-94f4-fe54ba7237b9	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	128	129	2025-09-28 08:49:41.428212	2025-09-28 08:49:41.428212
d884d9ee-5be3-42a9-9340-1c74c17eae96	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	129	130	2025-09-28 08:49:55.402522	2025-09-28 08:49:55.402522
266a97e7-e52c-42e7-bd36-788000308bf8	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	130	131	2025-09-28 08:53:31.556365	2025-09-28 08:53:31.556365
6eb07d22-b3fd-4afe-934c-cb5a9cfca6f8	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	131	132	2025-09-28 08:54:04.944501	2025-09-28 08:54:04.944501
a05d20da-945c-491b-9e60-782469f2f099	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	132	133	2025-09-28 08:54:34.954478	2025-09-28 08:54:34.954478
5c45dd4b-a6b1-4d5c-82a4-f25a2840c148	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	133	134	2025-09-28 08:55:04.933464	2025-09-28 08:55:04.933464
8f305f66-96b7-4dca-b64b-e65a8c13cc05	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	134	135	2025-09-28 08:55:34.955034	2025-09-28 08:55:34.955034
c7579d83-407b-432a-b55a-35fb062aae98	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	135	136	2025-09-28 08:56:04.955205	2025-09-28 08:56:04.955205
51e270ef-6e77-47aa-9498-566ae98c4c63	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	136	137	2025-09-28 08:57:24.535645	2025-09-28 08:57:24.535645
b7ff7b90-1d2f-45a2-be3e-3b87ecc2d90b	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	137	138	2025-09-28 08:58:28.599165	2025-09-28 08:58:28.599165
1aec8d43-73eb-4107-8cec-7491141b7fd7	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	138	139	2025-09-28 08:58:41.664032	2025-09-28 08:58:41.664032
26f64ab2-571d-44fb-8cc2-b2a6c6e8be84	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	139	140	2025-09-28 08:59:16.572254	2025-09-28 08:59:16.572254
48b04944-e27f-4e1f-bfb4-dd65f77f0974	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user6	dyx	edit_content	编辑内容	\N	140	141	2025-09-28 09:00:20.830144	2025-09-28 09:00:20.830144
dae07c62-2ed5-416b-8551-14d06fda6142	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	141	142	2025-09-28 09:03:17.465686	2025-09-28 09:03:17.465686
e4885bb1-92ad-4d72-80e7-29a010c38e03	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	142	143	2025-09-28 09:03:47.483504	2025-09-28 09:03:47.483504
a3102303-58c0-4e07-b924-811dcd8cd0c4	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	143	144	2025-09-28 09:04:17.488194	2025-09-28 09:04:17.488194
edc4880f-184e-45d4-9c54-a67e7dc587e3	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	144	145	2025-09-28 09:04:47.475265	2025-09-28 09:04:47.475265
befee568-ab03-448a-a6b0-6dccac9829aa	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	145	146	2025-09-28 09:05:30.37998	2025-09-28 09:05:30.37998
ca2cc5fa-ba26-4ec5-9261-581a18660af7	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	146	147	2025-09-28 09:06:00.373445	2025-09-28 09:06:00.373445
3ea5e16c-5c84-4e7c-9351-d72229676f4a	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	147	148	2025-09-28 09:06:30.3714	2025-09-28 09:06:30.3714
b9e7b9ef-1620-4fb2-a9c0-684c43742531	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	148	149	2025-09-28 09:07:00.362038	2025-09-28 09:07:00.362038
363e6b9c-4e67-408b-a2b5-a455290f60b4	f7f167a5-18dd-4357-909a-dccc7a8ffd44	user1	admin	edit_content	编辑内容	\N	149	150	2025-09-28 09:07:30.389156	2025-09-28 09:07:30.389156
909865b4-d355-4821-8af5-3e7cb4e0afdd	9fb9127f-3d2f-477b-b872-0caa44a4449d	user1	系统管理员	create	创建文档: 协作文档发布测试	\N	\N	1	2025-10-13 03:55:22.998453	2025-10-13 03:55:22.998453
2b777d99-981e-4e2a-8b7f-5705d2e753c1	c9d6c31d-20fc-41b9-a88d-fede780c4edc	user1	系统管理员	create	创建文档: 人员需求申请表	\N	\N	1	2025-10-13 04:18:54.845724	2025-10-13 04:18:54.845724
\.


--
-- TOC entry 3635 (class 0 OID 24931)
-- Dependencies: 222
-- Data for Name: performance_stats; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.performance_stats (id, user_id, period, date, total_tasks, completed_tasks, approved_tasks, rejected_tasks, total_score, average_score, total_hours, average_hours, created_at, updated_at) FROM stdin;
caf19aff-a03e-4613-ad2b-381c0dc4c733	user1	monthly	2025-09	1	0	0	0	0	0.00	0.00	0.00	2025-09-01 09:41:00.390007	2025-09-04 08:11:48.613232
63df2b6f-7d44-42ee-b313-e0a410cf69f1	user6	monthly	2025-09	10	10	10	0	10	1.00	0.00	0.00	2025-09-03 08:55:07.02503	2025-09-05 08:26:58.148867
708e80da-bfe8-4422-aa63-264f795ea7d1	user6	weekly	2025-35	6	6	6	0	6	1.00	0.00	0.00	2025-09-05 08:27:08.937071	2025-09-05 08:27:08.937071
3f979c8e-0fcb-4888-a8e2-88df2545b766	user6	yearly	2025	10	10	10	0	10	1.00	0.00	0.00	2025-09-05 08:27:18.478779	2025-09-05 08:27:18.478779
b6517c96-eab5-447e-8f0c-747e32c2d960	user1	monthly	2025-08	0	0	0	0	0	0.00	0.00	0.00	2025-08-29 09:54:21.646423	2025-08-29 09:54:21.646423
3036158e-84da-4722-b1a7-7cc4f6b810ed	user6	monthly	2025-10	0	0	0	0	0	0.00	0.00	0.00	2025-10-10 03:35:05.866349	2025-10-10 03:35:05.866349
b95a2642-e7ab-453b-a224-9dee88e4accc	user1	weekly	2025-41	0	0	0	0	0	0.00	0.00	0.00	2025-10-13 06:31:52.261677	2025-10-13 06:31:52.261677
9cbba38e-68f3-44df-9403-a24acfd2af2e	user1	daily	2025-10-13	0	0	0	0	0	0.00	0.00	0.00	2025-10-13 06:31:53.157217	2025-10-13 06:31:53.157217
9f55b254-0a4d-4028-98c6-a62a7232d8ef	user8	monthly	2025-10	1	2	2	0	10	5.00	0.00	0.00	2025-10-10 02:36:47.865637	2025-10-17 06:33:00.197562
8f922618-9685-48da-b255-ee49ae984f3e	user1	monthly	2025-10	0	19	19	0	95	5.00	0.00	0.00	2025-10-09 07:31:11.460115	2025-10-17 08:13:02.16302
\.


--
-- TOC entry 3645 (class 0 OID 49153)
-- Dependencies: 232
-- Data for Name: project_categories; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.project_categories (id, project_id, name, type, icon, description, sort_order, created_at, updated_at) FROM stdin;
270ad7ac-4066-49a8-8b30-529d13def981	f8b89026-2a33-424f-96e3-7e9d2ac5379d	会议记录	meeting	📋	\N	1	2025-10-15 06:04:26.080603	2025-10-15 06:04:26.080603
8d3670ef-4476-443e-ba04-f5a29e7a7046	proj1	会议记录	meeting	📋	\N	1	2025-10-15 06:04:26.080603	2025-10-15 06:04:26.080603
b11028de-9072-4033-93b6-5ca1af0598bc	proj2	会议记录	meeting	📋	\N	1	2025-10-15 06:04:26.080603	2025-10-15 06:04:26.080603
78d04f06-5dfd-48bd-a384-48fa5cb060af	proj2025301	会议记录	meeting	📋	\N	1	2025-10-15 06:04:26.080603	2025-10-15 06:04:26.080603
91e59a45-4f7a-4870-8ba1-910a1e733d96	proj2025302	会议记录	meeting	📋	\N	1	2025-10-15 06:04:26.080603	2025-10-15 06:04:26.080603
da1b8c8e-64a5-4ce7-a333-7a80dbffa9ff	proj2025401	会议记录	meeting	📋	\N	1	2025-10-15 06:04:26.080603	2025-10-15 06:04:26.080603
3b3bafdf-f74b-4a13-936e-da943ae86d3d	proj3	会议记录	meeting	📋	\N	1	2025-10-15 06:04:26.080603	2025-10-15 06:04:26.080603
06851d5b-f424-49e3-a55a-cd1605c33736	proj2025402	会议记录	meeting	📋	\N	1	2025-10-15 06:04:26.080603	2025-10-15 06:04:26.080603
a25aee00-48b5-4e89-9ddf-1fe3d08eaf0e	f8b89026-2a33-424f-96e3-7e9d2ac5379d	模型测试	model_test	🧪	\N	2	2025-10-15 06:04:26.080603	2025-10-15 06:04:26.080603
5c66fa2a-8296-4dcf-bf64-1f0b37ab7cac	proj1	模型测试	model_test	🧪	\N	2	2025-10-15 06:04:26.080603	2025-10-15 06:04:26.080603
793542c8-2db2-40fc-bbef-25aa87cb567b	proj2	模型测试	model_test	🧪	\N	2	2025-10-15 06:04:26.080603	2025-10-15 06:04:26.080603
2f5a5224-1e4c-4906-861e-64d5751e91cf	proj2025301	模型测试	model_test	🧪	\N	2	2025-10-15 06:04:26.080603	2025-10-15 06:04:26.080603
28daa6c3-6a07-4ba7-9e75-7e67108c498a	proj2025302	模型测试	model_test	🧪	\N	2	2025-10-15 06:04:26.080603	2025-10-15 06:04:26.080603
ba7975aa-6ac4-4c97-ae18-4361a35b2673	proj2025401	模型测试	model_test	🧪	\N	2	2025-10-15 06:04:26.080603	2025-10-15 06:04:26.080603
4e9ee1fa-0aae-49fc-bfd7-1345b7918603	proj3	模型测试	model_test	🧪	\N	2	2025-10-15 06:04:26.080603	2025-10-15 06:04:26.080603
24f46ecc-71fe-41f5-a220-41b6ff65eab7	proj2025402	模型测试	model_test	🧪	\N	2	2025-10-15 06:04:26.080603	2025-10-15 06:04:26.080603
327f60f8-e30a-4e61-9c90-3387d3a4cee6	f8b89026-2a33-424f-96e3-7e9d2ac5379d	需求文档	requirement	\N	\N	0	2025-10-15 06:17:52.415684	2025-10-15 06:17:52.415684
2e8bf91f-355a-4bf2-a4a0-41ee1b30ed7b	proj2025403	会议记录	meeting	📋	\N	1	2025-10-15 07:04:21.70526	2025-10-15 07:04:21.70526
7e01d7ba-16e2-41a8-b781-445eb35773de	proj2025403	模型测试	model_test	🧪	\N	2	2025-10-15 07:04:21.70526	2025-10-15 07:04:21.70526
\.


--
-- TOC entry 3636 (class 0 OID 24936)
-- Dependencies: 223
-- Data for Name: project_stats; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.project_stats (id, project_id, total_tasks, pending_tasks, in_progress_tasks, completed_tasks, approved_tasks, rejected_tasks, completion_rate, average_score, total_hours, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 3637 (class 0 OID 24941)
-- Dependencies: 224
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.projects (id, name, description, status, priority, start_date, end_date, created_by, total_tasks, completed_tasks, assigned_tasks, created_at, updated_at, category, sub_category) FROM stdin;
proj1	20241201_泌尿系统CT标注项目	泌尿系统CT影像的精确标注，包括肾脏、膀胱、输尿管等器官的识别和标注	active	high	2024-12-01	2024-12-31	user1	10	3	5	2025-08-29 09:12:58.092482	2025-10-14 03:12:39.73736	case	trial
proj2	20241205_胸部X光片标注项目	胸部X光片的肺部疾病检测标注，包括肺炎、结核、肿瘤等病变的识别	active	medium	2024-12-05	2025-01-15	user1	7	3	5	2025-08-29 09:12:58.092482	2025-10-14 03:12:39.73736	case	trial
proj2025302	20250905泌尿第五批	泌尿数据	active	medium	2025-09-05	\N	user6	48	2	2	2025-09-05 06:35:53.269229	2025-10-14 03:12:39.73736	ai_annotation	daily
proj3	20241210_脑部MRI标注项目	脑部MRI影像的神经结构标注，包括脑肿瘤、脑梗塞、脑出血等病变的精确标注	completed	high	2024-12-10	2025-10-14	user1	5	5	5	2025-08-29 09:12:58.092482	2025-10-14 03:12:39.73736	case	trial
proj2025402	20251014肝胆标注	注意命名	active	medium	2025-10-14	\N	user6	0	0	0	2025-10-14 07:59:24.472511	2025-10-14 07:59:24.472511	case	trial
proj2025403	20251015肝胆标注任务	肝胆标注任务的项目描述	active	medium	2025-10-15	\N	user1	0	0	0	2025-10-15 07:04:21.66121	2025-10-15 07:04:21.66121	case	research
proj2025401	20251009任务导入测试		active	medium	2025-10-09	\N	user1	48	2	3	2025-10-09 08:10:04.264305	2025-10-17 06:33:00.187063	ai_annotation	research_ai
f8b89026-2a33-424f-96e3-7e9d2ac5379d	20250902		active	medium	2025-09-02	\N	user1	48	19	15	2025-09-02 06:38:52.232262	2025-10-17 08:12:59.6003	case	trial
proj2025301	20250904泌尿CT标注任务	此项目为泌尿第四批标注	active	medium	2025-09-04	\N	user1	121	17	17	2025-09-04 02:11:21.426306	2025-10-17 08:13:02.150692	case	trial
\.


--
-- TOC entry 3638 (class 0 OID 24948)
-- Dependencies: 225
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.roles (id, name, role, description, is_active, created_at, updated_at, permissions) FROM stdin;
5c564516-3809-46e7-9581-405865c777a9	审核员	reviewer	负责标注审核的用户	t	2025-08-29 09:12:58.092482	2025-09-11 07:22:14.474264	["Project", "ProjectDashboard", "ProjectManagement", "TaskPool", "MyWorkspace", "TaskReview", "WorkLogManagement", "WorkLogWeekDetail", "CollaborationManagement", "CollaborationDocument", "MeetingNotes", "ModelTests", "ArticleDetail", "Performance", "TeamPerformance", "PersonalPerformance", "System", "UserManagement", "RoleManagement", "UserCenter"]
f5d095ca-5d27-479d-84e9-f60b7c3455f0	管理员	admin	系统管理员，拥有所有权限	t	2025-08-29 09:12:58.092482	2025-10-16 07:51:19.775965	["Dashboard", "Console", "Project", "ProjectDashboard", "ProjectManagement", "Task", "TaskPool", "MyWorkspace", "TaskReview", "WorkLog", "WorkLogManagement", "WorkLogWeekDetail", "Articles", "MeetingNotes", "ModelTests", "CollaborationManagement", "ArticleDetail", "CollaborationCreate", "CollaborationDocument", "Performance", "PersonalPerformance", "TeamPerformance", "System", "UserManagement", "RoleManagement", "UserCenter"]
362b6c0e-0263-4d4b-99a1-3e7c0782e5de	标注员	annotator	负责图像标注的普通用户	t	2025-08-29 09:12:58.092482	2025-10-16 07:51:58.93738	["ProjectManagement", "TaskPool", "MyWorkspace", "WorkLog", "WorkLogManagement", "WorkLogWeekDetail", "MeetingNotes", "CollaborationManagement", "ArticleDetail", "CollaborationDocument", "PersonalPerformance", "UserCenter"]
0588e5c7-2950-4499-b18d-246e9e813321	行政员	executive	负责行政事务	t	2025-10-16 03:59:03.582384	2025-10-16 08:36:14.350156	["WorkLog", "WorkLogManagement", "WorkLogWeekDetail", "Articles", "MeetingNotes", "ModelTests", "CollaborationManagement", "ArticleDetail", "CollaborationCreate", "CollaborationDocument", "UserCenter"]
a6faa22b-f952-45be-9b8f-7ddbd5cad880	开发工程师	development	负责软件或网页开发	t	2025-10-16 03:29:52.23115	2025-10-16 08:36:19.072768	["WorkLog", "WorkLogManagement", "WorkLogWeekDetail", "Articles", "MeetingNotes", "ModelTests", "CollaborationManagement", "ArticleDetail", "CollaborationCreate", "CollaborationDocument", "UserCenter"]
08a14e07-d024-4b89-a2de-83c1b2809025	算法工程师	algorithm	负责算法研发工作	t	2025-10-16 03:27:30.351242	2025-10-16 08:36:23.0819	["ProjectManagement", "WorkLog", "WorkLogManagement", "WorkLogWeekDetail", "Articles", "MeetingNotes", "ModelTests", "CollaborationManagement", "ArticleDetail", "CollaborationCreate", "CollaborationDocument", "UserCenter"]
\.


--
-- TOC entry 3639 (class 0 OID 24955)
-- Dependencies: 226
-- Data for Name: task_attachments; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.task_attachments (id, task_id, file_name, file_url, file_size, file_type, attachment_type, uploaded_by, created_at) FROM stdin;
ec931258-9f7b-4723-ad96-12a98d2a684e	16146129-de9a-4f16-a0a0-76f774183ea8	f28274a8-c3fe-459e-aeeb-c519c6951d98.png	http://localhost:9000/medical-annotations/reviews/16146129-de9a-4f16-a0a0-76f774183ea8/f28274a8-c3fe-459e-aeeb-c519c6951d98.png	\N	image	review_screenshot	user1	2025-09-02 09:08:51.105469
f3974c33-75bb-44f5-b654-2f9c0bb655e4	16146129-de9a-4f16-a0a0-76f774183ea8	f28274a8-c3fe-459e-aeeb-c519c6951d98.png	http://localhost:9000/medical-annotations/reviews/16146129-de9a-4f16-a0a0-76f774183ea8/f28274a8-c3fe-459e-aeeb-c519c6951d98.png	\N	image	review_screenshot	user1	2025-09-02 09:08:51.155818
7df1d6f5-a97d-4fd1-a803-06f60395d76f	24c243c6-7bca-4e28-80b8-f855ddc7e09d	488927bf-fbb2-4a97-bd2f-48c96b91e712.png	http://localhost:9000/medical-annotations/reviews/24c243c6-7bca-4e28-80b8-f855ddc7e09d/488927bf-fbb2-4a97-bd2f-48c96b91e712.png	\N	image	review_screenshot	user1	2025-09-03 05:01:10.436237
7acc6a71-933b-4697-a7e4-469b32251d3b	24c243c6-7bca-4e28-80b8-f855ddc7e09d	488927bf-fbb2-4a97-bd2f-48c96b91e712.png	http://localhost:9000/medical-annotations/reviews/24c243c6-7bca-4e28-80b8-f855ddc7e09d/488927bf-fbb2-4a97-bd2f-48c96b91e712.png	\N	image	review_screenshot	user1	2025-09-03 05:01:10.582738
edeb3cb5-43e8-4ce0-a54f-9e57f455d3ad	157cb789-fd87-48b0-a02c-d1cb02476169	533feef3-5155-4f81-a5ee-c96bd104f860.png	http://localhost:9000/medical-annotations/reviews/157cb789-fd87-48b0-a02c-d1cb02476169/533feef3-5155-4f81-a5ee-c96bd104f860.png	\N	image	review_screenshot	user1	2025-09-03 05:54:33.1448
ef4fa2c0-df4c-4170-8c98-2b6d53211c67	157cb789-fd87-48b0-a02c-d1cb02476169	533feef3-5155-4f81-a5ee-c96bd104f860.png	http://localhost:9000/medical-annotations/reviews/157cb789-fd87-48b0-a02c-d1cb02476169/533feef3-5155-4f81-a5ee-c96bd104f860.png	\N	image	review_screenshot	user1	2025-09-03 05:54:33.339288
280e75cb-c86b-4290-a939-c59db36a244f	2161e972-ac9c-4f2a-bee3-44407c04a877	5f57d716-ea8c-4ba1-a05b-68eda1cc32a5.png	http://localhost:9000/medical-annotations/reviews/2161e972-ac9c-4f2a-bee3-44407c04a877/5f57d716-ea8c-4ba1-a05b-68eda1cc32a5.png	\N	image	skip_screenshot	user1	2025-09-03 07:50:24.800577
03da9e54-2964-4be6-8df2-919d75bf2a09	303e3b52-370c-4d52-87ec-1cf8633f8665	cd9914f2-0348-401a-adda-5fd417889de2.png	http://localhost:9000/medical-annotations/annotations/303e3b52-370c-4d52-87ec-1cf8633f8665/cd9914f2-0348-401a-adda-5fd417889de2.png	\N	image	annotation_screenshot	user1	2025-09-04 08:01:06.841231
1b2be71e-513e-4bf4-8360-8c7b6b17ed4f	303e3b52-370c-4d52-87ec-1cf8633f8665	470ca68b-1d42-4113-b709-ac7012bd2049.png	http://localhost:9000/medical-annotations/annotations/303e3b52-370c-4d52-87ec-1cf8633f8665/470ca68b-1d42-4113-b709-ac7012bd2049.png	\N	image	annotation_screenshot	user1	2025-09-04 08:01:06.841231
8b39151a-249a-4ef6-81e3-fdb2f98f59f1	303e3b52-370c-4d52-87ec-1cf8633f8665	da106c43-fe25-4ed8-b1ea-fc6c30ba69f9.png	http://localhost:9000/medical-annotations/reviews/303e3b52-370c-4d52-87ec-1cf8633f8665/da106c43-fe25-4ed8-b1ea-fc6c30ba69f9.png	\N	image	review_screenshot	user1	2025-09-04 08:02:16.853882
9d717f50-d3ca-4c50-99c1-dc27741a6f00	303e3b52-370c-4d52-87ec-1cf8633f8665	d5a8cccc-1f1b-4464-b131-a384007167a2.png	http://localhost:9000/medical-annotations/reviews/303e3b52-370c-4d52-87ec-1cf8633f8665/d5a8cccc-1f1b-4464-b131-a384007167a2.png	\N	image	review_screenshot	user1	2025-09-04 08:02:16.853882
0152f6f3-ced5-4189-9b32-1d6631151ca1	303e3b52-370c-4d52-87ec-1cf8633f8665	0a194e0b-2a38-4e1e-9319-0ff7e938f4f1.png	http://localhost:9000/medical-annotations/reviews/303e3b52-370c-4d52-87ec-1cf8633f8665/0a194e0b-2a38-4e1e-9319-0ff7e938f4f1.png	\N	image	review_screenshot	user1	2025-09-04 08:02:16.853882
26a8d0a9-014c-4575-ba6b-7559cad67d47	303e3b52-370c-4d52-87ec-1cf8633f8665	e8f30065-3f7e-40d5-b1a3-6737bacefe92.png	http://localhost:9000/medical-annotations/reviews/303e3b52-370c-4d52-87ec-1cf8633f8665/e8f30065-3f7e-40d5-b1a3-6737bacefe92.png	\N	image	review_screenshot	user1	2025-09-04 08:02:16.853882
ec4b1e80-c03c-42a6-8508-568832dcbd62	303e3b52-370c-4d52-87ec-1cf8633f8665	da106c43-fe25-4ed8-b1ea-fc6c30ba69f9.png	http://localhost:9000/medical-annotations/reviews/303e3b52-370c-4d52-87ec-1cf8633f8665/da106c43-fe25-4ed8-b1ea-fc6c30ba69f9.png	\N	image	review_screenshot	user1	2025-09-04 08:02:16.902238
70a62d4f-76ac-4a01-898a-ccaa28a07582	303e3b52-370c-4d52-87ec-1cf8633f8665	d5a8cccc-1f1b-4464-b131-a384007167a2.png	http://localhost:9000/medical-annotations/reviews/303e3b52-370c-4d52-87ec-1cf8633f8665/d5a8cccc-1f1b-4464-b131-a384007167a2.png	\N	image	review_screenshot	user1	2025-09-04 08:02:16.902238
1e58b302-48e8-46ae-82d0-70410ad8b252	303e3b52-370c-4d52-87ec-1cf8633f8665	0a194e0b-2a38-4e1e-9319-0ff7e938f4f1.png	http://localhost:9000/medical-annotations/reviews/303e3b52-370c-4d52-87ec-1cf8633f8665/0a194e0b-2a38-4e1e-9319-0ff7e938f4f1.png	\N	image	review_screenshot	user1	2025-09-04 08:02:16.902238
fe8d2225-fa4f-45a3-8e5b-da800301317a	303e3b52-370c-4d52-87ec-1cf8633f8665	e8f30065-3f7e-40d5-b1a3-6737bacefe92.png	http://localhost:9000/medical-annotations/reviews/303e3b52-370c-4d52-87ec-1cf8633f8665/e8f30065-3f7e-40d5-b1a3-6737bacefe92.png	\N	image	review_screenshot	user1	2025-09-04 08:02:16.902238
43af116d-01fa-462a-8b28-8853c6fd8cab	3b95072f-b399-4b0a-8592-11067495d965	f1fa4623-1488-47d7-9545-b46903e3daf5.png	http://localhost:9000/medical-annotations/reviews/3b95072f-b399-4b0a-8592-11067495d965/f1fa4623-1488-47d7-9545-b46903e3daf5.png	\N	image	skip_screenshot	user6	2025-09-05 07:19:24.934843
4f3b71e5-9525-4323-8089-4f5a25fcffe0	task13	930bd500-ab32-4786-9d53-236333f01b28.png	http://192.168.200.20:9000/medical-annotations/reviews/task13/930bd500-ab32-4786-9d53-236333f01b28.png	\N	image	review_screenshot	user1	2025-10-09 07:32:21.607343
bdb89f23-d6fd-4fe8-9e1f-80609cd35266	task13	930bd500-ab32-4786-9d53-236333f01b28.png	http://192.168.200.20:9000/medical-annotations/reviews/task13/930bd500-ab32-4786-9d53-236333f01b28.png	\N	image	review_screenshot	user1	2025-10-09 07:32:21.704358
9768e610-ea15-497b-a2e0-87c2df7760ff	303e3b52-370c-4d52-87ec-1cf8633f8665	8e57b4f2-9241-4541-b3de-cf178846a335.png	http://192.168.200.20:9000/medical-annotations/annotations/303e3b52-370c-4d52-87ec-1cf8633f8665/8e57b4f2-9241-4541-b3de-cf178846a335.png	\N	image	annotation_screenshot	user1	2025-10-09 07:33:12.612746
d6cacd76-46a6-40f8-a6b3-bdb44e9f6195	74afdca6-5b80-401e-acd2-5716a21a6663	92263bb3-892c-4fac-be1d-ef88f38ed4c2.png	http://192.168.200.20:9000/medical-annotations/annotations/74afdca6-5b80-401e-acd2-5716a21a6663/92263bb3-892c-4fac-be1d-ef88f38ed4c2.png	\N	image	annotation_screenshot	user1	2025-10-09 08:03:05.898435
9b984b0f-c9ec-4d43-88af-756d76c7d1ef	74afdca6-5b80-401e-acd2-5716a21a6663	1ee18443-6d31-4f7e-86a1-5f78accead20.png	http://192.168.200.20:9000/medical-annotations/reviews/74afdca6-5b80-401e-acd2-5716a21a6663/1ee18443-6d31-4f7e-86a1-5f78accead20.png	\N	image	review_screenshot	user1	2025-10-09 08:03:59.248549
2cd1719e-86ba-4475-b9cc-5cb410318cfe	74afdca6-5b80-401e-acd2-5716a21a6663	1ee18443-6d31-4f7e-86a1-5f78accead20.png	http://192.168.200.20:9000/medical-annotations/reviews/74afdca6-5b80-401e-acd2-5716a21a6663/1ee18443-6d31-4f7e-86a1-5f78accead20.png	\N	image	review_screenshot	user1	2025-10-09 08:03:59.337666
168ba71d-8ddc-457b-8587-8182d1f8050d	74afdca6-5b80-401e-acd2-5716a21a6663	62236b4f-22f4-4686-98a9-008783f16fc5.png	http://192.168.200.20:9000/medical-annotations/annotations/74afdca6-5b80-401e-acd2-5716a21a6663/62236b4f-22f4-4686-98a9-008783f16fc5.png	\N	image	annotation_screenshot	user1	2025-10-09 08:04:26.409142
3490565e-a8a0-41b6-b378-0b878b014bcb	d4b4b038-9bbb-4937-a2fb-31ebcf55e9ba	82574ec1-117c-4362-a8d7-205d6621a186.png	http://192.168.200.20:9000/medical-annotations/annotations/d4b4b038-9bbb-4937-a2fb-31ebcf55e9ba/82574ec1-117c-4362-a8d7-205d6621a186.png	\N	image	annotation_screenshot	user1	2025-10-09 08:19:46.525904
9f60ab1a-8d46-4ea5-8ef8-a9bd982c27f0	90a4d30e-4d50-4543-adee-9932bca548d6	a5b2f7a4-1b93-4cec-b6d7-503157c43f41.png	http://192.168.200.20:9000/medical-annotations/reviews/90a4d30e-4d50-4543-adee-9932bca548d6/a5b2f7a4-1b93-4cec-b6d7-503157c43f41.png	\N	image	review_screenshot	user1	2025-10-09 08:25:06.806953
997056ce-02e8-45fe-ab82-9d26bbd63f56	90a4d30e-4d50-4543-adee-9932bca548d6	a5b2f7a4-1b93-4cec-b6d7-503157c43f41.png	http://192.168.200.20:9000/medical-annotations/reviews/90a4d30e-4d50-4543-adee-9932bca548d6/a5b2f7a4-1b93-4cec-b6d7-503157c43f41.png	\N	image	review_screenshot	user1	2025-10-09 08:25:06.918491
a25f6020-fe0a-40f4-a72a-cebeb8910a61	90a4d30e-4d50-4543-adee-9932bca548d6	dd0588d4-806a-46e1-9cc4-c933a28022ae.png	http://192.168.200.20:9000/medical-annotations/annotations/90a4d30e-4d50-4543-adee-9932bca548d6/dd0588d4-806a-46e1-9cc4-c933a28022ae.png	\N	image	annotation_screenshot	user1	2025-10-09 08:31:01.488372
e7d7e71d-d7a7-4f40-a868-8b0e065e43b5	b16ed336-68e4-4045-9dff-cf44a734f77d	0bdf0711-e20c-48bc-abc7-6726cf87a42b.png	http://192.168.200.20:9000/medical-annotations/reviews/b16ed336-68e4-4045-9dff-cf44a734f77d/0bdf0711-e20c-48bc-abc7-6726cf87a42b.png	\N	image	skip_screenshot	user1	2025-10-09 08:32:50.394014
49cd7539-820c-4f3a-9841-489c0010fdc3	4644fae1-f896-4123-829b-cea7692bc664	5d3c2352-0297-47d7-9b66-11e090cf1aac.png	http://192.168.200.20:9000/medical-annotations/reviews/4644fae1-f896-4123-829b-cea7692bc664/5d3c2352-0297-47d7-9b66-11e090cf1aac.png	\N	image	skip_screenshot	user1	2025-10-09 09:00:57.121848
edc8dc25-5803-476d-adbb-05005543ac61	d4b4b038-9bbb-4937-a2fb-31ebcf55e9ba	468432f7-9fbd-48f7-a4a5-4507062c7c8c.png	http://192.168.200.20:9000/medical-annotations/reviews/d4b4b038-9bbb-4937-a2fb-31ebcf55e9ba/468432f7-9fbd-48f7-a4a5-4507062c7c8c.png	\N	image	review_screenshot	user1	2025-10-09 09:17:02.834683
199d8918-4e5f-4c40-a1c0-8e6c4cd42cbb	d4b4b038-9bbb-4937-a2fb-31ebcf55e9ba	468432f7-9fbd-48f7-a4a5-4507062c7c8c.png	http://192.168.200.20:9000/medical-annotations/reviews/d4b4b038-9bbb-4937-a2fb-31ebcf55e9ba/468432f7-9fbd-48f7-a4a5-4507062c7c8c.png	\N	image	review_screenshot	user1	2025-10-09 09:17:02.924152
f9b40bee-4bf3-4896-8c13-d17791051cc5	b16ed336-68e4-4045-9dff-cf44a734f77d	dcccdb3f-caea-48fb-9e6b-263e36fe49d9.png	http://192.168.200.20:9000/medical-annotations/reviews/b16ed336-68e4-4045-9dff-cf44a734f77d/dcccdb3f-caea-48fb-9e6b-263e36fe49d9.png	\N	image	skip_screenshot	user1	2025-10-09 09:17:53.652814
e3f423af-6c13-4fdf-982a-be81fafd78a2	303e3b52-370c-4d52-87ec-1cf8633f8665	fe4a77f9-929a-466a-a4b7-cd828eea0165.png	http://192.168.200.20:9000/medical-annotations/reviews/303e3b52-370c-4d52-87ec-1cf8633f8665/fe4a77f9-929a-466a-a4b7-cd828eea0165.png	\N	image	review_screenshot	user1	2025-10-09 09:24:32.660664
bac9e918-cc5d-42c9-86cb-8e5dd188c3b1	303e3b52-370c-4d52-87ec-1cf8633f8665	fe4a77f9-929a-466a-a4b7-cd828eea0165.png	http://192.168.200.20:9000/medical-annotations/reviews/303e3b52-370c-4d52-87ec-1cf8633f8665/fe4a77f9-929a-466a-a4b7-cd828eea0165.png	\N	image	review_screenshot	user1	2025-10-09 09:24:32.767891
39e113e1-94dd-4b61-b410-6721c6d4b7bf	d4b4b038-9bbb-4937-a2fb-31ebcf55e9ba	53ee3e81-30e7-4982-97b4-6c374999c893.png	http://192.168.200.20:9000/medical-annotations/annotations/d4b4b038-9bbb-4937-a2fb-31ebcf55e9ba/53ee3e81-30e7-4982-97b4-6c374999c893.png	\N	image	annotation_screenshot	user1	2025-10-09 09:25:13.010978
db3d3d47-bd78-4c57-b865-7ad000c0e522	abee54a1-08c4-481f-b767-43843b323f7d	a059a6e1-b10e-4561-a71e-afe9e89a8485.png	http://192.168.200.20:9000/medical-annotations/annotations/abee54a1-08c4-481f-b767-43843b323f7d/a059a6e1-b10e-4561-a71e-afe9e89a8485.png	\N	image	annotation_screenshot	user1	2025-10-09 09:26:12.787983
178e214a-e689-4578-adba-ab91981bd939	d392e9d3-cc8c-4e26-bdc7-a8e1585e95b5	8ccf100b-6055-42ce-ad2e-7b645a53db40.png	http://192.168.200.20:9000/medical-annotations/annotations/d392e9d3-cc8c-4e26-bdc7-a8e1585e95b5/8ccf100b-6055-42ce-ad2e-7b645a53db40.png	\N	image	annotation_screenshot	user1	2025-10-09 09:27:11.706332
4e62c6ad-f5e3-46bf-b41c-421d092b1cc8	4e7d4687-bf61-4579-b9a7-6a6c19243811	278e0665-0cc8-4a09-bb9b-f5e6ff0f6266.png	http://192.168.200.20:9000/medical-annotations/reviews/4e7d4687-bf61-4579-b9a7-6a6c19243811/278e0665-0cc8-4a09-bb9b-f5e6ff0f6266.png	\N	image	review_screenshot	user6	2025-10-10 02:43:11.462104
44c374a3-ef63-42e6-a26b-fa888986940d	4e7d4687-bf61-4579-b9a7-6a6c19243811	278e0665-0cc8-4a09-bb9b-f5e6ff0f6266.png	http://192.168.200.20:9000/medical-annotations/reviews/4e7d4687-bf61-4579-b9a7-6a6c19243811/278e0665-0cc8-4a09-bb9b-f5e6ff0f6266.png	\N	image	review_screenshot	user6	2025-10-10 02:43:11.556588
ce931de7-13d0-4c48-907d-79dd4f153024	53a17e38-5888-4f3e-a8ab-cc2add73f137	8d2af3d2-3664-48d2-8cfa-c815a24533c8.png	http://192.168.200.20:9000/medical-annotations/reviews/53a17e38-5888-4f3e-a8ab-cc2add73f137/8d2af3d2-3664-48d2-8cfa-c815a24533c8.png	\N	image	skip_screenshot	user8	2025-10-10 02:47:16.96392
ef1bf538-50c0-4290-a9b3-cf6c93a29534	53a17e38-5888-4f3e-a8ab-cc2add73f137	08b9b934-fe18-4e8b-829d-4e2643e59370.png	http://192.168.200.20:9000/medical-annotations/reviews/53a17e38-5888-4f3e-a8ab-cc2add73f137/08b9b934-fe18-4e8b-829d-4e2643e59370.png	\N	image	skip_screenshot	user8	2025-10-10 02:48:16.918242
b1c5480b-d540-4d83-94b3-7fe568107b03	5743c3fb-5c58-4cac-b802-40709a1ec1db	345a5c4a-b381-491a-9f87-4f1e5426bd3b.png	http://192.168.200.20:9000/medical-annotations/reviews/5743c3fb-5c58-4cac-b802-40709a1ec1db/345a5c4a-b381-491a-9f87-4f1e5426bd3b.png	\N	image	review_screenshot	user6	2025-10-10 03:16:10.017545
0e42d1a0-a225-4953-b453-bc593199c912	5743c3fb-5c58-4cac-b802-40709a1ec1db	345a5c4a-b381-491a-9f87-4f1e5426bd3b.png	http://192.168.200.20:9000/medical-annotations/reviews/5743c3fb-5c58-4cac-b802-40709a1ec1db/345a5c4a-b381-491a-9f87-4f1e5426bd3b.png	\N	image	review_screenshot	user6	2025-10-10 03:16:10.090554
e3d0eb0e-3af4-4abc-aef0-d198c518de93	16146129-de9a-4f16-a0a0-76f774183ea8	5906c636-1627-4bac-b39d-39431cb53781.png	http://localhost:9000/medical-annotations/annotations/16146129-de9a-4f16-a0a0-76f774183ea8/5906c636-1627-4bac-b39d-39431cb53781.png	\N	image	annotation_screenshot	user1	2025-09-02 09:08:09.201624
2e423d4c-84ee-4078-a184-4a8b1fe067cf	16146129-de9a-4f16-a0a0-76f774183ea8	e7865657-a40b-4dd1-b377-d3ec56ba68cf.png	http://localhost:9000/medical-annotations/annotations/16146129-de9a-4f16-a0a0-76f774183ea8/e7865657-a40b-4dd1-b377-d3ec56ba68cf.png	\N	image	annotation_screenshot	user1	2025-09-02 09:09:43.628312
1c4373aa-80f2-4779-a507-80e039d4f44a	d4b4b038-9bbb-4937-a2fb-31ebcf55e9ba	cba8c6d1-5a69-419b-966d-baa5de6f6d8e.png	http://192.168.200.20:9000/medical-annotations/annotations/d4b4b038-9bbb-4937-a2fb-31ebcf55e9ba/cba8c6d1-5a69-419b-966d-baa5de6f6d8e.png	\N	image	annotation_screenshot	user1	2025-10-17 08:12:40.153568
2637a537-8858-4c95-85a0-ddd89e8b303e	187505fa-49e5-4bcc-b6e5-6a7343a5b52c	0c333f6e-b5ab-4778-a9d2-ea3e16a6994e.png	http://192.168.200.20:9000/medical-annotations/annotations/187505fa-49e5-4bcc-b6e5-6a7343a5b52c/0c333f6e-b5ab-4778-a9d2-ea3e16a6994e.png	\N	image	annotation_screenshot	user1	2025-10-17 08:12:49.998503
\.


--
-- TOC entry 3640 (class 0 OID 24961)
-- Dependencies: 227
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.tasks (id, title, description, project_id, status, priority, assigned_to, created_by, image_url, annotation_data, score, assigned_at, submitted_at, reviewed_by, reviewed_at, review_comment, created_at, updated_at, timeline, skipped_at, skip_reason, skip_images, assigned_to_name, created_by_name, reviewed_by_name, skip_requested_at, skip_request_reason, skip_request_images, skip_requested_by, skip_reviewed_at, skip_reviewed_by, skip_review_comment) FROM stdin;
de35f565-a0c4-4b3f-bad5-a01a2ee780b0	JiaMin	2025第四次泌尿标注任务	proj2025301	approved	medium	user6	user1	E:/训练留档/泌尿导出/JiaMin	{"comment": "\\u5b8c\\u7f8e\\u6807\\u6ce8\\uff0c\\u4f60\\u5c31\\u5b66\\u5427\\u5c31", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-09-04T02:15:34.004Z", "screenshot_count": 0}	5	2025-09-04 10:15:23.526434	2025-09-04 10:15:34.017019	user6	2025-09-04 10:15:59.769505	完美标注，你就学吧就	2025-09-04 02:13:24.321151	2025-09-04 02:15:59.768844	[{"time": "2025-09-04T10:15:23.526434", "type": "claimed", "user_id": "user6", "user_name": "代雨昕"}, {"time": "2025-09-04T10:15:34.017019", "type": "submitted", "comment": "完美标注，你就学吧就", "user_id": "user6", "user_name": "代雨昕", "organ_count": 1}, {"time": "2025-09-04T10:15:59.769505", "type": "reviewed", "score": 5, "action": "approve", "comment": "完美标注，你就学吧就", "user_id": "user6", "user_name": "代雨昕"}]	\N	\N	\N	代雨昕	\N	代雨昕	\N	\N	\N	\N	\N	\N	\N
04e2933d-acdd-4496-bf9b-a25d51a8132e	KongTengteng	2025第四次泌尿标注任务	proj2025301	approved	medium	user1	user1	E:/训练留档/泌尿导出/KongTengteng	{"comment": "\\u5b89\\u629a\\u6211\\u6211\\u7a81\\u7136\\u6390\\u5934\\u53bb\\u5c3e\\u5929\\u6c14\\u95ee\\u9898\\u542c\\u4e0d\\u6e05\\u4e8c\\u4f4d\\u7279\\u59d4\\u5c48\\u7238\\u7238\\u53bb\\u542c\\u542c", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-09T09:31:52.785Z", "screenshot_count": 0}	5	2025-10-09 17:31:23.186431	2025-10-09 17:31:52.797002	user6	2025-10-10 10:32:19.035812	  ，免费的武器	2025-09-04 02:13:24.321151	2025-10-10 02:32:19.046241	[{"time": "2025-10-09T17:31:23.186431", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T17:31:52.797002", "type": "submitted", "comment": "安抚我我突然掐头去尾天气问题听不清二位特委屈爸爸去听听", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-10T10:32:19.035812", "type": "reviewed", "score": 5, "action": "approve", "comment": "  ，免费的武器", "user_id": "user6", "user_name": "代雨昕"}]	\N	\N	\N	系统管理员	\N	代雨昕	\N	\N	\N	\N	\N	\N	\N
35baef21-fd15-4b82-8552-6d2402488a07	HuZhongying	2025第四次泌尿标注任务	proj2025301	approved	medium	user6	user1	E:/训练留档/泌尿导出/HuZhongying	{"comment": "\\u5b8c\\u7f8e\\u6807\\u6ce8\\uff0c\\u4f60\\u5c31\\u5b66\\u5427\\u5c31", "organ_count": 3, "uploaded_images": [], "timestamp": "2025-09-04T02:14:25.508Z", "screenshot_count": 0}	5	2025-09-04 10:14:02.073068	2025-09-04 10:14:25.521429	user6	2025-09-04 10:14:43.672762	还行	2025-09-04 02:13:24.321151	2025-09-04 02:14:43.663751	[{"time": "2025-09-04T10:14:02.073068", "type": "claimed", "user_id": "user6", "user_name": "代雨昕"}, {"time": "2025-09-04T10:14:25.521429", "type": "submitted", "comment": "完美标注，你就学吧就", "user_id": "user6", "user_name": "代雨昕", "organ_count": 1}, {"time": "2025-09-04T10:14:43.672762", "type": "reviewed", "score": 5, "action": "approve", "comment": "还行", "user_id": "user6", "user_name": "代雨昕"}]	\N	\N	\N	代雨昕	\N	代雨昕	\N	\N	\N	\N	\N	\N	\N
e1df49f7-e103-472c-b1b0-0731de2a736d	JiaChunling	2025第四次泌尿标注任务	proj2025301	approved	medium	user6	user1	E:/训练留档/泌尿导出/JiaChunling	{"comment": "\\u5b8c\\u7f8e\\u6807\\u6ce8\\uff0c\\u4f60\\u5c31\\u5b66\\u5427\\u5c31", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-09-04T02:15:38.108Z", "screenshot_count": 0}	5	2025-09-04 10:15:17.885759	2025-09-04 10:15:38.118726	user6	2025-09-04 10:16:03.399399	完美标注，你就学吧就	2025-09-04 02:13:24.321151	2025-09-04 02:16:03.3946	[{"time": "2025-09-04T10:15:17.885759", "type": "claimed", "user_id": "user6", "user_name": "代雨昕"}, {"time": "2025-09-04T10:15:38.118726", "type": "submitted", "comment": "完美标注，你就学吧就", "user_id": "user6", "user_name": "代雨昕", "organ_count": 1}, {"time": "2025-09-04T10:16:03.399399", "type": "reviewed", "score": 5, "action": "approve", "comment": "完美标注，你就学吧就", "user_id": "user6", "user_name": "代雨昕"}]	\N	\N	\N	代雨昕	\N	代雨昕	\N	\N	\N	\N	\N	\N	\N
2161e972-ac9c-4f2a-bee3-44407c04a877	陈春德	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	skipped	high	\N	user1	D:/任务管理测试数据/肝脏/陈春德	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-03 07:50:24.89077	[{"time": "2025-09-03T15:50:24.891908", "type": "skipped", "images": ["http://localhost:9000/medical-annotations/reviews/2161e972-ac9c-4f2a-bee3-44407c04a877/5f57d716-ea8c-4ba1-a05b-68eda1cc32a5.png"], "reason": "啥数据，反省一下", "user_id": "user1", "user_name": "系统管理员"}]	2025-09-03 15:50:24.891908	啥数据，反省一下	["http://localhost:9000/medical-annotations/reviews/2161e972-ac9c-4f2a-bee3-44407c04a877/5f57d716-ea8c-4ba1-a05b-68eda1cc32a5.png"]	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
70f70b61-4ca9-4760-90dc-19f2c3f669a4	BaiYulu	2025第四次泌尿标注任务	proj2025301	approved	medium	user1	user1	E:/训练留档/泌尿导出/BaiYulu	{"comment": "asdfafwqtgqwdasfqwrqwfaf", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-09T09:40:49.071Z", "screenshot_count": 0}	5	2025-10-09 17:40:37.081596	2025-10-09 17:40:49.084269	user6	2025-10-10 10:32:29.883339	多牛逼	2025-09-04 02:13:24.321151	2025-10-10 02:32:29.941253	[{"time": "2025-10-09T17:40:37.081596", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T17:40:49.084269", "type": "submitted", "comment": "asdfafwqtgqwdasfqwrqwfaf", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-10T10:32:29.883339", "type": "reviewed", "score": 5, "action": "approve", "comment": "多牛逼", "user_id": "user6", "user_name": "代雨昕"}]	\N	\N	\N	系统管理员	\N	代雨昕	\N	\N	\N	\N	\N	\N	\N
bb48eadd-47fc-4328-9778-4c6ee21284d7	程第灿	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
af2dcd6f-bf19-4e85-b32d-a9d20f53e610	王庭珍	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
64b8d579-ac76-4a14-99f9-d2f8affbbb65	杜启学	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/杜启学	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
6d2da6ad-8bbb-4998-bb4a-b9d6a646fa71	张孝良	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/张孝良	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
72741ddd-4d98-4fdf-8b9a-c2e336a0ef82	陈昌	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/陈昌	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
7a7a5955-ad90-472a-b701-80a93a2bea90	郑安学	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/郑安学	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
8069fe40-711a-48a8-b839-ed479da50f5d	周训跃	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/周训跃	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
81a1ea3f-d785-4d5a-b066-9c0b694170d3	李朝云	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/李朝云	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
85ba2797-92b3-4556-8ea1-1ec8a5c9fe69	吴光高	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/吴光高	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
8ba080ad-a81a-4a18-8858-1d75b9a0dc80	周文荣	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/周文荣	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
95d4caea-6e6b-43ab-b53d-af05e0f194ca	夏建国	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/夏建国	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
98771a22-0192-4433-a222-ca6bfe8a2d92	陆显照	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/陆显照	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
9ae02d64-327d-46bc-b9c0-7918f91c9561	郭长安	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/郭长安	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
ba01586c-49ff-41f2-b841-2689f882db58	沈春容	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
40f7edf5-cf05-4b3a-8840-61b08882ca6c	车镇远	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	approved	high	user1	user1	D:/任务管理测试数据/肝脏/车镇远	{"comment": "\\u7684\\u9760\\u8fd1\\u548c\\u52a8\\u7269\\u548c\\u524d\\u540e\\u5bf9\\u6bd4\\u6765\\u770b\\u8bf7\\u95ee\\u4f60\\u6211\\u5f97", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-10T01:07:46.844Z", "screenshot_count": 0}	5	2025-10-10 09:07:34.206615	2025-10-10 09:07:46.863131	user1	2025-10-17 14:32:25.634584		2025-09-02 06:39:58.916713	2025-10-17 06:32:25.600467	[{"time": "2025-10-10T09:07:34.206615", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-10T09:07:46.863131", "type": "submitted", "comment": "的靠近和动物和前后对比来看请问你我得", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-17T14:32:25.634584", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	系统管理员	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
9c28e30d-176b-4a33-9701-d5194fffbcee	罗祥素	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/罗祥素	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
9e1f1616-f5ad-4433-9a46-8d3c8155cb56	朱克进	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/朱克进	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
afd6e664-cb20-4d59-8c01-fada8a1f42f3	张天炼	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/张天炼	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
b30784ef-27d9-4a4e-8534-096fa35d4b0c	张天虎	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/张天虎	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
c6953480-6de8-4e13-ac4f-ccd472522560	任忆宸	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/任忆宸	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
19700c12-e320-48de-a4c4-4dbf04f35412	陆显照	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
49066da6-57d9-4483-96df-6322a3825368	沈春容	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	approved	high	user8	user1	D:/任务管理测试数据/肝脏/沈春容	{"comment": "dawdwartqwtqwtqawdasgf", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-10T02:36:36.762Z", "screenshot_count": 0}	5	2025-10-10 10:36:26.618343	2025-10-10 10:36:36.771847	user6	2025-10-10 10:36:47.859386	打完后而后期	2025-09-02 06:39:58.916713	2025-10-10 02:36:47.854712	[{"time": "2025-10-10T10:36:26.618343", "type": "claimed", "user_id": "user8", "user_name": "王欢欢"}, {"time": "2025-10-10T10:36:36.771847", "type": "submitted", "comment": "dawdwartqwtqwtqawdasgf", "user_id": "user8", "user_name": "王欢欢", "organ_count": 1}, {"time": "2025-10-10T10:36:47.859386", "type": "reviewed", "score": 5, "action": "approve", "comment": "打完后而后期", "user_id": "user6", "user_name": "代雨昕"}]	\N	\N	\N	王欢欢	系统管理员	代雨昕	\N	\N	\N	\N	\N	\N	\N
c97c3b8c-3f3f-44d5-96d7-f0cf4262dc2c	程第灿	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/程第灿	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
cc0bccda-cb5a-4513-b00a-2352fd47bb47	孙平	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/孙平	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
ccc6a973-d7a9-412a-afe5-537251c7976d	王庭珍	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/王庭珍	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
d71bed96-a9e6-4e6d-946b-88284a145203	蒋明俊	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/蒋明俊	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
dcdd5696-b518-4ee1-a7e3-2fe1ac45b4ac	于春国	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/于春国	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
eb31838b-bb40-4be7-9072-50e73b761b73	刘永林	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/刘永林	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
ef6bed93-fbc4-4d98-a140-c730f954ed49	郑君	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/郑君	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
f1aee405-a69d-4f8b-9cf9-a48b0056811e	仇德银	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/仇德银	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
f327c3d2-b637-4f56-867e-402197ced2ab	刘成慧	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/刘成慧	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
f5b60537-c04f-420e-8731-59745e401997	聂义	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/聂义	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
19f54030-101a-42ad-98b3-1ab4c80e8712	BianHongyi	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/BianHongyi	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a6a03ab2-7ea3-4fa7-aa3c-8a6e66d551c2	BiXinxi	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/BiXinxi	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2bfbfb55-bc22-4c57-835a-9466becbdc21	CaiGe	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/CaiGe	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
6fe221b2-312f-42dc-8985-85e42865f8a1	CaoCuihong	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/CaoCuihong	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4a1ee3b6-14c6-4405-8814-3d0bfdb6abd2	CaoLili	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/CaoLili	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b73c18c1-20be-4946-aaed-46e03101e0b6	ChaoXiangying	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/ChaoXiangying	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
463be5d3-b139-4c07-9500-9ef5b4f77bbf	杜启学	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
de2b89a8-6e44-4568-bbf8-01dc94d80218	ChenJianchun	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/ChenJianchun	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
f9f56444-b179-42f1-bc6d-7ea13f510039	李叶	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/李叶	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
fa92c509-a9c9-4019-a870-451bd6d691a9	陈仕书	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	pending	high	\N	user1	D:/任务管理测试数据/肝脏/陈仕书	{"estimated_hours": 2}	\N	\N	\N	\N	\N	\N	2025-09-02 06:39:58.916713	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
1f5d0a0d-19dc-4416-acbb-63d5532b475f	ChenJianli	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/ChenJianli	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
416e3692-fb0e-40f8-99af-095831fe4763	ChenJiazhu	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/ChenJiazhu	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4a652145-71bf-4b88-aa6e-494d393d147b	ChenJinxue	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/ChenJinxue	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
04c6f9b6-f0e8-45ef-ad7e-4f7f875eabf1	ChenPing	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/ChenPing	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9adcbb07-5844-425f-a1cd-4de1bab1acc4	ChenYanhua	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/ChenYanhua	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
709c46d0-f3f5-4f60-b5f9-4188646a4d6e	ChenYubing	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/ChenYubing	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7aa407bb-c582-4ad7-afec-d7e2bc5b4ed3	ChenZhongxin	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/ChenZhongxin	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
05c203bb-73ad-468a-b51a-d15e07f9851b	create	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/create	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0f5ab73d-77b1-4e83-8b01-488bf1d84c5b	CuiAnyuan	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/CuiAnyuan	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
ce70f212-ed50-4cab-ba6a-3136a70746e9	DingFenghui	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/DingFenghui	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
883e2158-ff44-40f5-9a42-0094d890dda5	DingJianchao	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/DingJianchao	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
eda5e108-67e3-4313-9fc0-4547bef6b5a5	DingJianming	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/DingJianming	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
323b219a-336e-4e9a-9df7-d593e087c83f	DongQiyin	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/DongQiyin	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b809996b-b89c-481a-b407-f76af30fb065	DuanYiguo	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/DuanYiguo	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b9a6c533-ad58-4dc7-8024-08a0c8038478	DuQinmin	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/DuQinmin	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
794f6c95-ac63-4b9c-9200-dec1faac8564	FanGuoming	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/FanGuoming	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
task14	肺炎X光片标注任务006	标注胸部X光片中的肺炎病变区域	proj2	pending	low	\N	user1	/api/images/chest006.jpg	\N	35	\N	\N	\N	\N	\N	2025-08-29 09:12:58.092482	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
task15	结核X光片标注任务007	标注胸部X光片中的结核病变区域	proj2	pending	low	\N	user1	/api/images/chest007.jpg	\N	30	\N	\N	\N	\N	\N	2025-08-29 09:12:58.092482	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
d111d74f-d867-4fbb-a826-7f48144afb9d	FeiShoulin	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/FeiShoulin	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
68321514-52d8-4077-bf2f-9fe12c8565ad	李朝云	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
task11	肿瘤X光片标注任务003	标注胸部X光片中的肿瘤病变区域	proj2	pending	high	\N	user1	/api/images/chest003.jpg	\N	70	\N	\N	\N	\N	\N	2025-08-29 09:12:58.092482	2025-10-16 07:01:16.184102	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
task1	肾脏CT标注任务001	标注左肾CT影像中的病变区域	proj1	approved	high	\N	user1	/api/images/kidney001.jpg	{"lesions": [{"x": 100, "y": 150, "type": "tumor"}]}	50	\N	2024-12-03 16:00:00	user1	2024-12-03 16:00:00	标注准确，质量良好	2025-08-29 09:12:58.092482	2025-10-16 07:12:54.918548	[{"time": "2024-12-01T09:00:00", "type": "created", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2024-12-02T10:30:00", "type": "claimed", "user_id": "user2", "user_name": "张医生"}, {"time": "2024-12-03T15:45:00", "type": "submitted", "comment": "已完成肾脏病变区域标注", "user_id": "user2", "user_name": "张医生", "organ_count": 1}, {"time": "2024-12-03T16:00:00", "type": "reviewed", "score": 5, "action": "approve", "comment": "标注准确，质量良好", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	张医生	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
8b9d6946-1535-48a2-a703-43a214a84c05	FengJichao	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/FengJichao	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
1dbf34ee-56d0-433c-836b-d8d4ce2ffbf5	FengJiyong	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/FengJiyong	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d0604f1a-e15e-45d3-9b05-cc9bc915e6e3	FengMinglin	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/FengMinglin	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
cd171589-89df-4eed-ab8a-ba1c632b580b	FengPuyun	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/FengPuyun	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
679acc7d-47f6-457f-8de2-f4250df58162	FuXiuying	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/FuXiuying	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
be81ffeb-1003-49d5-96c7-2ee216193066	GanZhisheng	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/GanZhisheng	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c9fc5fc2-d767-4cad-b815-244f9a049997	GaoXianyun	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/GaoXianyun	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
885d4276-2d91-4ef3-93d2-c4b44864e62a	GaoXixue	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/GaoXixue	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b522950c-125c-4a7d-8d3e-74a52a5eb4e5	GuanYuguo	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/GuanYuguo	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5b9d0650-27b5-40d1-a74b-4afbf5a249cd	GuoLianyan	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/GuoLianyan	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2cc03c48-e738-4ba2-8516-c33bca8e18aa	HeYelin	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/HeYelin	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d3a4a952-ac56-4272-bd79-55a8e164978f	HouGuiyun	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/HouGuiyun	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
task21	肾脏CT标注任务009-已跳过	示例：任务被跳过，提供跳过原因和截图	proj1	skipped	low	\N	user1	/api/images/kidney009.jpg	\N	\N	\N	\N	\N	\N	\N	2025-08-29 09:12:58.092482	2025-09-02 08:17:19.885746	[{"time": "2024-12-05T09:00:00", "type": "created", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2024-12-06T10:00:00", "type": "skipped", "images": ["http://minio.local/bucket/skip_001.jpg"], "reason": "影像质量不达标，无法标注", "user_id": "user1", "user_name": "系统管理员"}]	2024-12-06 10:00:00	影像质量不达标，无法标注	["http://minio.local/bucket/skip_001.jpg"]	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
task5	膀胱CT标注任务005	标注膀胱CT影像中的肿瘤区域	proj1	pending	high	\N	user1	/api/images/bladder005.jpg	\N	55	\N	\N	\N	\N	\N	2025-08-29 09:12:58.092482	2025-09-02 08:17:19.885746	[{"time": "2024-12-01T10:15:00", "type": "created", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
task6	输尿管CT标注任务006	标注输尿管CT影像中的结石区域	proj1	pending	medium	\N	user1	/api/images/ureter006.jpg	\N	40	\N	\N	\N	\N	\N	2025-08-29 09:12:58.092482	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
task7	肾脏CT标注任务007	标注左肾CT影像中的感染区域	proj1	pending	low	\N	user1	/api/images/kidney007.jpg	\N	35	\N	\N	\N	\N	\N	2025-08-29 09:12:58.092482	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
task8	膀胱CT标注任务008	标注膀胱CT影像中的炎症区域	proj1	pending	low	\N	user1	/api/images/bladder008.jpg	\N	30	\N	\N	\N	\N	\N	2025-08-29 09:12:58.092482	2025-09-02 08:17:19.885746	[]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
task16	脑肿瘤MRI标注任务001	标注脑部MRI影像中的肿瘤区域	proj3	approved	high	\N	user1	/api/images/brain001.jpg	{"lesions": [{"x": 100, "y": 100, "type": "tumor"}]}	80	\N	2024-12-12 17:00:00	user1	2024-12-12 17:00:00	标注精确，质量优秀	2025-08-29 09:12:58.092482	2025-10-16 07:01:16.184102	[]	\N	\N	\N	王医生	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
task2	膀胱CT标注任务002	标注膀胱CT影像中的异常区域	proj1	approved	medium	\N	user1	/api/images/bladder002.jpg	{"lesions": [{"x": 200, "y": 180, "type": "stone"}]}	40	\N	2024-12-04 14:30:00	user1	2024-12-04 14:30:00	标注正确	2025-08-29 09:12:58.092482	2025-10-16 07:12:54.918548	[{"time": "2024-12-01T09:15:00", "type": "created", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2024-12-02T11:00:00", "type": "claimed", "user_id": "user2", "user_name": "张医生"}, {"time": "2024-12-04T14:15:00", "type": "submitted", "comment": "已完成膀胱结石标注", "user_id": "user2", "user_name": "张医生", "organ_count": 1}, {"time": "2024-12-04T14:30:00", "type": "reviewed", "score": 4, "action": "approve", "comment": "标注正确", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	张医生	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
da5801f8-3f8d-4140-b771-6f437c8046c5	HouXinyu	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/HouXinyu	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
8cb58072-d56b-4130-91ab-6d0d8da0c5d8	HouYanzhang	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/HouYanzhang	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c2ec6146-f391-4543-af4a-34a331446bf5	HuangfuGongjian	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/HuangfuGongjian	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
bf003efc-c5c6-47fb-a699-12487092c300	HuangSongsheng	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/HuangSongsheng	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4143d3c2-b54f-466a-a105-c34ce73fa52c	HuangYuli	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/HuangYuli	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a1b13565-9ef1-4f60-89d7-2b8df2a23d2d	HuKezhen	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/HuKezhen	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
cc2af3f1-47e4-4dea-a205-fd5f114ffbfb	HuQingzhong	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/HuQingzhong	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d214662d-1024-4d55-99d9-a94e6fc88e53	郭长安	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c7b581a2-7a88-43c5-9227-eec66ac858fe	郑小明	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5b944084-d91f-43ec-a02c-7cf9248c0124	郑安学	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c4702c58-92e2-4a7a-a5c0-0b06dc91f0d1	郑君	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4eeab9f4-9a27-4b04-bf78-26118258b98f	LiangHaidong	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiangHaidong	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5bb8ff42-7cc0-4e02-bd32-ef6ac02581ad	LiangLicun	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiangLicun	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
185e830c-4692-41d8-b8e1-84366204a672	LiCanglong	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiCanglong	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d5b8edd0-6ffe-44a5-930f-8d450cc771c3	LiChunqing	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiChunqing	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
da61fa4f-e164-41d8-991d-cfd42bf103d7	LiDesheng	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiDesheng	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
742e79d5-110a-490e-b083-5f51d270168d	LiFengqin	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiFengqin	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0834ddd2-23ab-4152-af7a-58b8c078c168	LiJing	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiJing	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d8301840-5043-4698-a4f5-112802619a31	LiLizhen	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiLizhen	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
f70b6150-0243-448b-9886-15bb97ad6676	LiMinghe	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiMinghe	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c32acbd7-d9bb-49d6-a97c-8bf12016f32e	LiShaoqiang	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiShaoqiang	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0c23950d-3b1f-4dac-b177-8249458afc51	LiShiqiang	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiShiqiang	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
37e1a447-500c-4e52-bac3-d8e200d313ff	LiShuo	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiShuo	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
f6d46fb3-36b5-43e2-b4ed-59d4876abbbe	LiuBaoquan	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiuBaoquan	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
91a433c0-928f-4633-8be5-e5c1ba32bd9b	LiuFuying	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiuFuying	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7c9ff599-5b83-4fbf-adf1-ef89d96c6463	LiuGuoqiang	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiuGuoqiang	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c00c7455-7d5e-4fe4-878b-ac858e2f93ed	LiuGuoxia	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiuGuoxia	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
99aa618b-92c6-4c4b-8080-29da2e7a345d	LiuHeng	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiuHeng	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
f6959c44-8251-481d-bcc0-46d881ab34a1	LiuHongying	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiuHongying	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c86257e5-5354-4bb9-b8e6-e56c0304a40d	LiuHuixing	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiuHuixing	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5a35a27f-0d5b-4107-8b0e-b3bc979157c7	LiuPengyue	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiuPengyue	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b2a3706f-e552-4986-bfec-0af406963365	LiuQiaoling	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiuQiaoling	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
425b99c6-567e-4e4c-b9db-14396985a8ef	LiuRenxiu	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiuRenxiu	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
02013e18-b5b2-4ce3-8101-1b7b2c1dc58f	LiuWei	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiuWei	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9813487f-1be6-4c9e-9e57-b9bc46567830	LiuWeidong	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiuWeidong	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
886c7473-3392-49dc-82cd-b8e981c93970	LiuYuecheng	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiuYuecheng	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d100fd1f-1bd3-4905-aa72-73070edc18c8	LiuYuhai	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiuYuhai	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
01e03155-432e-4573-a41a-caefc50b3b22	LiWenkai	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiWenkai	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
64795fd7-0d72-4243-85c0-1fb297373d8a	LiXinxiang	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiXinxiang	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3be922a4-562d-4adf-b1b1-8ab3db1326de	LiXiumei	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiXiumei	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9fa2f7e5-69da-4f06-b3ca-2c51e8fb2f8e	LiYouliang	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiYouliang	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2a61591d-8e94-4319-bbbe-83b0683fa850	LiYuanxin	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiYuanxin	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7d3d02d7-c723-4aa8-ab8b-3c3c8d92d255	LiYuxiang	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiYuxiang	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5b90907c-7bde-486a-bd90-5d5a3a199c9d	LiZhujun	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiZhujun	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
296ddf9d-1010-4ce2-8963-15137ba14cdf	LiZhuxue	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiZhuxue	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5b70538b-e656-418d-bff7-5f83d6ea9f44	LiZuntian	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LiZuntian	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
6d1fe99b-34e6-49ce-92e6-42889da57add	LuFengying	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LuFengying	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
23771182-8ee5-4f09-b87e-96ad8e8ae14c	LuZhidong	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LuZhidong	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c54a61c2-2ec1-43be-96c8-6410ecf52636	LvYaotian	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LvYaotian	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0bb9fb0b-cc72-4562-b897-bc165b8ed689	LvYujin	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/LvYujin	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7ae546ac-fdd7-40f7-8e7f-2d636598d792	MaDezhong	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/MaDezhong	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
e2e08a9c-ab1b-47c7-8ad9-d0ce84acd7b1	MaJuanjuan	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/MaJuanjuan	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
96c47640-31ee-47f9-ace4-3300f27c919b	MaoBin	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/MaoBin	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
60e670c5-fc55-4475-9100-76e556d0a6ed	MaShuhua	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/MaShuhua	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
59b994c3-c030-4935-a7f6-4dc73dde251a	MengFanbin	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/MengFanbin	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
acd3cac6-b81d-4c8b-9564-a31a1d5246fa	MengFankai	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/MengFankai	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0faa00ac-1a62-4a80-8f1e-8b44678fcae3	MengLingqiang	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/MengLingqiang	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
86bb84ae-d6c2-4dcf-9248-54b8b7b3a96b	MengYanting	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/MengYanting	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c7dd4e12-4049-4fdb-bd95-c87d18d31818	NiuXiaojuan	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/NiuXiaojuan	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
551cc30d-926c-4f9c-a3cb-b4cb4c0ad6e1	PangXuejun	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/PangXuejun	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
26a5f2c6-78d9-443a-9ba9-97a26b97a3f8	PangYutang	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/PangYutang	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9725b8e3-30f5-40f6-bfad-f3f6973e824f	QiDexiang	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/QiDexiang	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
db83f47d-169e-486b-9e08-79402202640d	QiHaiyun	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/QiHaiyun	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9b5362c5-607c-42a1-b52a-094ac6d3d4ba	QinShouzhao	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/QinShouzhao	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d9f57adc-645c-49a4-9155-1e8d9bb09811	QiuZhongren	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/QiuZhongren	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
763d2dce-9c2e-43e9-ab3f-bbbe4dadd3e5	QuQinghua	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/QuQinghua	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
f3485408-1e72-47bc-ad07-c15544b93f0a	RenFengli	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/RenFengli	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
303d367a-b095-4cd5-bacf-2a8e81ebfba4	RenGuiping ct	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/RenGuiping ct	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
91ac249e-6c4e-47bc-8ae4-54ed3b67306c	RenYan	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/RenYan	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
41770198-6ff9-4fb3-af02-cb9fcec8431f	ShangChunyang	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/ShangChunyang	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2c75f2fd-77c0-4296-8325-76febf3051ac	SongGuiying	2025第四次泌尿标注任务	proj2025301	pending	medium	\N	user1	E:/训练留档/泌尿导出/SongGuiying	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-09-04 02:13:24.321151	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d30b917d-b021-4a88-ad24-8ae692b64272	JiangShumei	2025第四次泌尿标注任务	proj2025301	approved	medium	user6	user1	E:/训练留档/泌尿导出/JiangShumei	{"comment": "\\u5b8c\\u7f8e\\u6807\\u6ce8\\uff0c\\u4f60\\u5c31\\u5b66\\u5427\\u5c31", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-09-04T02:15:41.932Z", "screenshot_count": 0}	5	2025-09-04 10:15:20.932263	2025-09-04 10:15:41.94471	user6	2025-09-04 10:15:56.498508	完美标注，你就学吧就	2025-09-04 02:13:24.321151	2025-09-04 02:15:56.491471	[{"time": "2025-09-04T10:15:20.932263", "type": "claimed", "user_id": "user6", "user_name": "代雨昕"}, {"time": "2025-09-04T10:15:41.944710", "type": "submitted", "comment": "完美标注，你就学吧就", "user_id": "user6", "user_name": "代雨昕", "organ_count": 1}, {"time": "2025-09-04T10:15:56.498508", "type": "reviewed", "score": 5, "action": "approve", "comment": "完美标注，你就学吧就", "user_id": "user6", "user_name": "代雨昕"}]	\N	\N	\N	代雨昕	\N	代雨昕	\N	\N	\N	\N	\N	\N	\N
41cd30a8-9e45-43ff-bbf0-2eb8a1040c4e	车镇远	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
ac743ee1-1d84-4f89-9511-2afefd4b8ea2	贺琴	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2816960b-da80-4c0a-8591-971ff428cd44	谢安相	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
00020275-6bee-4f63-a938-69f61eb1ab95	蔡恒菊	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
task19	脑萎缩MRI标注任务004	标注脑部MRI影像中的萎缩区域	proj3	approved	medium	user6	user1	/api/images/brain004.jpg	{"comment": "\\u5b8c\\u7f8e\\u6807\\u6ce8\\uff0c\\u4f60\\u81ea\\u5df1\\u5b66\\u5427\\u5c31", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-09-04T06:05:46.902Z", "screenshot_count": 0}	5	2025-09-04 14:05:24.518887	2025-09-04 14:05:46.915465	user6	2025-09-04 14:06:10.683031	完美标注，你自己学吧就	2025-08-29 09:12:58.092482	2025-09-04 06:06:10.676594	[{"time": "2025-09-04T14:05:24.518887", "type": "claimed", "user_id": "user6", "user_name": "代雨昕"}, {"time": "2025-09-04T14:05:46.915465", "type": "submitted", "comment": "完美标注，你自己学吧就", "user_id": "user6", "user_name": "代雨昕", "organ_count": 1}, {"time": "2025-09-04T14:06:10.683031", "type": "reviewed", "score": 5, "action": "approve", "comment": "完美标注，你自己学吧就", "user_id": "user6", "user_name": "代雨昕"}]	\N	\N	\N	代雨昕	系统管理员	代雨昕	\N	\N	\N	\N	\N	\N	\N
task17	脑梗塞MRI标注任务002	标注脑部MRI影像中的梗塞区域	proj3	approved	high	user6	user1	/api/images/brain002.jpg	{"comment": "\\u5b8c\\u7f8e\\u6807\\u6ce8\\uff0c\\u4f60\\u81ea\\u5df1\\u5b66\\u5427\\u5c31", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-09-04T06:05:50.237Z", "screenshot_count": 0}	5	2025-09-04 14:05:19.651448	2025-09-04 14:05:50.246722	user6	2025-09-04 14:06:14.979668	完美标注，你自己学吧就	2025-08-29 09:12:58.092482	2025-09-04 06:06:14.974357	[{"time": "2025-09-04T14:05:19.651448", "type": "claimed", "user_id": "user6", "user_name": "代雨昕"}, {"time": "2025-09-04T14:05:50.246722", "type": "submitted", "comment": "完美标注，你自己学吧就", "user_id": "user6", "user_name": "代雨昕", "organ_count": 1}, {"time": "2025-09-04T14:06:14.979668", "type": "reviewed", "score": 5, "action": "approve", "comment": "完美标注，你自己学吧就", "user_id": "user6", "user_name": "代雨昕"}]	\N	\N	\N	代雨昕	系统管理员	代雨昕	\N	\N	\N	\N	\N	\N	\N
task18	脑出血MRI标注任务003	标注脑部MRI影像中的出血区域	proj3	approved	high	user6	user1	/api/images/brain003.jpg	{"comment": "\\u5b8c\\u7f8e\\u6807\\u6ce8\\uff0c\\u4f60\\u81ea\\u5df1\\u5b66\\u5427\\u5c31", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-09-04T06:05:54.333Z", "screenshot_count": 0}	5	2025-09-04 14:05:22.093591	2025-09-04 14:05:54.344197	user6	2025-09-04 14:06:19.61357	完美标注，你自己学吧就	2025-08-29 09:12:58.092482	2025-09-04 06:06:19.611893	[{"time": "2025-09-04T14:05:22.093591", "type": "claimed", "user_id": "user6", "user_name": "代雨昕"}, {"time": "2025-09-04T14:05:54.344197", "type": "submitted", "comment": "完美标注，你自己学吧就", "user_id": "user6", "user_name": "代雨昕", "organ_count": 1}, {"time": "2025-09-04T14:06:19.613570", "type": "reviewed", "score": 5, "action": "approve", "comment": "完美标注，你自己学吧就", "user_id": "user6", "user_name": "代雨昕"}]	\N	\N	\N	代雨昕	系统管理员	代雨昕	\N	\N	\N	\N	\N	\N	\N
task20	脑积水MRI标注任务005	标注脑部MRI影像中的积水区域	proj3	approved	medium	user6	user1	/api/images/brain005.jpg	{"comment": "\\u5b8c\\u7f8e\\u6807\\u6ce8\\uff0c\\u4f60\\u81ea\\u5df1\\u5b66\\u5427\\u5c31", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-09-04T06:06:45.446Z", "screenshot_count": 0}	5	2025-09-04 14:06:37.216954	2025-09-04 14:06:45.457371	user6	2025-09-04 14:06:56.610899	完美标注，你自己学吧就	2025-08-29 09:12:58.092482	2025-09-04 06:06:56.616657	[{"time": "2025-09-04T14:06:37.216954", "type": "claimed", "user_id": "user6", "user_name": "代雨昕"}, {"time": "2025-09-04T14:06:45.457371", "type": "submitted", "comment": "完美标注，你自己学吧就", "user_id": "user6", "user_name": "代雨昕", "organ_count": 1}, {"time": "2025-09-04T14:06:56.610899", "type": "reviewed", "score": 5, "action": "approve", "comment": "完美标注，你自己学吧就", "user_id": "user6", "user_name": "代雨昕"}]	\N	\N	\N	代雨昕	系统管理员	代雨昕	\N	\N	\N	\N	\N	\N	\N
dfc8a598-5706-4c42-885c-5b29a83ee53d	罗永信	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/罗永信	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
ece11f77-4fe6-43d3-801a-42c533a6081c	罗祥素	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/罗祥素	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a531e2ab-12ab-4400-b0ad-ffddebb723ea	聂义	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/聂义	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
ddb1415a-c551-4a3b-b979-9f0c94755617	董沁柚	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/董沁柚	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
bae0a4f8-eddb-4daf-ba44-8e97aa18a470	蒋明俊	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c992f38e-9bf6-4807-825f-8a06fd737e60	董沁柚	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
dc160ade-14bc-4223-96ee-587aa8b02833	李叶	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3be86ec0-7594-4025-98ac-211c6bb209d9	朱克进	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
15a244db-c66b-4e1e-9a2f-4441a094c4ca	张道见	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3047c285-1d32-4dc1-ad0e-c665c3e8a7cf	张正黔	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
de31922d-5194-4641-a95a-b6eadfcaf265	张孝良	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9f4851b7-16ea-4c03-9fa9-45275960cb68	张天虎	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3bca581c-4aaf-454d-be72-cd90f41391e1	于春国	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/于春国	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b275637f-372d-473d-840c-5820cbeee682	仇德银	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/仇德银	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
bc277d64-e8b9-4979-96ad-6b390984729c	任修永	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/任修永	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c231612a-0606-4491-a2bf-bf5d6cada6ad	任忆宸	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/任忆宸	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
fbabbaf3-e525-4300-b881-f13885f7fe05	冷玉奎	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/冷玉奎	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
171ebe76-c15d-489c-8740-bd6f312450c6	刘国南	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/刘国南	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
81dc593c-7ebe-4b86-9b73-6cdb57a8c0f7	刘成慧	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/刘成慧	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
e46777ef-bb78-423f-868b-2e53db90e214	刘永林	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/刘永林	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
74700456-16cb-4b51-a161-e61f9ae22d6c	吴光高	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/吴光高	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2198dd95-c397-4815-bfc2-80466dd5eb57	周文荣	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/周文荣	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b0afe3f5-ecdb-49f3-b592-0f67ac759c04	周训跃	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/周训跃	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
46237991-a54b-4ac7-a28b-d8698477dee2	夏建国	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/夏建国	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
8be66f8e-ab25-4fdf-8850-f784d69daf8f	孙平	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/孙平	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
429d1a82-d7d8-4291-93ac-e621db1618d4	孙朝军	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/孙朝军	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
97e6832e-95d8-44f4-bcfc-9b9cb778634b	孙筑琴	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/孙筑琴	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9ccc1a25-a7c8-4dd2-80c6-6ddde439b2d4	张其右	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/张其右	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
8e9d5abe-cbcb-4aab-966d-45f54ce2db11	张天炼	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/张天炼	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
053819fb-2462-4ec8-8a84-5db1dbb56398	张天虎	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/张天虎	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
6e08148d-041b-4211-a079-6ba51336af12	张孝良	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/张孝良	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
555dd6f0-db05-4bda-9be9-9b1863584247	张正黔	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/张正黔	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2d4b0679-0479-4b71-bd02-bf4a25a7ed15	张道见	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/张道见	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d6eb0918-341e-4016-83a5-c2d0a6587d76	朱克进	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/朱克进	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4f42505d-ed7d-4032-bfab-859ee2d6ab63	李叶	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/李叶	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2f276c09-cfeb-42b5-8697-e6e77b4a2c4f	李朝云	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/李朝云	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b51aa0e3-2dfe-4b46-b820-6d220d99c86e	杜启学	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/杜启学	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
ce9e92ef-9d61-4b78-8d0e-6efc43dc53f1	沈春容	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/沈春容	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
191f3d69-4b9c-4d47-baf3-1a7985145355	王庭珍	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/王庭珍	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
e4699935-e051-4654-aa06-2c7ee85c7c50	程第灿	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/程第灿	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b2f26e0f-444b-4517-9243-365baca99d11	JIA BIN		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4b94a2c3-51cb-4464-b6d6-7ec2fbab194e	蒋明俊	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/蒋明俊	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
537efcb3-55be-4062-b7c0-a9ea51bafdfd	蔡恒菊	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/蔡恒菊	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
bf901c06-debe-4ca1-a5c7-3df13b17f923	贺琴	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/贺琴	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
02e2c25d-2b24-49ac-8b9b-eae11306c516	车镇远	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/车镇远	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
fcec320f-dce1-4b1d-9aa7-ac154e23ce47	郑君	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/郑君	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9de5eacd-b040-4c13-b9f4-fdef2a93e782	郑安学	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/郑安学	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3a6dccc3-442d-4c81-86e2-7f789640691f	郑小明	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/郑小明	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
138c8668-b9fe-4580-bdca-38cba7343a05	陆显照	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/陆显照	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
1c4bdd7a-87e2-4332-bde5-0c17906b0b06	陈仕书	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/陈仕书	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a683873e-7a73-41d1-a8f5-2eb6a5f27c98	陈昌	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/陈昌	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0652f9d1-b3e8-4509-9df0-31e05673dec9	陈春德	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/陈春德	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
8faec497-1961-4011-ba99-9a5fb8c895be	陈永富	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/陈永富	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0a2ab376-7838-4765-a894-e7034474b9a5	雷青松	请输入任务描述大大大	proj2025302	pending	high	\N	user6	D:/任务管理测试数据/肝脏/雷青松	{"estimated_hours": 2.5}	\N	\N	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 06:36:18.383359	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3b95072f-b399-4b0a-8592-11067495d965	陈朝会	请输入任务描述大大大	proj2025302	skipped	high	\N	user6	D:/任务管理测试数据/肝脏/陈朝会	{"estimated_hours": 2.5}	\N	2025-09-05 14:38:01.031567	\N	\N	\N	\N	2025-09-05 06:36:18.383359	2025-09-05 08:19:44.0053	[{"time": "2025-09-05T14:38:01.031567", "type": "claimed", "user_id": "user6", "user_name": "代雨昕"}, {"time": "2025-09-05T15:19:25.090738", "type": "skip_requested", "images": ["http://localhost:9000/medical-annotations/reviews/3b95072f-b399-4b0a-8592-11067495d965/f1fa4623-1488-47d7-9545-b46903e3daf5.png"], "reason": "faffffffffffffffff", "user_id": "user6", "user_name": "代雨昕"}, {"time": "2025-09-05T16:19:44.009712", "type": "skip_approved", "comment": "同意跳过申请", "user_id": "user6", "approved": true, "user_name": "代雨昕"}]	2025-09-05 16:19:44.009712	faffffffffffffffff	["http://localhost:9000/medical-annotations/reviews/3b95072f-b399-4b0a-8592-11067495d965/f1fa4623-1488-47d7-9545-b46903e3daf5.png"]	\N	\N	\N	2025-09-05 15:19:25.090738	faffffffffffffffff	["http://localhost:9000/medical-annotations/reviews/3b95072f-b399-4b0a-8592-11067495d965/f1fa4623-1488-47d7-9545-b46903e3daf5.png"]	user6	2025-09-05 16:19:44.009712	user6	同意跳过申请
be4fd47f-eabc-491d-a98a-dc3676ae225f	谢安相	请输入任务描述大大大	proj2025302	approved	high	user6	user6	D:/任务管理测试数据/肝脏/谢安相	{"comment": " \\u5e06\\u5e06\\u5e06\\u5e06\\u5e06\\u5e06\\u5e06\\u5e06\\u5e06\\u5e06\\u5e06\\u5e06\\u5e06\\u5e06", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-09-05T06:38:56.902Z", "screenshot_count": 0}	5	2025-09-05 14:37:55.425572	2025-09-05 14:38:56.913958	user6	2025-09-05 16:26:49.289159		2025-09-05 06:36:18.383359	2025-09-05 08:26:49.294006	[{"time": "2025-09-05T14:37:55.425572", "type": "claimed", "user_id": "user6", "user_name": "代雨昕"}, {"time": "2025-09-05T14:38:56.913958", "type": "submitted", "comment": " 帆帆帆帆帆帆帆帆帆帆帆帆帆帆", "user_id": "user6", "user_name": "代雨昕", "organ_count": 1}, {"time": "2025-09-05T16:26:49.289159", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user6", "user_name": "代雨昕"}]	\N	\N	\N	代雨昕	\N	代雨昕	\N	\N	\N	\N	\N	\N	\N
db910922-116d-4db3-94fd-0e4ec7e16d03	郭长安	请输入任务描述大大大	proj2025302	approved	high	user6	user6	D:/任务管理测试数据/肝脏/郭长安	{"comment": "\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-09-05T06:39:03.102Z", "screenshot_count": 0}	5	2025-09-05 14:37:58.046357	2025-09-05 14:39:03.112044	user6	2025-09-05 16:26:52.190708		2025-09-05 06:36:18.383359	2025-09-05 08:26:52.194933	[{"time": "2025-09-05T14:37:58.046357", "type": "claimed", "user_id": "user6", "user_name": "代雨昕"}, {"time": "2025-09-05T14:39:03.112044", "type": "submitted", "comment": "烦烦烦烦烦烦烦烦烦烦烦烦烦烦烦", "user_id": "user6", "user_name": "代雨昕", "organ_count": 1}, {"time": "2025-09-05T16:26:52.190708", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user6", "user_name": "代雨昕"}]	\N	\N	\N	代雨昕	\N	代雨昕	\N	\N	\N	\N	\N	\N	\N
c25d8990-76a9-4450-bfca-29e600f61430	雷青松	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9063c7d2-cbc5-4a6c-be8f-a4bb49fa76b9	陈永富	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
07ff2efe-1218-4412-90ea-8e3535f494e0	陈朝会	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
1d0f4dbd-aa5e-4b9f-9e09-d35d030ae337	陈春德	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b556c0df-ecdd-4e0b-9e02-49c5eb19749d	陈昌	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
ca63148e-7089-476d-b62d-c0f35a3b75f6	SONG SHANG JUN		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
12c5af9a-b22a-4d25-91df-d682ba894bab	SHAO MING XIANG		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0abf9d6b-046b-4bfb-bf27-bae13b776669	SHANG XIU ZHEN		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5101d3b7-a97b-4bd0-8a3e-5f8f75964589	MAO QING YU		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9cda1deb-fc5d-4b08-b88a-adf67d597c90	张天炼	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
61202eff-040a-4b53-9eee-56d15b21d37c	张其右	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3fc4aa11-69cf-4af9-968d-dfde98ab73c1	孙筑琴	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c72be5e2-e10f-404c-89f1-1899f9b33c80	孙朝军	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
034b4a2e-e2cb-4afa-be2b-b42e697bf709	孙平	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
de6f9c9a-90e0-4ed5-9653-ab71996e0e99	夏建国	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a2b460a3-350f-464b-be55-6fc1a2a4678b	周训跃	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
528d2e10-5944-43ee-a767-7b6e611cf74f	周文荣	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
85f3b8f0-7a5c-4bf3-a336-052787938a70	吴光高	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
378f4c30-5f91-4990-abe1-7c0c99d23c5c	刘永林	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a340ce90-b733-4193-a8d6-a7a42c0d8827	刘成慧	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a987f042-5155-40d4-beeb-0ef151fe6371	刘国南	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
314e60e2-7eec-471b-8ab4-06b49424118a	冷玉奎	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5db901fb-8840-430e-a008-885fab371332	任忆宸	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
de38d372-a0b1-4e3f-9f5b-23fda41fc57c	任修永	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
bd68d064-e7bc-4b56-a875-eeb0e81d5e8a	仇德银	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
533bddf6-cdfe-41bf-89e5-3c1dea0fc159	于春国	细致的标注，不然挨打	proj2025401	pending	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	\N	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 08:54:59.150337	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
74afdca6-5b80-401e-acd2-5716a21a6663	JiaoGuizhan	2025第四次泌尿标注任务	proj2025301	approved	medium	user1	user1	E:/训练留档/泌尿导出/JiaoGuizhan	{"comment": "\\u81ea\\u5df1\\u770b\\u53c8\\u600e\\u6837\\uff0c\\u4e0d\\u6539\\u5355\\u72ec", "organ_count": 1, "uploaded_images": ["http://192.168.200.20:9000/medical-annotations/annotations/74afdca6-5b80-401e-acd2-5716a21a6663/62236b4f-22f4-4686-98a9-008783f16fc5.png"], "timestamp": "2025-10-09T08:04:26.413Z", "screenshot_count": 1}	5	2025-10-09 16:02:27.452693	2025-10-09 16:04:26.421188	user1	2025-10-17 14:32:30.159391		2025-09-04 02:13:24.321151	2025-10-17 06:32:30.119755	[{"time": "2025-10-09T16:02:27.452693", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T16:03:06.013106", "type": "submitted", "comment": "这是一个描述自己看把", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-09T16:03:59.308515", "type": "reviewed", "score": null, "action": "reject", "comment": "自己看", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T16:04:26.421188", "type": "submitted", "comment": "自己看又怎样，不改单独", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-17T14:32:30.159391", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	系统管理员	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N
4644fae1-f896-4123-829b-cea7692bc664	陈仕书	细致的标注，不然挨打	proj2025401	skipped	medium	\N	user1	\N	{"estimated_hours": 3.0}	\N	2025-10-09 16:55:22.938254	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-09 09:01:41.938968	[{"time": "2025-10-09T16:55:22.938254", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T17:00:57.261968", "type": "skip_requested", "images": ["http://192.168.200.20:9000/medical-annotations/reviews/4644fae1-f896-4123-829b-cea7692bc664/5d3c2352-0297-47d7-9b66-11e090cf1aac.png"], "reason": "导航键佛奥还不够好久", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T17:01:41.979607", "type": "skip_approved", "comment": "行吧", "user_id": "user1", "approved": true, "user_name": "系统管理员"}]	2025-10-09 17:01:41.979607	导航键佛奥还不够好久	["http://192.168.200.20:9000/medical-annotations/reviews/4644fae1-f896-4123-829b-cea7692bc664/5d3c2352-0297-47d7-9b66-11e090cf1aac.png"]	\N	\N	\N	2025-10-09 17:00:57.261968	导航键佛奥还不够好久	["http://192.168.200.20:9000/medical-annotations/reviews/4644fae1-f896-4123-829b-cea7692bc664/5d3c2352-0297-47d7-9b66-11e090cf1aac.png"]	user1	2025-10-09 17:01:41.979607	user1	行吧
b16ed336-68e4-4045-9dff-cf44a734f77d	JiNini	2025第四次泌尿标注任务	proj2025301	skipped	medium	\N	user1	E:/训练留档/泌尿导出/JiNini	{"estimated_hours": 4.0}	\N	2025-10-09 16:31:43.727947	\N	\N	\N	\N	2025-09-04 02:13:24.321151	2025-10-09 09:18:08.494087	[{"time": "2025-10-09T16:31:43.727947", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T16:32:50.436346", "type": "skip_requested", "images": ["http://192.168.200.20:9000/medical-annotations/reviews/b16ed336-68e4-4045-9dff-cf44a734f77d/0bdf0711-e20c-48bc-abc7-6726cf87a42b.png"], "reason": "烦烦烦烦烦烦烦烦烦烦烦烦烦烦烦烦烦烦", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T16:33:21.794936", "type": "skip_rejected", "comment": "这肯定不行啊，必须标注", "user_id": "user1", "approved": false, "user_name": "系统管理员"}, {"time": "2025-10-09T17:17:53.666743", "type": "skip_requested", "images": ["http://192.168.200.20:9000/medical-annotations/reviews/b16ed336-68e4-4045-9dff-cf44a734f77d/dcccdb3f-caea-48fb-9e6b-263e36fe49d9.png"], "reason": "不标了，自己想想看有没有问题呢", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T17:18:08.528539", "type": "skip_approved", "comment": "行", "user_id": "user1", "approved": true, "user_name": "系统管理员"}]	2025-10-09 17:18:08.528539	不标了，自己想想看有没有问题呢	["http://192.168.200.20:9000/medical-annotations/reviews/b16ed336-68e4-4045-9dff-cf44a734f77d/dcccdb3f-caea-48fb-9e6b-263e36fe49d9.png"]	\N	\N	\N	2025-10-09 17:17:53.666743	不标了，自己想想看有没有问题呢	["http://192.168.200.20:9000/medical-annotations/reviews/b16ed336-68e4-4045-9dff-cf44a734f77d/dcccdb3f-caea-48fb-9e6b-263e36fe49d9.png"]	user1	2025-10-09 17:18:08.528539	user1	行
3b7a82cc-c922-45fd-bf58-2e4f20daf6f0	MA JIAN		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
ca6fa579-ac81-4674-9ee7-06f5c0170368	LiangGaofeng	2025第四次泌尿标注任务	proj2025301	approved	medium	user1	user1	E:/训练留档/泌尿导出/LiangGaofeng	{"comment": "qwrqwtqwttqvctvtttqevwvc6ewy ", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-09T09:34:15.338Z", "screenshot_count": 0}	5	2025-10-09 17:34:08.337222	2025-10-09 17:34:15.353148	user1	2025-10-17 14:32:36.199084		2025-09-04 02:13:24.321151	2025-10-17 06:32:36.177574	[{"time": "2025-10-09T17:34:08.337222", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T17:34:15.353148", "type": "submitted", "comment": "qwrqwtqwttqvctvtttqevwvc6ewy ", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-17T14:32:36.199084", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	系统管理员	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N
7805b7a8-b11c-46aa-8459-1ceee93977cf	BaiXinqi	2025第四次泌尿标注任务	proj2025301	approved	medium	user1	user1	E:/训练留档/泌尿导出/BaiXinqi	{"comment": "aweqrtqwttqwtttqetasdasqw", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-09T09:38:29.391Z", "screenshot_count": 0}	5	2025-10-09 17:38:12.252797	2025-10-09 17:38:29.403294	user1	2025-10-17 14:32:38.376106		2025-09-04 02:13:24.321151	2025-10-17 06:32:38.364131	[{"time": "2025-10-09T17:38:12.252797", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T17:38:29.403294", "type": "submitted", "comment": "aweqrtqwttqwtttqetasdasqw", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-17T14:32:38.376106", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	系统管理员	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N
3296f6ed-881f-40f0-b2ad-f9c149705d96	BanHu	2025第四次泌尿标注任务	proj2025301	approved	medium	user1	user1	E:/训练留档/泌尿导出/BanHu	{"comment": "awfawfawfaw", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-09T09:43:27.633Z", "screenshot_count": 0}	5	2025-10-09 17:43:15.226064	2025-10-09 17:43:27.643531	user1	2025-10-17 14:32:39.91821		2025-09-04 02:13:24.321151	2025-10-17 06:32:39.915528	[{"time": "2025-10-09T17:43:15.226064", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T17:43:27.643531", "type": "submitted", "comment": "awfawfawfaw", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-17T14:32:39.918210", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	系统管理员	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N
2eae67bf-2688-46d9-9131-515fe63dc3a4	蔡恒菊	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	approved	high	user1	user1	D:/任务管理测试数据/肝脏/蔡恒菊	{"comment": "\\u5ba1\\u6838\\u5b8c\\u6bd5\\u540e\\u7684\\u4e1c\\u897fi\\u5927\\u5bb6\\u963f\\u5a46\\u7684\\u9a84\\u50b2\\u548c\\u5355\\u4f4d\\u6211\\u7acb\\u523b\\u53bb\\u6d77\\u5357", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-10T01:02:51.950Z", "screenshot_count": 0}	5	2025-10-10 09:01:55.598397	2025-10-10 09:02:51.962517	user1	2025-10-17 14:32:41.559166		2025-09-02 06:39:58.916713	2025-10-17 06:32:41.566254	[{"time": "2025-10-10T09:01:55.598397", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-10T09:02:51.962517", "type": "submitted", "comment": "审核完毕后的东西i大家阿婆的骄傲和单位我立刻去海南", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-17T14:32:41.559166", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	系统管理员	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
18dd2643-7259-4215-8f59-574c709f0dc3	KangDexin	2025第四次泌尿标注任务	proj2025301	approved	medium	user1	user1	E:/训练留档/泌尿导出/KangDexin	{"comment": "\\u560e\\u560e\\u95ee\\u8fc7\\u4ed6\\u7ef4\\u5854\\u6258\\u5c3c\\u5982\\u56fe\\u54bd\\u5589\\u708e\\u8ba9\\u4ed6", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-09T09:30:01.367Z", "screenshot_count": 0}	5	2025-10-09 17:29:44.227051	2025-10-09 17:30:01.380559	user6	2025-10-10 09:10:29.278128		2025-09-04 02:13:24.321151	2025-10-10 01:10:29.253976	[{"time": "2025-10-09T17:29:44.227051", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T17:30:01.380559", "type": "submitted", "comment": "嘎嘎问过他维塔托尼如图咽喉炎让他", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-10T09:10:29.278128", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user6", "user_name": "代雨昕"}]	\N	\N	\N	系统管理员	\N	代雨昕	\N	\N	\N	\N	\N	\N	\N
44897977-2998-4881-b6c8-2918d3c5374c	LV JIAN ZHI		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4a740039-4102-4727-ad85-9d029762671a	LUO JIAN HUA		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
e7dd79d1-6e2a-4e44-acb4-0ecf7cd8f4da	LU LI MIAO		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3d2fc028-e630-42a0-b446-94e23f2cff89	LIU JIANG BO		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0c034a2c-18f7-417e-bffc-91da803474c7	张正黔	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	approved	high	user1	user1	D:/任务管理测试数据/肝脏/张正黔	{"comment": "\\u7236\\u4eb2\\u4e4c\\u514b\\u5170\\u548c\\u4f60\\u5feb\\u70b9\\u56de\\u53bb\\u5427\\u6211\\u514b\\u9686\\u4e94\\u767e", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-10T01:13:21.262Z", "screenshot_count": 0}	5	2025-10-10 09:13:12.529943	2025-10-10 09:13:21.271069	user1	2025-10-17 14:32:47.679366		2025-09-02 06:39:58.916713	2025-10-17 06:32:47.72261	[{"time": "2025-10-10T09:13:12.529943", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-10T09:13:21.271069", "type": "submitted", "comment": "父亲乌克兰和你快点回去吧我克隆五百", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-17T14:32:47.679366", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	系统管理员	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
06752f5d-6d11-45a1-91e9-a0c81a3d2e5b	孙筑琴	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	approved	high	user1	user1	D:/任务管理测试数据/肝脏/孙筑琴	{"comment": "dnakldhaoholujpoweqjwe q", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-10T02:05:48.137Z", "screenshot_count": 0}	5	2025-10-10 09:13:09.985057	2025-10-10 10:05:48.149036	user1	2025-10-17 14:32:49.32349		2025-09-02 06:39:58.916713	2025-10-17 06:32:49.376386	[{"time": "2025-10-10T09:13:09.985057", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-10T10:05:48.149036", "type": "submitted", "comment": "dnakldhaoholujpoweqjwe q", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-17T14:32:49.323490", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	系统管理员	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
3197de9a-e5a6-4a5d-bee2-037e2eef74d1	刘国南	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	approved	high	user1	user1	D:/任务管理测试数据/肝脏/刘国南	{"comment": "lkdjnljwoiqyhoieuqpwhnrklqwrqw", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-10T02:11:01.516Z", "screenshot_count": 0}	5	2025-10-10 10:10:39.30303	2025-10-10 10:11:01.526356	user1	2025-10-17 14:32:50.877445		2025-09-02 06:39:58.916713	2025-10-17 06:32:50.88197	[{"time": "2025-10-10T10:10:39.303030", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-10T10:11:01.526356", "type": "submitted", "comment": "lkdjnljwoiqyhoieuqpwhnrklqwrqw", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-17T14:32:50.877445", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	系统管理员	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
58c7c779-c5a0-4dfe-973b-48a83a0064ec	陈朝会	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	approved	high	user1	user1	D:/任务管理测试数据/肝脏/陈朝会	{"comment": "dqwjroiwhqoirhojtkf;lqkwetq", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-10T02:15:35.136Z", "screenshot_count": 0}	5	2025-10-10 10:15:26.100092	2025-10-10 10:15:35.146586	user1	2025-10-17 14:32:53.047176		2025-09-02 06:39:58.916713	2025-10-17 06:32:53.033534	[{"time": "2025-10-10T10:15:26.100092", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-10T10:15:35.146586", "type": "submitted", "comment": "dqwjroiwhqoirhojtkf;lqkwetq", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-17T14:32:53.047176", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	系统管理员	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
4a766e17-7bc6-4ce3-994d-6e1a90b4127e	罗永信	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	approved	high	user8	user1	D:/任务管理测试数据/肝脏/罗永信	{"comment": "\\u6d4b\\u8bd5\\u63d0\\u4ea4\\u901a\\u77e5\\u8bf7\\u95ee\\u72ac\\u761f\\u70ed\\u63d0\\u53d6\\u7269", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-10T02:38:21.556Z", "screenshot_count": 0}	5	2025-10-10 10:37:53.912033	2025-10-10 10:38:21.567145	user6	2025-10-10 10:39:13.192363	审核它通过 瓦盆请问	2025-09-02 06:39:58.916713	2025-10-10 02:39:13.236959	[{"time": "2025-10-10T10:37:53.912033", "type": "claimed", "user_id": "user8", "user_name": "王欢欢"}, {"time": "2025-10-10T10:38:21.567145", "type": "submitted", "comment": "测试提交通知请问犬瘟热提取物", "user_id": "user8", "user_name": "王欢欢", "organ_count": 1}, {"time": "2025-10-10T10:39:13.192363", "type": "reviewed", "score": 5, "action": "approve", "comment": "审核它通过 瓦盆请问", "user_id": "user6", "user_name": "代雨昕"}]	\N	\N	\N	王欢欢	系统管理员	代雨昕	\N	\N	\N	\N	\N	\N	\N
4d20dc4b-3f62-4c2f-99d6-7a9281669f15	任修永	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	approved	high	user8	user1	D:/任务管理测试数据/肝脏/任修永	{"comment": "\\u63d0\\u4ea4\\u5ba1\\u6838\\u4e86\\u7684\\u72ac\\u761f\\u70ed\\u72ac\\u761f\\u70ed\\u63d0\\u53d6\\u7269\\u5929\\u5929t", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-10T02:42:22.583Z", "screenshot_count": 0}	5	2025-10-10 10:41:36.863274	2025-10-10 10:42:22.594567	user6	2025-10-10 10:42:42.06779	lnlknlkbblm	2025-09-02 06:39:58.916713	2025-10-10 02:42:42.175611	[{"time": "2025-10-10T10:41:36.863274", "type": "claimed", "user_id": "user8", "user_name": "王欢欢"}, {"time": "2025-10-10T10:42:22.594567", "type": "submitted", "comment": "提交审核了的犬瘟热犬瘟热提取物天天t", "user_id": "user8", "user_name": "王欢欢", "organ_count": 1}, {"time": "2025-10-10T10:42:42.067790", "type": "reviewed", "score": 5, "action": "approve", "comment": "lnlknlkbblm", "user_id": "user6", "user_name": "代雨昕"}]	\N	\N	\N	王欢欢	系统管理员	代雨昕	\N	\N	\N	\N	\N	\N	\N
4e7d4687-bf61-4579-b9a7-6a6c19243811	张其右	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	approved	high	user8	user1	D:/任务管理测试数据/肝脏/张其右	{"comment": "\\u81ea\\u5df1\\u770b\\u770b\\u7b49\\u5019who\\u4fc4\\u56fd\\u548c\\u671f\\u671b\\u5de5\\u4eba\\u4f01\\u9e45", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-10T02:57:07.387Z", "screenshot_count": 0}	5	2025-10-10 10:41:39.399742	2025-10-10 10:57:07.397823	user6	2025-10-10 10:57:21.511192	dqwqtqrqwerqwwr	2025-09-02 06:39:58.916713	2025-10-10 02:57:21.476215	[{"time": "2025-10-10T10:41:39.399742", "type": "claimed", "user_id": "user8", "user_name": "王欢欢"}, {"time": "2025-10-10T10:42:55.201629", "type": "submitted", "comment": "再次提提交测试爱的请问人情味", "user_id": "user8", "user_name": "王欢欢", "organ_count": 1}, {"time": "2025-10-10T10:43:11.530645", "type": "reviewed", "score": null, "action": "reject", "comment": "dahuichongbiaoweq", "user_id": "user6", "user_name": "代雨昕"}, {"time": "2025-10-10T10:57:07.397823", "type": "submitted", "comment": "自己看看等候who俄国和期望工人企鹅", "user_id": "user8", "user_name": "王欢欢", "organ_count": 1}, {"time": "2025-10-10T10:57:21.511192", "type": "reviewed", "score": 5, "action": "approve", "comment": "dqwqtqrqwerqwwr", "user_id": "user6", "user_name": "代雨昕"}]	\N	\N	\N	王欢欢	系统管理员	代雨昕	\N	\N	\N	\N	\N	\N	\N
fab4ebb1-44ed-463f-84fa-9a5b0de0e895	LI YU YING		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4125cb3b-c302-4cbc-b7b8-1f97ce4b5b37	LI YONG ZHI		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
e01bf005-6efb-435a-a731-7d071b1ec59c	LI SHUANG LIAN		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3226701b-264f-4f03-8239-e4fa2b09bf9a	JIAO PI XIANG		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
310901d3-debf-45ad-bdec-c60c34befa03	JIANG HUA		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
53a17e38-5888-4f3e-a8ab-cc2add73f137	冷玉奎	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	approved	high	user8	user1	D:/任务管理测试数据/肝脏/冷玉奎	{"comment": "\\u6848\\u8bf4\\u6cd5\\u72ac\\u761f\\u70ed\\u72ac\\u761f\\u70ed\\u8bf7\\u95ee", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-11T08:02:55.038Z", "screenshot_count": 0}	5	2025-10-10 10:41:42.008343	2025-10-11 08:02:55.046104	user1	2025-10-13 14:40:36.625593	你通过了	2025-09-02 06:39:58.916713	2025-10-13 06:40:36.616103	[{"time": "2025-10-10T10:41:42.008343", "type": "claimed", "user_id": "user8", "user_name": "王欢欢"}, {"time": "2025-10-10T10:47:17.047430", "type": "skip_requested", "images": ["http://192.168.200.20:9000/medical-annotations/reviews/53a17e38-5888-4f3e-a8ab-cc2add73f137/8d2af3d2-3664-48d2-8cfa-c815a24533c8.png"], "reason": "申请他跳过看看考过英语", "user_id": "user8", "user_name": "王欢欢"}, {"time": "2025-10-10T10:47:39.683971", "type": "skip_rejected", "comment": "拒绝跳过申请", "user_id": "user6", "approved": false, "user_name": "代雨昕"}, {"time": "2025-10-10T10:48:16.988467", "type": "skip_requested", "images": ["http://192.168.200.20:9000/medical-annotations/reviews/53a17e38-5888-4f3e-a8ab-cc2add73f137/08b9b934-fe18-4e8b-829d-4e2643e59370.png"], "reason": "嫩江抛弃我黑哦气味很浓二号桥乌克兰", "user_id": "user8", "user_name": "王欢欢"}, {"time": "2025-10-10T11:32:09.005573", "type": "skip_rejected", "comment": "的撒发生", "user_id": "user6", "approved": false, "user_name": "代雨昕"}, {"time": "2025-10-11T08:02:55.046104", "type": "submitted", "comment": "案说法犬瘟热犬瘟热请问", "user_id": "user8", "user_name": "王欢欢", "organ_count": 1}, {"time": "2025-10-13T14:40:36.625593", "type": "reviewed", "score": 5, "action": "approve", "comment": "你通过了", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	王欢欢	系统管理员	系统管理员	2025-10-10 10:48:16.988467	嫩江抛弃我黑哦气味很浓二号桥乌克兰	["http://192.168.200.20:9000/medical-annotations/reviews/53a17e38-5888-4f3e-a8ab-cc2add73f137/08b9b934-fe18-4e8b-829d-4e2643e59370.png"]	user8	2025-10-10 11:32:09.005573	user6	的撒发生
b5384f43-18f0-4162-9f94-03148f2ca429	聂义	细致的标注，不然挨打	proj2025401	in_progress	medium	user8	user1	\N	{"estimated_hours": 3.0}	\N	2025-10-11 08:02:48.589791	\N	\N	\N	\N	2025-10-09 08:54:59.150337	2025-10-11 08:02:48.579862	[{"time": "2025-10-11T08:02:48.589791", "type": "claimed", "user_id": "user8", "user_name": "王欢欢"}]	\N	\N	\N	王欢欢	\N	\N	\N	\N	\N	\N	\N	\N	\N
5743c3fb-5c58-4cac-b802-40709a1ec1db	郑小明	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	approved	high	user8	user1	D:/任务管理测试数据/肝脏/郑小明	{"comment": "safawqeqwrqwfagawdqwr", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-10T03:32:19.574Z", "screenshot_count": 0}	5	2025-10-10 11:15:42.884824	2025-10-10 11:32:19.584765	user1	2025-10-11 16:03:12.301959	safqwrqwrqwrq	2025-09-02 06:39:58.916713	2025-10-11 08:03:12.296189	[{"time": "2025-10-10T11:15:42.884824", "type": "claimed", "user_id": "user8", "user_name": "王欢欢"}, {"time": "2025-10-10T11:15:48.978871", "type": "submitted", "comment": "2rfqwtqtqwtqwt", "user_id": "user8", "user_name": "王欢欢", "organ_count": 1}, {"time": "2025-10-10T11:16:09.925667", "type": "reviewed", "score": null, "action": "reject", "comment": "fasfasf", "user_id": "user6", "user_name": "代雨昕"}, {"time": "2025-10-10T11:32:19.584765", "type": "submitted", "comment": "safawqeqwrqwfagawdqwr", "user_id": "user8", "user_name": "王欢欢", "organ_count": 1}, {"time": "2025-10-11T16:03:12.301959", "type": "reviewed", "score": 5, "action": "approve", "comment": "safqwrqwrqwrq", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	王欢欢	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
e097f39b-ec95-46cf-b2fc-c02cd5531d81	罗永信	细致的标注，不然挨打	proj2025401	approved	medium	user8	user1	\N	{"comment": "\\u5ba1\\u6838\\u610f\\u89c1\\u5df2\\u7ecf\\u5728\\u622a\\u56fe\\u4e2d\\u6807\\u660e", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-13T10:11:55.896Z", "screenshot_count": 0}	5	2025-10-13 18:11:32.676324	2025-10-13 18:11:55.908229	user1	2025-10-17 14:33:00.216639		2025-10-09 08:54:59.150337	2025-10-17 06:33:00.187063	[{"time": "2025-10-13T18:11:32.676324", "type": "claimed", "user_id": "user8", "user_name": "王欢欢"}, {"time": "2025-10-13T18:11:55.908229", "type": "submitted", "comment": "审核意见已经在截图中标明", "user_id": "user8", "user_name": "王欢欢", "organ_count": 1}, {"time": "2025-10-17T14:33:00.216639", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	王欢欢	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N
b57b3bb2-881c-4431-ae43-5d8087191102	罗祥素	细致的标注，不然挨打	proj2025401	approved	medium	user8	user1	\N	{"comment": "\\u5e26\\u56de\\u53bb\\u6211i\\u6000\\u67d4\\u533a\\u5f88\\u6e29\\u67d4", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-13T08:33:24.793Z", "screenshot_count": 0}	5	2025-10-13 16:31:46.493075	2025-10-13 16:33:24.803488	user1	2025-10-13 16:33:51.811039	国家规定	2025-10-09 08:54:59.150337	2025-10-13 08:33:51.980556	[{"time": "2025-10-13T16:31:46.493075", "type": "claimed", "user_id": "user8", "user_name": "王欢欢"}, {"time": "2025-10-13T16:33:24.803488", "type": "submitted", "comment": "带回去我i怀柔区很温柔", "user_id": "user8", "user_name": "王欢欢", "organ_count": 1}, {"time": "2025-10-13T16:33:51.811039", "type": "reviewed", "score": 5, "action": "approve", "comment": "国家规定", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	王欢欢	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N
79e63b39-2c3d-4761-9639-c3bc9df4bbc5	ZHUANG JU XIANG		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
8e875afd-d718-41f8-ad01-c1c502d374da	ZHENG CHUN LAN		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b3a2a05c-b22e-414f-a8ad-a9650c8bd5e5	YU SHU MEI		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a36c44e1-80f8-48b4-803e-672fa3b2fccc	YU JIAN YING		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
38a321ec-7c44-44ea-8e5a-2e6f1fd4ea11	YU BO		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
f9892113-1912-444c-bd36-60e10f2999da	YANG KAI		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
fed1bf30-85d7-44ec-af6b-517909db12ba	XU ZAI GUANG		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
932b9806-eb72-4822-b7bd-c3c6ac3502cc	XU LING JUAN		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2b7145b0-9cb4-4a72-a081-d57e8bd47709	XIU XUE RONG		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
6b26aeec-5f47-4ddc-b261-28a9eb9ef6e5	XIN CHENG		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
dba2dcc6-6b09-44b9-bf0c-177562eba40e	XIAO AI XIANG		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
db68fa37-c9a3-4d95-8933-e3a1a0f3209d	WU QING JUAN		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b4831c33-c2d5-4c8e-a9ff-346bb658e71d	WANG ZONG FU		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5edc1737-e579-470f-9cd6-781704c93a6b	WANG ZHI YUAN		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
54e672a6-c251-480a-8d48-9c5e5d5f90d9	WANG YONG QING		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c985c261-9571-4b5f-9f23-e2c701a0d730	WANG YONG		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
221fea3e-0cdc-43be-a382-9e3d727902eb	WANG XIU FENG		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
183ce963-fcbd-4091-8237-367f9cb7644f	WANG JIN TAO		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9132b126-b728-4691-a947-7e55f5ef8e00	WANG CHUN XIANG		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
71c4528b-bdc1-4aba-b457-14a112677d73	TENG LONG		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
ffac2afc-533d-4155-8227-16bda5f3ec8b	SU YAN HUA		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
369499b8-7ff8-4be6-af43-db985756a387	SONG XIU JUAN		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
265a011c-77f7-402d-bcf6-0055c88472cb	HOU QIU JU		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
e55ed433-09c7-4819-a5cc-f9f0ff9286b5	HAN XIU SUO		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
14f5ec02-2d8a-463d-9751-63df28c629b4	HAN JIAN MIN		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b609c60f-1f99-46c5-9283-b016d287b56a	GONG MEI YUN		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3e03cb3a-ac3d-4054-a081-1dbe3873a0d1	GAO RONG		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a8150c78-2062-4dc1-be12-ab2308e63bf5	FU YU LAN		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0341669a-dc95-4711-ab59-0510fd4c3257	FANG HAO ZHE		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a2320d79-536a-450c-aa36-c6b90200860d	DU WEN JUN		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
6be118b4-3c90-4280-8853-5d9618ed7cba	CHEN XIAO MIN		proj2025402	pending	medium	\N	user6	\N	{"estimated_hours": 0.0}	\N	\N	\N	\N	\N	\N	2025-10-14 07:59:24.54806	2025-10-14 07:59:24.54806	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b4b90f0f-6494-434f-8740-997c9f798676	ZouShulan	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3221440d-3661-4344-a21f-ecc0dcbccc83	ZhuZhengge	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7621cd06-9add-4718-975b-ac19744b040d	ZhuYuqian	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0edaf329-daf0-4482-8e46-e7712a919eae	ZhuRuixian	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c426d13e-4461-4cb5-9476-12afa0390898	ZhuDekui	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2cc28697-fb12-4314-bb41-07a7c246d9a3	ZhuChunlin	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b2543e46-c39e-4a01-b0d0-3fe1d9457143	ZhouYanmin	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
08617f47-731c-43f1-90e2-096eb7296bfa	ZhouLanfang	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c3685c36-1e8c-4a36-89d4-fc7ea2ead7a4	ZhouHekun	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
ece880d0-815b-4b34-b4ad-e966d2ce94c0	ZhengRuifa	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
67e37a66-0e0e-405a-8d3b-6917c67533f1	ZhaoYunlan	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
6cec6871-a17f-4c52-92b1-be0f871b9623	ZhaoYunfu	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a5e1b507-4474-46e7-b8f4-454787e4eeb8	ZhaoYuanquan	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
e9b641f8-20d7-43cd-ae63-4e8323ef6309	ZhaoYonggang	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3ea5a9d8-a66f-4e0b-902e-cd0a9cccda92	ZhaoYanbiao	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
1ee48230-989d-41c0-8d54-4f34b66ad93f	ZhaoXutang	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d8c6cf80-382f-4ebe-9e2a-459a382273b8	ZhaoXixun	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
1d7294d4-05b5-41fe-89b8-7165473a2622	ZhaoShiyu	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7aaa28e5-53fe-457d-9498-ad7da1b14d70	ZhaoQuansheng	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5a6da657-9402-4b9e-896e-3c5cef472a42	ZhaoQing	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
263b2609-fb8c-4e79-88a9-97c48a26bdf7	ZhaoJulu	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
44aa126b-6c89-4ee0-9dc2-afd898901310	ZhaoHongyi	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9659fe10-db28-4d0e-8706-cb46613088f8	ZhaoHongmei	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
6e4f91f0-6efd-42e8-a2c3-bbb2ba8ab41b	ZhaoFen	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2c34c915-ea6f-41ed-976b-d7e093558fd2	ZhangYunjuan	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
aa0d0c69-8cb5-47ba-bc34-e4402d9fd99d	ZhangYanhua	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
054884a9-26c6-4dae-a3be-90cd6d4156e2	ZhangYan	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c5dd8d54-e1fe-4ba9-9504-ba90d3fa3153	ZhangXuejun	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0ca946cc-049c-4612-ba45-6728a7d91978	ZhangXinjun	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
e72df68b-2ad5-4b7f-9497-05a4a68f7eab	ZhangXianlin	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c6cbfd71-07f4-426e-87f8-1e78f5a039ef	ZhangWenqian	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
141ea3fa-70ac-4e36-a33e-45f9e0b0c90a	ZhangWenbao	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9158fd23-fa38-4ad9-8108-89e638d0039b	ZhangSongling	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b9eb90d9-daa4-483c-949a-246545bc13ca	ZhangShuping	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
1614a509-f91f-4762-84d4-22f858dab3a5	ZhangRongyu	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0b824ec1-eb00-4f80-af87-965930dacd5d	ZhangQingqi	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
941d8c09-2d81-4365-98d5-bd1225529d78	ZhangNinghai	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2d0d7da9-3c7d-4400-bfce-9f6d41b893ef	ZhangMingxiu	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
516eb5d9-15e8-481d-802d-ea117b4e2a5a	ZhangMeihua	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
fb790ac6-b2c0-4537-a9ca-096639e6590f	ZhangLinbing	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2a5544e8-a8dc-493c-a588-1c308414b5d5	ZhangLanhua	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
33b1306c-d8da-466f-8514-5d8483b26fe1	ZhangJiYuan	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9f117999-f7cd-4f07-88a9-93a2cf800f23	ZhangHuying	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
37e24846-a414-4e08-a4dc-047c7c75b995	ZhangDongxing	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0c42472f-33a6-4b22-a744-bb2eba31ca78	ZhangChuanliang	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2062e3c5-583d-4f29-95f9-68a8fa9e1707	ZhangBin	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
6fc02146-07c6-48c6-bc63-3db66e337d2f	ZhangBaochun	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
e16a17aa-df0a-4f93-849e-a31b4902a7ae	ZhangAizhi	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0789f992-3559-45ac-ac63-bd4b6fb1f3a4	ZhangAirong	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9cd7aef2-a1b2-41b0-8bcb-ee32f39e8a6e	ZhanAibo	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
e7f5ef19-46a5-4cf0-bb2c-f19c3d8e0621	YuWenyan	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
803bb32b-fc22-45b7-aecb-6baef508c9a3	YuQiuyan	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
928d49fa-1110-4550-b36b-ee06671bc6e6	YuCuilan	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b0573eb1-74e4-45be-9db4-af8542363d7c	YouXiujie	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c7cf2d25-d74f-4b26-a5a1-9616102fca04	YinQijian	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b9ab43b4-0c24-4b0e-b037-4e4d5c4c269f	YaoLi	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
48d374ec-1964-42d1-a5cf-8742e1945d9c	YaoHongmei	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9efc7601-a975-46dc-a60b-39397a04f55c	YanJiahui	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
1d72b804-0a58-41fe-8df2-4a763f259b1f	YangYuying	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3b1fa2a7-ccd5-484b-bf0a-3fd00aae1d04	YangQingfang	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
eba8563a-6e7a-4c96-b8d8-002206ebb4d7	YangPeng	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
741d512d-54ea-4b5c-ad7f-15f5f3cca8dd	YangHongying	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5097e946-da61-4b71-bd01-67e57dddd5c5	XuLeina	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3201f342-be68-43cb-b971-b245634958c4	XuFumei	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
ff94c830-a5fb-4e13-bb3e-4c3a2be77e9f	XuChuanguo	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7c9ac49b-1563-4acf-af02-fc4e0cbaa252	XingLei	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
145882cd-fd79-46b9-bee9-c2d0dac1e1e9	XianYuqiao	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
235dba4b-bb64-474c-99fa-81cd88eabf16	XiaNianhui	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
0ce4953b-b310-4355-b1f5-743964bed2f5	XiangYichang	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
baee9bd8-31d0-46ad-b9e3-5fab3bbc0ff2	WuZhenxiang	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
cef78d94-6e19-4027-ad47-b0bef8213db6	WuHouchun	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
371b0a29-2e4d-41a3-b551-384f987b1745	WenShumei	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9e939dc2-cde7-4af8-aa4d-323fb1ff7f52	WeiJunying	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4bcf8b85-d374-4fa8-8401-cd458617fd26	WangZhongzhen	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
10e93e4e-b85d-4566-b3f0-277049732b4f	WangZhenguo	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9cdda639-c377-4d10-878d-d65674aed62a	WangZheng	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
e3f34abb-8142-49a3-987c-9b36e6fb863a	WangYunqing	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
f8c73ba0-e44e-4246-a12c-4a2cb3485b4c	WangYunhua	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9890d5f4-be2c-4740-bcef-a36218f55a99	WangXueli	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
78af29a1-3ca1-4a50-992e-ac214e51a5da	WangXuegong	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5b45ca7a-eaf0-4f47-9153-832366575d69	WangXiuming	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3704093e-7a79-4d93-a49c-e75a04a915aa	WangXiangbin	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c0f053d2-d1e8-455c-aab1-79eab2c21a18	WangTiantian	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
05a8441d-db4b-4941-80f6-9aab1076235f	WangSijun	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
af2aed24-5da1-490e-bab8-02213ff93027	WangShuhong	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
e1ec1767-a010-4124-ba2c-7789f536c110	WangRanfeng	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
c9b70cb0-fa7a-4d89-83c8-8f3d3c34849c	WangQinghe	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
796128b0-940f-4a77-be62-00211e7d12c2	WangMin	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
beea042b-ce8e-480e-91b8-59262e0276dc	WangLianyi	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4e1fb1a0-0dfb-47ce-a9a7-a13e02b43e08	WangKuangdong	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9e911b88-b67d-4f3e-9e63-a3661bd04a9b	WangKegang	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7f237fe6-6afb-4933-88c8-56689af64d64	WangJimei	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
bd743609-f3b8-4872-bab2-151763842555	WangJianhua	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
dfa61aa6-50ad-47e4-9f5e-cc1ad7b21386	WangHui	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
616f3df7-12d9-4213-a3fa-7db7099ee335	WangHengwei	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a2dc16d6-1b96-4d6f-8b10-080278b04f3f	WangHaodu	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2176bc48-70b1-4071-a393-d100bf31d875	WangFangxue	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
861333a2-f30a-4e50-a69c-e4f475cd3f9b	WangEnxiang	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b8294287-b49b-4887-aa13-eb8716c567d8	WangDeyuan	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
092b58ef-1ace-483c-b77c-6765f03dfd75	WangChunquan	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
09fa51c0-2f10-45bb-9ec6-ee97f8771a9c	WangChunmei	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
fa7f646b-2ee2-4f2a-bad6-8bc326bf6f9e	WangChunhua	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
e0fc1b96-4c03-40ed-a4e5-e8df785c0360	WangChengyou	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7efed3ce-b14f-4b2f-b553-cf7622653c51	TianWeidong	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7db871b1-8b2a-4f51-b42e-52345858d666	TianDexing	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
419a3bd7-7838-4304-bdb0-f795a33448eb	SunZhaoxia	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
396afa6a-6963-4e66-83fa-4c6663091eab	SunQixiang	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9172edf6-4e53-4f25-a06c-2dcd872eccfc	SunLixiang	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
03f58337-2776-4db0-a616-1da238651a7a	SunJianhua	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9236c412-cbef-4082-8bc4-ab46a2e36ee3	SunGuiqin	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d74a799a-f676-4b40-b72e-be2a8bd80d17	SunFengxin	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4065b8b9-9a85-4a4e-ba47-ced14c212226	SunChuanhe	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
de66aba2-f901-4e7c-aac7-1547ebe5803a	SuDiancheng	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
cf73169e-e127-4947-a61f-569ea1bfe441	SongZhixue	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
41d1bd51-89c2-48a3-9836-099f529e9124	SongYicai	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4855f911-dffd-4bbc-a479-6434d3069783	SiQinge	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3b7d5021-6acb-4c5f-b20b-64f2bf2ca177	SiHongwei	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
cb1e165d-428d-48c7-bc5f-c9d25f392f4a	ShiZaiyin	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a378ddc8-4760-4c6c-8556-5146cf0ef474	ShiYu	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b1d98736-25a3-48d5-b9e0-cd564e9ee95c	ShiKejiang	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d31d0a0e-88ac-40af-b672-9b9fc9133963	ShiChuanbin	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
cfd26fa8-55d3-40eb-9f47-56bd866d1ba8	ShenShiduan	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
6172e93b-8ed3-4eec-a688-9848c16996eb	ShaoAixing	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
410fa6b3-a915-45f4-86b7-0a3323bf090c	ShangZhenyang	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
b6f22102-b472-4ae2-812a-bddb0b799709	ShangRongxin	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7300c555-f55a-4102-ab12-913e931890bf	ShangQing	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
fb8a8d6d-fa07-47d8-90b6-786d7a5e8ede	RenGuiping	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
d1d8bdfc-2f4e-49d0-83f6-ff9305d495e0	QuQinghai	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a5403de2-587a-4452-9672-0bbd2b0f577c	QiHuaiming	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
a68656b4-d8f8-4e0a-8f76-87b7a9b50eb6	PinYanxia	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2a3a3e5d-784d-43ee-bff0-171a53021e08	PeiJinsheng	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
1e2b7703-febc-4c88-bec4-c89b4fb5ae6e	NiuXiaoxi	任务描述	proj2025403	pending	medium	\N	user1	\N	{"estimated_hours": 4.0}	\N	\N	\N	\N	\N	\N	2025-10-15 07:04:21.708903	2025-10-15 07:04:21.708903	[]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
task22	膀胱CT标注任务010-打回后重启	被审核打回后，重新开始	proj1	pending	medium	\N	user1	/api/images/bladder010.jpg	\N	\N	\N	\N	\N	\N	\N	2025-08-29 09:12:58.092482	2025-10-16 06:56:25.259962	[{"time": "2024-12-05T08:00:00", "type": "created", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2024-12-05T09:00:00", "type": "claimed", "user_id": "user3", "user_name": "李医生"}, {"time": "2024-12-06T09:00:00", "type": "submitted", "comment": "已完成", "user_id": "user3", "user_name": "李医生"}, {"time": "2024-12-06T10:00:00", "type": "reviewed", "action": "reject", "comment": "边界不清晰", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2024-12-07T09:00:00", "type": "restarted", "user_id": "user3", "user_name": "李医生"}]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
task4	肾脏CT标注任务004	标注右肾CT影像中的囊肿区域	proj1	pending	medium	\N	user1	/api/images/kidney004.jpg	\N	45	\N	\N	\N	\N	\N	2025-08-29 09:12:58.092482	2025-10-16 06:56:25.259962	[{"time": "2024-12-01T10:00:00", "type": "created", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2024-12-03T09:00:00", "type": "claimed", "user_id": "user3", "user_name": "李医生"}, {"time": "2024-12-03T09:30:00", "type": "started", "comment": "开始标注右肾囊肿区域", "user_id": "user3", "user_name": "李医生"}]	\N	\N	\N	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N	\N
task13	积液X光片标注任务005	标注胸部X光片中的胸腔积液区域	proj2	pending	medium	\N	user1	/api/images/chest005.jpg	{"lesions": [{"x": 140, "y": 200, "type": "pleural_effusion"}]}	40	\N	2024-12-10 16:30:00	user1	2025-10-09 15:32:21.720313	完美	2025-08-29 09:12:58.092482	2025-10-16 06:56:25.259962	[{"time": "2024-12-05T11:30:00", "type": "created", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2024-12-07T14:00:00", "type": "claimed", "user_id": "user3", "user_name": "李医生"}, {"time": "2024-12-07T14:30:00", "type": "started", "comment": "开始标注胸腔积液区域", "user_id": "user3", "user_name": "李医生"}, {"time": "2024-12-10T16:30:00", "type": "submitted", "comment": "已完成胸腔积液区域标注，请审核", "user_id": "user3", "user_name": "李医生", "organ_count": 1}, {"time": "2025-10-09T15:32:21.720313", "type": "reviewed", "score": null, "action": "reject", "comment": "完美", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	\N	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
task10	结核X光片标注任务002	标注胸部X光片中的结核病变区域	proj2	approved	high	\N	user1	/api/images/chest002.jpg	{"lesions": [{"x": 180, "y": 160, "type": "tuberculosis"}]}	60	\N	2024-12-08 16:30:00	user1	2024-12-08 16:30:00	标注详细，质量良好	2025-08-29 09:12:58.092482	2025-10-16 06:56:25.259962	[]	\N	\N	\N	李医生	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
task9	肺炎X光片标注任务001	标注胸部X光片中的肺炎病变区域	proj2	approved	high	\N	user1	/api/images/chest001.jpg	{"lesions": [{"x": 120, "y": 200, "type": "pneumonia"}]}	50	\N	2024-12-07 15:45:00	user1	2024-12-07 15:45:00	标注准确	2025-08-29 09:12:58.092482	2025-10-16 06:56:25.259962	[]	\N	\N	\N	李医生	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
task12	气胸X光片标注任务004	标注胸部X光片中的气胸区域	proj2	approved	medium	\N	user1	/api/images/chest004.jpg	{"lesions": [{"x": 160, "y": 140, "type": "pneumothorax"}]}	45	\N	2024-12-09 14:20:00	user1	2024-12-09 15:00:00	气胸区域标注准确	2025-08-29 09:12:58.092482	2025-10-16 07:01:16.184102	[{"time": "2024-12-05T11:00:00", "type": "created", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2024-12-06T09:30:00", "type": "claimed", "user_id": "user4", "user_name": "王医生"}, {"time": "2024-12-06T10:00:00", "type": "started", "comment": "开始标注气胸区域", "user_id": "user4", "user_name": "王医生"}, {"time": "2024-12-09T14:20:00", "type": "submitted", "comment": "已完成气胸区域标注", "user_id": "user4", "user_name": "王医生", "organ_count": 1}, {"time": "2024-12-09T15:00:00", "type": "reviewed", "score": 4, "action": "approve", "comment": "气胸区域标注准确", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	王医生	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
157cb789-fd87-48b0-a02c-d1cb02476169	张道见	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	approved	high	\N	user1	D:/任务管理测试数据/肝脏/张道见	{"comment": "niudehen\\u81ea\\u5df1\\u770b\\n", "organ_count": 4, "uploaded_images": [], "timestamp": "2025-09-03T07:59:09.271Z", "screenshot_count": 0}	5	2025-09-03 13:53:10.724291	2025-09-03 15:59:09.283256	user1	2025-09-03 15:59:38.845927	行吧	2025-09-02 06:39:58.916713	2025-10-16 07:01:58.184399	[{"time": "2025-09-03T13:53:10.724291", "type": "claimed", "user_id": "user5", "user_name": "王志虎"}, {"time": "2025-09-03T13:53:34.392260", "type": "submitted", "comment": "这还不行，请你来标嘛", "user_id": "user5", "user_name": "王志虎", "organ_count": 1}, {"time": "2025-09-03T13:54:33.341892", "type": "reviewed", "score": null, "action": "reject", "comment": "放屁", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-09-03T15:59:09.283256", "type": "submitted", "comment": "niudehen自己看\\n", "user_id": "user5", "user_name": "王志虎", "organ_count": 1}, {"time": "2025-09-03T15:59:38.845927", "type": "reviewed", "score": 5, "action": "approve", "comment": "行吧", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	王志虎	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
20df8ff4-eab4-4f44-bbc5-69ff992ebe0a	陈永富	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	approved	high	\N	user1	D:/任务管理测试数据/肝脏/陈永富	{"comment": "\\u725b\\u5f97\\u5f88\\u7684\\u6807\\u6ce8\\uff0c\\u81ea\\u5df1\\u770b\\u561b", "organ_count": 3, "uploaded_images": [], "timestamp": "2025-09-03T03:59:03.813Z", "screenshot_count": 0}	5	2025-09-03 09:11:43.288167	2025-09-03 11:59:03.824772	user1	2025-09-03 11:59:45.849922	还行	2025-09-02 06:39:58.916713	2025-10-16 07:01:58.184399	[{"time": "2025-09-03T09:11:43.288167", "type": "claimed", "user_id": "user5", "user_name": "王志虎"}, {"time": "2025-09-03T11:59:03.824772", "type": "submitted", "comment": "牛得很的标注，自己看嘛", "user_id": "user5", "user_name": "王志虎", "organ_count": 3}, {"time": "2025-09-03T11:59:45.849922", "type": "reviewed", "score": 5, "action": "approve", "comment": "还行", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	王志虎	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
24c243c6-7bca-4e28-80b8-f855ddc7e09d	雷青松	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	approved	high	\N	user1	D:/任务管理测试数据/肝脏/雷青松	{"comment": "\\u4f60\\u6765\\u6807\\u561b\\uff0c\\u7edd\\u5bf9\\u4e0d\\u5982\\u6211", "organ_count": 4, "uploaded_images": [], "timestamp": "2025-09-03T07:59:24.487Z", "screenshot_count": 0}	5	2025-09-03 11:58:48.136972	2025-09-03 15:59:24.49899	user1	2025-09-03 15:59:45.636934	还行	2025-09-02 06:39:58.916713	2025-10-16 07:01:58.184399	[{"time": "2025-09-03T11:58:48.136972", "type": "claimed", "user_id": "user5", "user_name": "王志虎"}, {"time": "2025-09-03T12:01:16.049318", "type": "submitted", "comment": "牛得很的标注，自己看", "user_id": "user5", "user_name": "王志虎", "organ_count": 1}, {"time": "2025-09-03T13:01:10.577733", "type": "reviewed", "score": null, "action": "reject", "comment": "bux", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-09-03T15:59:24.498990", "type": "submitted", "comment": "你来标嘛，绝对不如我", "user_id": "user5", "user_name": "王志虎", "organ_count": 1}, {"time": "2025-09-03T15:59:45.636934", "type": "reviewed", "score": 5, "action": "approve", "comment": "还行", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	王志虎	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
16146129-de9a-4f16-a0a0-76f774183ea8	谢安相	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	approved	high	\N	user1	D:/任务管理测试数据/肝脏/谢安相	{"comment": "\\u4f60\\u6765\\u561b\\uff0c\\u4f60\\u884c\\uff0c\\u4f60\\u6807\\u4e00\\u4e2a\\u770b\\u770b", "organ_count": 1, "uploaded_images": ["http://localhost:9000/medical-annotations/annotations/16146129-de9a-4f16-a0a0-76f774183ea8/e7865657-a40b-4dd1-b377-d3ec56ba68cf.png"], "timestamp": "2025-09-02T09:09:43.682Z", "screenshot_count": 1}	5	2025-09-02 17:07:17.130832	2025-09-02 17:09:43.721272	user1	2025-09-02 17:10:11.666541	算你合格得了	2025-09-02 06:39:58.916713	2025-10-16 07:12:54.918548	[{"time": "2025-09-02T17:07:17.130832", "type": "claimed", "user_id": "user2", "user_name": "张医生"}, {"time": "2025-09-02T17:08:09.309355", "type": "submitted", "comment": "标注难度很大，不准找茬", "user_id": "user2", "user_name": "张医生", "organ_count": 4}, {"time": "2025-09-02T17:08:51.163153", "type": "reviewed", "score": null, "action": "reject", "comment": "标注的狗屎", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-09-02T17:09:43.721272", "type": "submitted", "comment": "你来嘛，你行，你标一个看看", "user_id": "user2", "user_name": "张医生", "organ_count": 1}, {"time": "2025-09-02T17:10:11.666541", "type": "reviewed", "score": 5, "action": "approve", "comment": "算你合格得了", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	张医生	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
task3	输尿管CT标注任务003	标注输尿管CT影像中的狭窄区域	proj1	approved	high	\N	user1	/api/images/ureter003.jpg	{"lesions": [{"x": 150, "y": 120, "type": "stricture"}]}	60	\N	2024-12-05 11:20:00	user1	2024-12-05 11:20:00	标注详细，质量优秀	2025-08-29 09:12:58.092482	2025-10-16 07:12:54.918548	[{"time": "2024-12-01T09:30:00", "type": "created", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2024-12-02T14:00:00", "type": "claimed", "user_id": "user2", "user_name": "张医生"}, {"time": "2024-12-05T11:00:00", "type": "submitted", "comment": "已完成输尿管狭窄区域标注", "user_id": "user2", "user_name": "张医生", "organ_count": 1}, {"time": "2024-12-05T11:20:00", "type": "reviewed", "score": 5, "action": "approve", "comment": "标注详细，质量优秀", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	张医生	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
90a4d30e-4d50-4543-adee-9932bca548d6	JiaRonghui	2025第四次泌尿标注任务	proj2025301	approved	medium	user1	user1	E:/训练留档/泌尿导出/JiaRonghui	{"comment": "\\u81ea\\u5df1\\u770b\\u770b\\u65b9\\u6cd5\\u7ed9\\u53d1\\u4e2a\\u516c\\u544a", "organ_count": 1, "uploaded_images": ["http://192.168.200.20:9000/medical-annotations/annotations/90a4d30e-4d50-4543-adee-9932bca548d6/dd0588d4-806a-46e1-9cc4-c933a28022ae.png"], "timestamp": "2025-10-09T08:31:01.631Z", "screenshot_count": 1}	5	2025-10-09 16:24:21.457905	2025-10-09 16:31:01.657999	user1	2025-10-17 14:32:27.808114		2025-09-04 02:13:24.321151	2025-10-17 06:32:27.767709	[{"time": "2025-10-09T16:24:21.457905", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T16:24:28.305858", "type": "submitted", "comment": "超哥开了三个小时 最后三个小时我一百四五的开", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-09T16:25:06.946853", "type": "reviewed", "score": null, "action": "reject", "comment": "超哥开了三个小时 最后三个小时我一百四五的开", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T16:31:01.657999", "type": "submitted", "comment": "自己看看方法给发个公告", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-17T14:32:27.808114", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	系统管理员	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N
abee54a1-08c4-481f-b767-43843b323f7d	KongDegui	2025第四次泌尿标注任务	proj2025301	approved	medium	user1	user1	E:/训练留档/泌尿导出/KongDegui	{"comment": "\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u70e6\\u53d1\\u751f", "organ_count": 1, "uploaded_images": ["http://192.168.200.20:9000/medical-annotations/annotations/abee54a1-08c4-481f-b767-43843b323f7d/a059a6e1-b10e-4561-a71e-afe9e89a8485.png"], "timestamp": "2025-10-09T09:26:12.879Z", "screenshot_count": 1}	5	2025-10-09 17:26:00.289419	2025-10-09 17:26:12.886003	user1	2025-10-17 14:32:31.896891		2025-09-04 02:13:24.321151	2025-10-17 06:32:31.858819	[{"time": "2025-10-09T17:26:00.289419", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T17:26:12.886003", "type": "submitted", "comment": "烦烦烦烦烦烦烦烦烦烦烦烦烦烦烦发生", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-17T14:32:31.896891", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	系统管理员	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N
303e3b52-370c-4d52-87ec-1cf8633f8665	JiangWei	2025第四次泌尿标注任务	proj2025301	approved	medium	user1	user1	E:/训练留档/泌尿导出/JiangWei	{"comment": "chongx itjiao dfasfsa", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-10T02:33:03.967Z", "screenshot_count": 0}	5	2025-09-04 15:58:58.217229	2025-10-10 10:33:03.978453	user1	2025-10-17 14:32:58.20045		2025-09-04 02:13:24.321151	2025-10-17 06:32:58.169761	[{"time": "2025-09-04T15:58:58.217229", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-09-04T16:01:06.951227", "type": "submitted", "comment": "fjhyfjhfjfjdhgdgfsfg", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-09-04T16:02:16.908224", "type": "reviewed", "score": null, "action": "reject", "comment": "1111", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T15:33:12.692439", "type": "submitted", "comment": "完美了还标水水水水水水水水", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-09T17:24:32.810971", "type": "reviewed", "score": null, "action": "reject", "comment": "重新来", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-10T10:33:03.978453", "type": "submitted", "comment": "chongx itjiao dfasfsa", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-17T14:32:58.200450", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	系统管理员	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N
d392e9d3-cc8c-4e26-bdc7-a8e1585e95b5	JinMingsheng	2025第四次泌尿标注任务	proj2025301	approved	medium	user1	user1	E:/训练留档/泌尿导出/JinMingsheng	{"comment": "index.vue:938 \\ud83d\\udccb [TaskReview] \\u83b7\\u53d6\\u4efb\\u52a1\\u5217\\u8868\\u5f00\\u59cb\\nindex.vue:965 \\ud83d\\udcca [TaskReview] \\u67e5\\u8be2\\u53c2\\u6570: {page: 1, pageSize: 20, status: Array(4), isReviewPage: true}\\nproject.ts:162 \\ud83d\\udccb [ProjectStore] \\u83b7\\u53d6\\u4efb\\u52a1\\u5217\\u8868: {page: 1, pageSize: 20, status: Array(4), isReviewPage: true}\\nprojectApi.ts?t=1760000436716:232 \\ud83c\\udfaf [ProjectAPI] \\u8c03\\u7528\\u771f\\u5b9eAPI\\u83b7\\u53d6\\u4efb\\u52a1: {page: 1, pageSize: 20, status: Array(4), isReviewPage: true}\\nprojectApi.ts?t=1760000436716:257 \\ud83d\\udd04 [ProjectAPI] \\u8f6c\\u6362\\u540e\\u7684\\u540e\\u7aef\\u53c2\\u6570: {status: 'submitted', skip: 0, limit: 20}\\nbackendApi.ts:140 \\ud83d\\udce1 [BackendAPI]", "organ_count": 1, "uploaded_images": ["http://192.168.200.20:9000/medical-annotations/annotations/d392e9d3-cc8c-4e26-bdc7-a8e1585e95b5/8ccf100b-6055-42ce-ad2e-7b645a53db40.png"], "timestamp": "2025-10-09T09:27:11.778Z", "screenshot_count": 1}	5	2025-10-09 17:27:01.255285	2025-10-09 17:27:11.786672	user1	2025-10-17 14:32:34.049265		2025-09-04 02:13:24.321151	2025-10-17 06:32:34.017545	[{"time": "2025-10-09T17:27:01.255285", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T17:27:11.786672", "type": "submitted", "comment": "index.vue:938 📋 [TaskReview] 获取任务列表开始\\nindex.vue:965 📊 [TaskReview] 查询参数: {page: 1, pageSize: 20, status: Array(4), isReviewPage: true}\\nproject.ts:162 📋 [ProjectStore] 获取任务列表: {page: 1, pageSize: 20, status: Array(4), isReviewPage: true}\\nprojectApi.ts?t=1760000436716:232 🎯 [ProjectAPI] 调用真实API获取任务: {page: 1, pageSize: 20, status: Array(4), isReviewPage: true}\\nprojectApi.ts?t=1760000436716:257 🔄 [ProjectAPI] 转换后的后端参数: {status: 'submitted', skip: 0, limit: 20}\\nbackendApi.ts:140 📡 [BackendAPI]", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-17T14:32:34.049265", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	系统管理员	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N
4ed39bcd-bed8-4db7-bf76-2258c69b4929	贺琴	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	approved	high	user1	user1	D:/任务管理测试数据/肝脏/贺琴	{"comment": "dadfwqnlfqnwlkfdqlhwoi", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-10T01:11:31.725Z", "screenshot_count": 0}	5	2025-10-10 09:11:11.67704	2025-10-10 09:11:31.738436	user1	2025-10-17 14:32:43.104014		2025-09-02 06:39:58.916713	2025-10-17 06:32:43.120204	[{"time": "2025-10-10T09:11:11.677040", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-10T09:11:31.738436", "type": "submitted", "comment": "dadfwqnlfqnwlkfdqlhwoi", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-17T14:32:43.104014", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	系统管理员	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
5109f891-0c83-4f87-81a1-3973bcfa9d4a	董沁柚	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	approved	high	user1	user1	D:/任务管理测试数据/肝脏/董沁柚	{"comment": "\\u591a\\u4e45\\u54e6i\\u6211\\u8fd8oh\\u5e74\\u9f84\\u4eba\\u53e3\\u77a7\\u4e0d\\u8d77\\u6211\\u4e86\\u5c31", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-10T01:12:41.654Z", "screenshot_count": 0}	5	2025-10-10 09:12:29.20053	2025-10-10 09:12:41.667738	user1	2025-10-17 14:32:45.758397		2025-09-02 06:39:58.916713	2025-10-17 06:32:45.790766	[{"time": "2025-10-10T09:12:29.200530", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-10T09:12:41.667738", "type": "submitted", "comment": "多久哦i我还oh年龄人口瞧不起我了就", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-17T14:32:45.758397", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	系统管理员	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
4f399004-28f0-4ccc-92c6-94de9f92df8b	AnDing	2025第四次泌尿标注任务	proj2025301	approved	medium	user1	user1	E:/训练留档/泌尿导出/AnDing	{"comment": ";ljphjqwdqwdqwd", "organ_count": 1, "uploaded_images": [], "timestamp": "2025-10-10T02:21:15.109Z", "screenshot_count": 0}	5	2025-10-09 17:35:09.609853	2025-10-10 10:21:15.119822	user1	2025-10-17 14:32:55.799752		2025-09-04 02:13:24.321151	2025-10-17 06:32:55.772882	[{"time": "2025-10-09T17:35:09.609853", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T17:35:28.350436", "type": "submitted", "comment": "akjhdkahwiokyrhwoqaihnrklqtttqwtwq", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-10T10:20:34.766491", "type": "reviewed", "score": null, "action": "reject", "comment": "bmcnbvvkvkj", "user_id": "user6", "user_name": "代雨昕"}, {"time": "2025-10-10T10:21:15.119822", "type": "submitted", "comment": ";ljphjqwdqwdqwd", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-17T14:32:55.799752", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	系统管理员	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N
187505fa-49e5-4bcc-b6e5-6a7343a5b52c	孙朝军	请输入任务描述大大大	f8b89026-2a33-424f-96e3-7e9d2ac5379d	approved	high	user1	user1	D:/任务管理测试数据/肝脏/孙朝军	{"comment": "", "organ_count": 1, "uploaded_images": ["http://192.168.200.20:9000/medical-annotations/annotations/187505fa-49e5-4bcc-b6e5-6a7343a5b52c/0c333f6e-b5ab-4778-a9d2-ea3e16a6994e.png"], "timestamp": "2025-10-17T08:12:50.088Z", "screenshot_count": 1}	5	2025-10-10 10:12:06.747767	2025-10-17 16:12:50.098367	user1	2025-10-17 16:12:59.582159		2025-09-02 06:39:58.916713	2025-10-17 08:12:59.6003	[{"time": "2025-10-10T10:12:06.747767", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-10T10:12:20.535743", "type": "submitted", "comment": "n k,ghreilodyquwuholehqwiklr", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-10T10:20:40.575650", "type": "reviewed", "score": null, "action": "reject", "comment": "n b bcnmbn,knl.kn;ln", "user_id": "user6", "user_name": "代雨昕"}, {"time": "2025-10-17T16:12:50.098367", "type": "submitted", "comment": "标注已完成", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-17T16:12:59.582159", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	系统管理员	系统管理员	系统管理员	\N	\N	\N	\N	\N	\N	\N
d4b4b038-9bbb-4937-a2fb-31ebcf55e9ba	KuangNailan	2025第四次泌尿标注任务	proj2025301	approved	medium	user1	user1	E:/训练留档/泌尿导出/KuangNailan	{"comment": "", "organ_count": 1, "uploaded_images": ["http://192.168.200.20:9000/medical-annotations/annotations/d4b4b038-9bbb-4937-a2fb-31ebcf55e9ba/cba8c6d1-5a69-419b-966d-baa5de6f6d8e.png"], "timestamp": "2025-10-17T08:12:40.278Z", "screenshot_count": 1}	5	2025-10-09 16:19:20.209726	2025-10-17 16:12:40.286437	user1	2025-10-17 16:13:02.117438		2025-09-04 02:13:24.321151	2025-10-17 08:13:02.150692	[{"time": "2025-10-09T16:19:20.209726", "type": "claimed", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T16:19:46.651881", "type": "submitted", "comment": "超哥开了三个小时 最后三个小时我一百四五的开", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-09T17:17:02.960718", "type": "reviewed", "score": null, "action": "reject", "comment": "支气管有大问题", "user_id": "user1", "user_name": "系统管理员"}, {"time": "2025-10-09T17:25:13.064091", "type": "submitted", "comment": "你看看呢测试一下法案嘎嘎嘎嘎嘎嘎", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-10T10:20:27.088048", "type": "reviewed", "score": null, "action": "reject", "comment": "mjv nb nmbn.,m,.", "user_id": "user6", "user_name": "代雨昕"}, {"time": "2025-10-17T16:12:40.286437", "type": "submitted", "comment": "标注已完成", "user_id": "user1", "user_name": "系统管理员", "organ_count": 1}, {"time": "2025-10-17T16:13:02.117438", "type": "reviewed", "score": 5, "action": "approve", "comment": "", "user_id": "user1", "user_name": "系统管理员"}]	\N	\N	\N	系统管理员	\N	系统管理员	\N	\N	\N	\N	\N	\N	\N
\.


--
-- TOC entry 3641 (class 0 OID 24969)
-- Dependencies: 228
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.users (id, username, real_name, email, password_hash, role, avatar_url, department, status, created_at, updated_at, tags, hire_date) FROM stdin;
user8	whh	王欢欢	whh@xxjz.com	$2b$12$n6JbwS0e1mXWFup./aLTDeMbOTUhfjFYKHTcSYrqopuYlfPXxDro2	annotator	/api/files/avatars/user8.png	研发部标注组	active	2025-10-10 02:35:54.101023	2025-10-13 10:11:19.268609	["专注设计", "很有想法", "辣~", "大长腿", "川妹子", "海纳百川"]	2025-08-29
user11	deptest	开发测试	deptest@xxjz.com	$2b$12$dlyzq8DA2b6f.wUVPKLMfeiYykfM8UbGQcTm08LPqsGBgKdPhqqS2	development	\N	研发部开发组	active	2025-10-16 08:35:03.476848	2025-10-16 08:35:03.476848	\N	2025-10-16
user10	xztest	行政测试	xztest@xxjz.com	$2b$12$bNeLoknCoJ5IJBRsQBnAmuAq2FZceaN7CSUqIj0ZjZs0NGdV3BAsW	executive	http://192.168.200.20:9000/medical-annotations/avatars/user10.png	星像行政部门	active	2025-10-16 08:33:44.983219	2025-10-16 08:38:15.140989	\N	2025-10-16
user9	zmh	张洺恒	zmh@xxjz.com	$2b$12$7BifwItvTYuw9RGIEIlV6O3MSZ4vrmDhv9M.SeEl4QOHhvO.VKmp6	admin	\N	研发部算法组	active	2025-10-16 07:53:55.710264	2025-10-16 08:40:20.305472	\N	2025-10-16
user12	cxh	陈显慧	cxh@xxjz.com	$2b$12$sd8Di8yx26ciMS7dTerKvOosMmTOF9290nGcGXUSI8cFmLp4aybyK	annotator	\N	研发部标注组	active	2025-10-16 08:41:21.319592	2025-10-16 08:41:21.319592	\N	2025-10-16
user13	gyf	龚奕菲	gyf@xxjz.com	$2b$12$lwdnlUnrEJRQxhlfS0UIne/aLQcH.fqfOjvBkttd6C2VQ5O/3BhyG	annotator	\N	研发部标注组	active	2025-10-16 08:42:09.207121	2025-10-16 08:42:09.207121	\N	2025-10-16
user14	wmz	王民昭	wmz@xxjz.com	$2b$12$5H71TighdKJHMhL2muQbOeRciKizdleK34kbTVEmWO2Wo6Dd6R8RO	annotator	\N	研发部标注组	active	2025-10-16 08:42:59.433092	2025-10-16 08:42:59.433092	\N	2025-10-16
user15	qc	邱诚	qc@xxjz.com	$2b$12$docI3rhHE.My5a4tPlGPROhYk3jJDrbNUgLHgXXJ32K3czIr031JW	annotator	\N	研发部标注组	active	2025-10-16 08:43:29.040659	2025-10-16 08:43:29.040659	\N	2025-10-16
user16	zzb	张智斌	zzb@xxjz.com	$2b$12$wMUy9YrI3uEfqkjatdpS1u0mmvqWzLlENhhqPi5ZUDcEVLYH1j6ou	algorithm	\N	研发部算法组	active	2025-10-17 07:27:21.776386	2025-10-17 07:27:21.776386	\N	2025-10-17
user17	wgp	王广鹏	wgb@xxjz.com	$2b$12$Kjsxe/qSOfB6YZYvFvpI5.0Y0TudC79ICj5Q9U2iR53n6fcyuwXGe	algorithm	\N	研发部算法组	active	2025-10-17 07:28:11.171009	2025-10-17 07:28:11.171009	\N	2025-10-17
user18	lxs	李兴顺	lxs@xxjz.com	$2b$12$T7Be1Nh2Jj5EzHa0TYnZNuaIJxdnXmgnaa2OE8ztqaO7F.cROKjLO	development	\N	研发部开发组	active	2025-10-17 07:29:25.628279	2025-10-17 07:29:25.628279	\N	2025-10-17
user1	admin	系统管理员	admin@example.com	$2b$12$8uEBXrcG0bHXwO2nQY/nPObXR3lu7CAYDNwnowrzikqyck1CDsMFS	admin	http://192.168.200.20:9000/medical-annotations/avatars/user1.png	星像行政部门	active	2025-08-29 09:12:58.092482	2025-10-13 06:00:06.117809	["专注工作", "积极向上", "团队协作", "帅逼", "大帅逼"]	2025-08-29
user6	dyx	代雨昕	dyx@xxjz.com	$2b$12$wORI0qB1eJDRnIhnTP6YM.zVY1AMtDvJ9QO06pqym2mmG1M089/tW	admin	\N	研发部标注组	active	2025-09-03 07:18:45.930529	2025-10-13 08:04:06.091954	["专注工作", "积极向上", "团队协作"]	2025-09-03
\.


--
-- TOC entry 3642 (class 0 OID 24976)
-- Dependencies: 229
-- Data for Name: work_log_entries; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.work_log_entries (id, work_week_id, user_id, work_date, day_of_week, work_content, work_type, priority, planned_hours, actual_hours, status, completion_rate, difficulties, next_day_plan, remarks, submitted_at, reviewed_at, reviewed_by, review_comment, created_at, updated_at) FROM stdin;
c906824b-3fba-4aca-8a31-195b299c67d4	e7a16135-9bbd-406b-8687-06e5a0e16b19	user1	2025-11-02	7	20241201_泌尿系统CT标注项目|相关文章：# nnUNet 模型测试文档\n链接：http://localhost:3006/login#/articles/meeting?articleId=b8a500fe-923d-405a-a8f6-f5835b2d9b9f	文档	normal	2	2	pending	100				\N	\N	\N	\N	2025-10-17 06:47:50.552738	2025-10-17 06:47:50.552738
3fb642d7-ebcb-49be-97b9-479229df0841	e7a16135-9bbd-406b-8687-06e5a0e16b19	user1	2025-11-02	7	Bug修复与优化|修复关键bug	开发	normal	2	2	pending	100				\N	\N	\N	\N	2025-10-17 06:50:07.170039	2025-10-17 06:50:07.170039
e8cd6451-d43d-4dd5-9397-f27aa0163afd	e7a16135-9bbd-406b-8687-06e5a0e16b19	user1	2025-11-03	1	日常标注工作|完成肝胆器官标注\n	标注	normal	2	2	pending	100				\N	\N	\N	\N	2025-10-17 06:52:30.013483	2025-10-17 06:52:30.013483
d04bfca1-2111-465b-ab4b-dad58d96afa2	e7a16135-9bbd-406b-8687-06e5a0e16b19	user1	2025-11-03	1	20250904泌尿CT标注任务|简单的日常宝珠	标注	normal	4	4	pending	100				\N	\N	\N	\N	2025-10-17 06:56:40.750426	2025-10-17 06:56:40.750426
99595de1-2646-4046-a87b-ca506b218775	e7a16135-9bbd-406b-8687-06e5a0e16b19	user1	2025-11-03	1	需求评审与讨论|评审代码	开发	normal	2	2	pending	100				\N	\N	\N	\N	2025-10-17 07:18:58.78689	2025-10-17 07:18:58.78689
0dd1ca40-beeb-43bd-aa57-47971d49006b	e7a16135-9bbd-406b-8687-06e5a0e16b19	user9	2025-11-02	7	模型测试与验证|泌尿模型测试工作	测试	normal	2	2	pending	100				\N	\N	\N	\N	2025-10-17 07:20:01.487261	2025-10-17 07:20:01.487261
\.


--
-- TOC entry 3643 (class 0 OID 24981)
-- Dependencies: 230
-- Data for Name: work_log_types; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.work_log_types (id, name, description, color, icon, is_active, sort_order, created_at, updated_at) FROM stdin;
568ab9d3-1691-4edf-bb01-a3a33fe8caae	开发	软件开发相关工作	#67C23A	Code	t	1	2025-09-05 17:51:48.791971	2025-09-05 17:51:48.791971
7df26ba1-2140-4ebb-b752-09f86e134c29	测试	软件测试相关工作	#E6A23C	TestTube	t	2	2025-09-05 17:51:48.794972	2025-09-05 17:51:48.794972
a6702152-3e5a-4e4f-95d9-17648a6b9674	会议	各类会议和讨论	#409EFF	Meeting	t	3	2025-09-05 17:51:48.794972	2025-09-05 17:51:48.794972
ef93c260-21c6-4d3b-9dae-3a50b7860153	学习	技术学习和培训	#9C27B0	Reading	t	4	2025-09-05 17:51:48.795971	2025-09-05 17:51:48.795971
d28ba256-979f-4bce-95b7-e603a835eb06	文档	文档编写和整理	#FF9800	Document	t	5	2025-09-05 17:51:48.795971	2025-09-05 17:51:48.795971
5303ca2c-e579-496a-a36c-b24ff83d10df	其他	其他工作内容	#909399	More	t	6	2025-09-05 17:51:48.796978	2025-09-05 17:51:48.796978
\.


--
-- TOC entry 3644 (class 0 OID 24986)
-- Dependencies: 231
-- Data for Name: work_weeks; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.work_weeks (id, title, week_start_date, week_end_date, description, status, config, created_by, created_at, updated_at) FROM stdin;
0ae392c1-3666-4c2c-a863-507382d03862	2025W45标注组工作计划	2025-11-02	2025-11-06	\N	active	{"covered_user_ids": ["user6", "user8", "user12", "user13", "user14", "user15"]}	user1	2025-10-17 03:26:06.561483	2025-10-17 03:26:06.561483
32a4dbb2-efb3-4c0b-8df0-b4b487101151	2025W46算法组工作计划	2025-11-09	2025-11-13	\N	active	{"covered_user_ids": ["user8", "user1", "user9"]}	user1	2025-10-17 03:33:09.138128	2025-10-17 03:33:09.138128
e6d19c67-9d3b-4b24-b97e-7c83f77808cd	2025W47算法组工作计划	2025-11-16	2025-11-20	\N	active	{"covered_user_ids": ["user8", "user1", "user9"]}	user1	2025-10-17 03:33:09.15995	2025-10-17 03:33:09.15995
ee524329-8c09-4717-9724-2b1b1728bdb2	2025W48算法组工作计划	2025-11-23	2025-11-27	\N	active	{"covered_user_ids": ["user8", "user1", "user9"]}	user1	2025-10-17 03:33:09.179226	2025-10-17 03:33:09.179226
df899cc7-4d10-425d-baeb-2d6e91e31352	2025W49算法组工作计划	2025-11-30	2025-12-04	\N	active	{"covered_user_ids": ["user8", "user1", "user9"]}	user1	2025-10-17 03:33:09.198165	2025-10-17 03:33:09.198165
7f898c31-bf1d-463d-a84f-9ed354eac9c3	2025W42算法组工作计划	2025-10-12	2025-10-16	\N	active	{"covered_user_ids": ["user1", "user9"]}	user1	2025-10-17 03:36:52.581063	2025-10-17 03:36:52.581063
9c7b9719-bcf6-4061-8137-30fb2d4e6ff4	2025W43算法组工作计划	2025-10-19	2025-10-23	\N	active	{"covered_user_ids": ["user1", "user9"]}	user1	2025-10-17 03:36:52.601536	2025-10-17 03:36:52.601536
c448bf36-660a-4aff-ae87-0dc5f478091c	2025W44算法组工作计划	2025-10-26	2025-10-30	\N	active	{"covered_user_ids": ["user1", "user9"]}	user1	2025-10-17 03:36:52.618033	2025-10-17 03:36:52.618033
c208fe91-4bee-4b1f-a3ec-2f7db08c0efb	2025W42标注组工作计划	2025-10-12	2025-10-16	\N	active	{"covered_user_ids": ["user6", "user8", "user12", "user13", "user14", "user15"]}	user1	2025-10-17 03:26:06.502977	2025-10-17 03:26:06.502977
048c5c97-7f93-4e90-ab1b-0d5266ac97a0	2025W43标注组工作计划	2025-10-19	2025-10-23	\N	active	{"covered_user_ids": ["user6", "user8", "user12", "user13", "user14", "user15"]}	user1	2025-10-17 03:26:06.521595	2025-10-17 03:26:06.521595
d253d4b5-3882-4b6b-a8de-3434231f04aa	2025W44标注组工作计划	2025-10-26	2025-10-30	\N	active	{"covered_user_ids": ["user6", "user8", "user12", "user13", "user14", "user15"]}	user1	2025-10-17 03:26:06.541834	2025-10-17 03:26:06.541834
e7a16135-9bbd-406b-8687-06e5a0e16b19	2025W45算法组工作计划	2025-11-02	2025-11-06	\N	active	{"covered_user_ids": ["user1", "user9"]}	user1	2025-10-17 03:36:52.633945	2025-10-17 03:36:52.633945
7e4ebc8a-42b1-4845-a50c-94bb6d6872b6	2025W46算法组工作计划(2)	2025-11-09	2025-11-13	\N	active	{"covered_user_ids": ["user1", "user9"]}	user1	2025-10-17 06:57:27.161745	2025-10-17 06:57:27.161745
4f43d273-68f7-4d98-9372-9828904c11d2	2025W47算法组工作计划(2)	2025-11-16	2025-11-20	\N	active	{"covered_user_ids": ["user1", "user9"]}	user1	2025-10-17 06:57:27.184805	2025-10-17 06:57:27.184805
59787dac-c5ef-40e0-a3b2-ecc74e0df776	2025W48算法组工作计划(2)	2025-11-23	2025-11-27	\N	active	{"covered_user_ids": ["user1", "user9"]}	user1	2025-10-17 06:57:27.201269	2025-10-17 06:57:27.201269
184449e4-8d44-4281-8e45-3a45a6eeb9eb	2025W49算法组工作计划(2)	2025-11-30	2025-12-04	\N	active	{"covered_user_ids": ["user9", "user16", "user17", "user1"]}	user1	2025-10-17 06:57:27.21748	2025-10-17 15:37:10.338447
\.


--
-- TOC entry 3378 (class 2606 OID 24997)
-- Name: article_edit_history article_edit_history_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.article_edit_history
    ADD CONSTRAINT article_edit_history_pkey PRIMARY KEY (id);


--
-- TOC entry 3380 (class 2606 OID 24999)
-- Name: articles articles_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_pkey PRIMARY KEY (id);


--
-- TOC entry 3386 (class 2606 OID 25001)
-- Name: collaboration_documents collaboration_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.collaboration_documents
    ADD CONSTRAINT collaboration_documents_pkey PRIMARY KEY (id);


--
-- TOC entry 3395 (class 2606 OID 25003)
-- Name: collaboration_sessions collaboration_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.collaboration_sessions
    ADD CONSTRAINT collaboration_sessions_pkey PRIMARY KEY (id);


--
-- TOC entry 3401 (class 2606 OID 25005)
-- Name: document_collaborators document_collaborators_document_id_user_id_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.document_collaborators
    ADD CONSTRAINT document_collaborators_document_id_user_id_key UNIQUE (document_id, user_id);


--
-- TOC entry 3403 (class 2606 OID 25007)
-- Name: document_collaborators document_collaborators_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.document_collaborators
    ADD CONSTRAINT document_collaborators_pkey PRIMARY KEY (id);


--
-- TOC entry 3408 (class 2606 OID 25009)
-- Name: document_comments document_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.document_comments
    ADD CONSTRAINT document_comments_pkey PRIMARY KEY (id);


--
-- TOC entry 3413 (class 2606 OID 25011)
-- Name: document_edit_history document_edit_history_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.document_edit_history
    ADD CONSTRAINT document_edit_history_pkey PRIMARY KEY (id);


--
-- TOC entry 3419 (class 2606 OID 25013)
-- Name: performance_stats performance_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.performance_stats
    ADD CONSTRAINT performance_stats_pkey PRIMARY KEY (id);


--
-- TOC entry 3457 (class 2606 OID 49162)
-- Name: project_categories project_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.project_categories
    ADD CONSTRAINT project_categories_pkey PRIMARY KEY (id);


--
-- TOC entry 3421 (class 2606 OID 25015)
-- Name: project_stats project_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.project_stats
    ADD CONSTRAINT project_stats_pkey PRIMARY KEY (id);


--
-- TOC entry 3424 (class 2606 OID 25017)
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- TOC entry 3428 (class 2606 OID 25019)
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- TOC entry 3430 (class 2606 OID 25021)
-- Name: task_attachments task_attachments_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.task_attachments
    ADD CONSTRAINT task_attachments_pkey PRIMARY KEY (id);


--
-- TOC entry 3433 (class 2606 OID 25023)
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- TOC entry 3437 (class 2606 OID 25025)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 3443 (class 2606 OID 25027)
-- Name: work_log_entries work_log_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.work_log_entries
    ADD CONSTRAINT work_log_entries_pkey PRIMARY KEY (id);


--
-- TOC entry 3446 (class 2606 OID 25029)
-- Name: work_log_types work_log_types_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.work_log_types
    ADD CONSTRAINT work_log_types_pkey PRIMARY KEY (id);


--
-- TOC entry 3451 (class 2606 OID 25031)
-- Name: work_weeks work_weeks_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.work_weeks
    ADD CONSTRAINT work_weeks_pkey PRIMARY KEY (id);


--
-- TOC entry 3381 (class 1259 OID 32771)
-- Name: idx_articles_is_locked; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_articles_is_locked ON public.articles USING btree (is_locked);


--
-- TOC entry 3382 (class 1259 OID 32772)
-- Name: idx_articles_locked_by; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_articles_locked_by ON public.articles USING btree (locked_by);


--
-- TOC entry 3383 (class 1259 OID 40960)
-- Name: idx_articles_project_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_articles_project_id ON public.articles USING btree (project_id);


--
-- TOC entry 3384 (class 1259 OID 40961)
-- Name: idx_articles_project_type; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_articles_project_type ON public.articles USING btree (project_id, type);


--
-- TOC entry 3387 (class 1259 OID 25032)
-- Name: idx_collaboration_documents_category; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_collaboration_documents_category ON public.collaboration_documents USING btree (category);


--
-- TOC entry 3388 (class 1259 OID 25033)
-- Name: idx_collaboration_documents_created; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_collaboration_documents_created ON public.collaboration_documents USING btree (created_at);


--
-- TOC entry 3389 (class 1259 OID 25034)
-- Name: idx_collaboration_documents_owner; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_collaboration_documents_owner ON public.collaboration_documents USING btree (owner_id);


--
-- TOC entry 3390 (class 1259 OID 25035)
-- Name: idx_collaboration_documents_priority; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_collaboration_documents_priority ON public.collaboration_documents USING btree (priority);


--
-- TOC entry 3391 (class 1259 OID 25036)
-- Name: idx_collaboration_documents_project; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_collaboration_documents_project ON public.collaboration_documents USING btree (project_id);


--
-- TOC entry 3392 (class 1259 OID 25037)
-- Name: idx_collaboration_documents_status; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_collaboration_documents_status ON public.collaboration_documents USING btree (status);


--
-- TOC entry 3393 (class 1259 OID 25038)
-- Name: idx_collaboration_documents_updated; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_collaboration_documents_updated ON public.collaboration_documents USING btree (updated_at);


--
-- TOC entry 3396 (class 1259 OID 25039)
-- Name: idx_collaboration_sessions_active; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_collaboration_sessions_active ON public.collaboration_sessions USING btree (is_active);


--
-- TOC entry 3397 (class 1259 OID 25040)
-- Name: idx_collaboration_sessions_document; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_collaboration_sessions_document ON public.collaboration_sessions USING btree (document_id);


--
-- TOC entry 3398 (class 1259 OID 25041)
-- Name: idx_collaboration_sessions_heartbeat; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_collaboration_sessions_heartbeat ON public.collaboration_sessions USING btree (last_heartbeat);


--
-- TOC entry 3399 (class 1259 OID 25042)
-- Name: idx_collaboration_sessions_user; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_collaboration_sessions_user ON public.collaboration_sessions USING btree (user_id);


--
-- TOC entry 3404 (class 1259 OID 25043)
-- Name: idx_document_collaborators_document; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_document_collaborators_document ON public.document_collaborators USING btree (document_id);


--
-- TOC entry 3405 (class 1259 OID 25044)
-- Name: idx_document_collaborators_role; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_document_collaborators_role ON public.document_collaborators USING btree (role);


--
-- TOC entry 3406 (class 1259 OID 25045)
-- Name: idx_document_collaborators_user; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_document_collaborators_user ON public.document_collaborators USING btree (user_id);


--
-- TOC entry 3409 (class 1259 OID 25046)
-- Name: idx_document_comments_document; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_document_comments_document ON public.document_comments USING btree (document_id);


--
-- TOC entry 3410 (class 1259 OID 25047)
-- Name: idx_document_comments_parent; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_document_comments_parent ON public.document_comments USING btree (parent_id);


--
-- TOC entry 3411 (class 1259 OID 25048)
-- Name: idx_document_comments_user; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_document_comments_user ON public.document_comments USING btree (user_id);


--
-- TOC entry 3414 (class 1259 OID 25049)
-- Name: idx_document_edit_history_action; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_document_edit_history_action ON public.document_edit_history USING btree (action);


--
-- TOC entry 3415 (class 1259 OID 25050)
-- Name: idx_document_edit_history_created; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_document_edit_history_created ON public.document_edit_history USING btree (created_at);


--
-- TOC entry 3416 (class 1259 OID 25051)
-- Name: idx_document_edit_history_document; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_document_edit_history_document ON public.document_edit_history USING btree (document_id);


--
-- TOC entry 3417 (class 1259 OID 25052)
-- Name: idx_document_edit_history_editor; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_document_edit_history_editor ON public.document_edit_history USING btree (editor_id);


--
-- TOC entry 3452 (class 1259 OID 49168)
-- Name: idx_project_categories_project_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_project_categories_project_id ON public.project_categories USING btree (project_id);


--
-- TOC entry 3453 (class 1259 OID 49170)
-- Name: idx_project_categories_sort; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_project_categories_sort ON public.project_categories USING btree (project_id, sort_order);


--
-- TOC entry 3454 (class 1259 OID 49169)
-- Name: idx_project_categories_type; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_project_categories_type ON public.project_categories USING btree (project_id, type);


--
-- TOC entry 3455 (class 1259 OID 49171)
-- Name: idx_project_categories_unique_type; Type: INDEX; Schema: public; Owner: admin
--

CREATE UNIQUE INDEX idx_project_categories_unique_type ON public.project_categories USING btree (project_id, type);


--
-- TOC entry 3438 (class 1259 OID 25053)
-- Name: idx_work_log_entries_date; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_work_log_entries_date ON public.work_log_entries USING btree (work_date);


--
-- TOC entry 3439 (class 1259 OID 25054)
-- Name: idx_work_log_entries_status; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_work_log_entries_status ON public.work_log_entries USING btree (status);


--
-- TOC entry 3440 (class 1259 OID 25055)
-- Name: idx_work_log_entries_week_user; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_work_log_entries_week_user ON public.work_log_entries USING btree (work_week_id, user_id);


--
-- TOC entry 3447 (class 1259 OID 25056)
-- Name: idx_work_weeks_dates; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_work_weeks_dates ON public.work_weeks USING btree (week_start_date, week_end_date);


--
-- TOC entry 3448 (class 1259 OID 25057)
-- Name: idx_work_weeks_status; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_work_weeks_status ON public.work_weeks USING btree (status);


--
-- TOC entry 3422 (class 1259 OID 25058)
-- Name: ix_projects_name; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_projects_name ON public.projects USING btree (name);


--
-- TOC entry 3425 (class 1259 OID 25059)
-- Name: ix_roles_name; Type: INDEX; Schema: public; Owner: admin
--

CREATE UNIQUE INDEX ix_roles_name ON public.roles USING btree (name);


--
-- TOC entry 3426 (class 1259 OID 25060)
-- Name: ix_roles_role; Type: INDEX; Schema: public; Owner: admin
--

CREATE UNIQUE INDEX ix_roles_role ON public.roles USING btree (role);


--
-- TOC entry 3431 (class 1259 OID 25061)
-- Name: ix_tasks_title; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_tasks_title ON public.tasks USING btree (title);


--
-- TOC entry 3434 (class 1259 OID 25062)
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: admin
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- TOC entry 3435 (class 1259 OID 25063)
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: admin
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- TOC entry 3441 (class 1259 OID 25064)
-- Name: ix_work_log_entries_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_work_log_entries_id ON public.work_log_entries USING btree (id);


--
-- TOC entry 3444 (class 1259 OID 25065)
-- Name: ix_work_log_types_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_work_log_types_id ON public.work_log_types USING btree (id);


--
-- TOC entry 3449 (class 1259 OID 25066)
-- Name: ix_work_weeks_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_work_weeks_id ON public.work_weeks USING btree (id);


--
-- TOC entry 3458 (class 2606 OID 25067)
-- Name: article_edit_history article_edit_history_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.article_edit_history
    ADD CONSTRAINT article_edit_history_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.articles(id);


--
-- TOC entry 3459 (class 2606 OID 25072)
-- Name: article_edit_history article_edit_history_editor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.article_edit_history
    ADD CONSTRAINT article_edit_history_editor_id_fkey FOREIGN KEY (editor_id) REFERENCES public.users(id);


--
-- TOC entry 3460 (class 2606 OID 25077)
-- Name: articles articles_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- TOC entry 3461 (class 2606 OID 25082)
-- Name: collaboration_documents collaboration_documents_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.collaboration_documents
    ADD CONSTRAINT collaboration_documents_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- TOC entry 3462 (class 2606 OID 25087)
-- Name: collaboration_sessions collaboration_sessions_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.collaboration_sessions
    ADD CONSTRAINT collaboration_sessions_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.collaboration_documents(id) ON DELETE CASCADE;


--
-- TOC entry 3463 (class 2606 OID 25092)
-- Name: collaboration_sessions collaboration_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.collaboration_sessions
    ADD CONSTRAINT collaboration_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3464 (class 2606 OID 25097)
-- Name: document_collaborators document_collaborators_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.document_collaborators
    ADD CONSTRAINT document_collaborators_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.collaboration_documents(id) ON DELETE CASCADE;


--
-- TOC entry 3465 (class 2606 OID 25102)
-- Name: document_collaborators document_collaborators_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.document_collaborators
    ADD CONSTRAINT document_collaborators_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3466 (class 2606 OID 25107)
-- Name: document_comments document_comments_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.document_comments
    ADD CONSTRAINT document_comments_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.collaboration_documents(id) ON DELETE CASCADE;


--
-- TOC entry 3467 (class 2606 OID 25112)
-- Name: document_comments document_comments_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.document_comments
    ADD CONSTRAINT document_comments_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.document_comments(id) ON DELETE CASCADE;


--
-- TOC entry 3468 (class 2606 OID 25117)
-- Name: document_comments document_comments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.document_comments
    ADD CONSTRAINT document_comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3469 (class 2606 OID 25122)
-- Name: document_edit_history document_edit_history_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.document_edit_history
    ADD CONSTRAINT document_edit_history_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.collaboration_documents(id) ON DELETE CASCADE;


--
-- TOC entry 3470 (class 2606 OID 25127)
-- Name: document_edit_history document_edit_history_editor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.document_edit_history
    ADD CONSTRAINT document_edit_history_editor_id_fkey FOREIGN KEY (editor_id) REFERENCES public.users(id);


--
-- TOC entry 3484 (class 2606 OID 49163)
-- Name: project_categories fk_project_categories_project; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.project_categories
    ADD CONSTRAINT fk_project_categories_project FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- TOC entry 3471 (class 2606 OID 25132)
-- Name: performance_stats performance_stats_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.performance_stats
    ADD CONSTRAINT performance_stats_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3472 (class 2606 OID 25137)
-- Name: project_stats project_stats_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.project_stats
    ADD CONSTRAINT project_stats_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- TOC entry 3473 (class 2606 OID 25142)
-- Name: projects projects_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3474 (class 2606 OID 25147)
-- Name: task_attachments task_attachments_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.task_attachments
    ADD CONSTRAINT task_attachments_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id) ON DELETE CASCADE;


--
-- TOC entry 3475 (class 2606 OID 25152)
-- Name: task_attachments task_attachments_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.task_attachments
    ADD CONSTRAINT task_attachments_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(id);


--
-- TOC entry 3476 (class 2606 OID 25157)
-- Name: tasks tasks_assigned_to_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_assigned_to_fkey FOREIGN KEY (assigned_to) REFERENCES public.users(id);


--
-- TOC entry 3477 (class 2606 OID 25162)
-- Name: tasks tasks_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3478 (class 2606 OID 25167)
-- Name: tasks tasks_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- TOC entry 3479 (class 2606 OID 25172)
-- Name: tasks tasks_reviewed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES public.users(id);


--
-- TOC entry 3480 (class 2606 OID 25177)
-- Name: work_log_entries work_log_entries_reviewed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.work_log_entries
    ADD CONSTRAINT work_log_entries_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES public.users(id);


--
-- TOC entry 3481 (class 2606 OID 25182)
-- Name: work_log_entries work_log_entries_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.work_log_entries
    ADD CONSTRAINT work_log_entries_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3482 (class 2606 OID 25187)
-- Name: work_log_entries work_log_entries_work_week_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.work_log_entries
    ADD CONSTRAINT work_log_entries_work_week_id_fkey FOREIGN KEY (work_week_id) REFERENCES public.work_weeks(id);


--
-- TOC entry 3483 (class 2606 OID 25192)
-- Name: work_weeks work_weeks_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.work_weeks
    ADD CONSTRAINT work_weeks_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


-- Completed on 2025-10-17 16:28:17

--
-- PostgreSQL database dump complete
--

-- Completed on 2025-10-17 16:28:17

--
-- PostgreSQL database cluster dump complete
--

