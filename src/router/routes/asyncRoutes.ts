import { RoutesAlias } from '../routesAlias'
import { AppRouteRecord } from '@/types/router'
import { WEB_LINKS } from '@/utils/constants'
import { projectRoutes } from './projectRoutes'
import { performanceRoutes } from './performanceRoutes'

/**
 * 菜单列表、异步路由
 *
 * 支持两种模式:
 * 前端静态配置 - 直接使用本文件中定义的路由配置
 * 后端动态配置 - 后端返回菜单数据，前端解析生成路由
 *
 * 菜单标题（title）:
 * 可以是 i18n 的 key，也可以是字符串，比如：'用户列表'
 *
 * RoutesAlias.Layout 指向的是布局组件，后端返回的菜单数据中，component 字段需要指向 /index/index
 * 路由元数据（meta）：异步路由在 asyncRoutes 中配置，静态路由在 staticRoutes 中配置
 */
export const asyncRoutes: AppRouteRecord[] = [
  // 工作日志（一级导航，跳转到现有 Project 下的路由，避免大规模改动）
  {
    path: '/work-log',
    name: 'WorkLog',
    component: RoutesAlias.Layout,
    meta: {
      title: '工作日志',
      icon: '&#xe6b7;'
      // 移除 roles 限制，允许所有登录用户访问
    },
    children: [
      {
        path: 'list',
        name: 'WorkLogEntry',
        redirect: '/project/work-log',
        component: RoutesAlias.Layout,
        meta: {
          title: '工作计划',
          keepAlive: false
        }
      },
      {
        path: 'week-detail/:weekId',
        name: 'WorkLogWeekDetailStandalone',
        component: RoutesAlias.WorkLogWeekDetail,
        meta: { title: '工作周详情', keepAlive: false, isHide: true, activePath: '/work-log/list' }
      }
    ]
  },
  // 团队协作（一级）
  {
    path: '/collaboration',
    name: 'Collaboration',
    component: RoutesAlias.Layout,
    meta: {
      title: '团队协作',
      icon: '&#xe7ae;'
      // 移除 roles 限制，允许所有登录用户访问
    },
    children: [
      {
        path: 'documents',
        name: 'CollaborationEntry',
        redirect: '/project/collaboration',
        component: RoutesAlias.Layout,
        meta: { title: '文档', keepAlive: false }
      },
      {
        path: 'document/:documentId',
        name: 'CollaborationDocumentStandalone',
        component: RoutesAlias.CollaborationDocument,
        meta: {
          title: '协作文档',
          keepAlive: false,
          isHide: true,
          activePath: '/collaboration/documents'
        }
      }
    ]
  },
  // 知识与文章（一级）
  {
    path: '/articles',
    name: 'Articles',
    component: RoutesAlias.Layout,
    meta: {
      title: '知识与文章',
      icon: '&#xe63a;'
      // 移除 roles 限制，允许所有登录用户访问
    },
    children: [
      {
        path: 'meetings',
        name: 'ArticlesMeetingEntry',
        redirect: '/project/meeting-notes',
        component: RoutesAlias.Layout,
        meta: { title: '会议记录', keepAlive: false }
      },
      {
        path: 'model-tests',
        name: 'ArticlesModelTestEntry',
        redirect: '/project/model-tests',
        component: RoutesAlias.Layout,
        meta: { title: '模型测试', keepAlive: false }
      }
    ]
  },
  {
    path: '/system',
    name: 'System',
    component: RoutesAlias.Layout,
    meta: {
      title: 'menus.system.title',
      icon: '&#xe7b9;',
      // 允许普通用户访问隐藏的个人中心
      roles: ['R_SUPER', 'R_ADMIN', 'R_USER']
    },
    children: [
      {
        path: 'user',
        name: 'User',
        component: RoutesAlias.User,
        meta: {
          title: 'menus.system.user',
          keepAlive: true,
          roles: ['R_SUPER', 'R_ADMIN']
        }
      },
      {
        path: 'role',
        name: 'Role',
        component: RoutesAlias.Role,
        meta: {
          title: 'menus.system.role',
          keepAlive: true,
          roles: ['R_SUPER', 'R_ADMIN']
        }
      },
      {
        path: 'user-center',
        name: 'UserCenter',
        component: RoutesAlias.UserCenter,
        meta: {
          title: 'menus.system.userCenter',
          isHide: true,
          keepAlive: true,
          isHideTab: true,
          roles: ['R_SUPER', 'R_ADMIN', 'R_USER']
        }
      },
      {
        path: 'menu',
        name: 'Menus',
        component: RoutesAlias.Menu,
        meta: {
          title: 'menus.system.menu',
          keepAlive: true,
          roles: ['R_SUPER'],
          authList: [
            {
              title: '新增',
              authMark: 'add'
            },
            {
              title: '编辑',
              authMark: 'edit'
            },
            {
              title: '删除',
              authMark: 'delete'
            }
          ]
        }
      }
    ]
  },
  {
    path: '/result',
    name: 'Result',
    component: RoutesAlias.Layout,
    meta: {
      title: 'menus.result.title',
      icon: '&#xe715;'
    },
    children: [
      {
        path: 'success',
        name: 'ResultSuccess',
        component: RoutesAlias.Success,
        meta: {
          title: 'menus.result.success',
          keepAlive: true
        }
      },
      {
        path: 'fail',
        name: 'ResultFail',
        component: RoutesAlias.Fail,
        meta: {
          title: 'menus.result.fail',
          keepAlive: true
        }
      }
    ]
  },
  {
    path: '/exception',
    name: 'Exception',
    component: RoutesAlias.Layout,
    meta: {
      title: 'menus.exception.title',
      icon: '&#xe820;'
    },
    children: [
      {
        path: '403',
        name: '403',
        component: RoutesAlias.Exception403,
        meta: {
          title: 'menus.exception.forbidden',
          keepAlive: true
        }
      },
      {
        path: '404',
        name: '404',
        component: RoutesAlias.Exception404,
        meta: {
          title: 'menus.exception.notFound',
          keepAlive: true
        }
      },
      {
        path: '500',
        name: '500',
        component: RoutesAlias.Exception500,
        meta: {
          title: 'menus.exception.serverError',
          keepAlive: true
        }
      }
    ]
  },
  ...projectRoutes,
  ...performanceRoutes
]
