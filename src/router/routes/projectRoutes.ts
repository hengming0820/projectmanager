import { RoutesAlias } from '../routesAlias'
import { AppRouteRecord } from '@/types/router'

export const projectRoutes: AppRouteRecord[] = [
  {
    path: '/project',
    name: 'Project',
    component: RoutesAlias.Layout,
    meta: {
      title: '项目管理',
      icon: '&#xe7b9;',
      roles: ['R_SUPER', 'R_ADMIN', 'R_ANNOTATOR', 'R_REVIEWER']
    },
    children: [
      {
        path: 'dashboard',
        name: 'ProjectDashboard',
        component: '/project/dashboard/index',
        meta: {
          title: '项目仪表板',
          keepAlive: true,
          roles: ['R_SUPER', 'R_ADMIN', 'R_ANNOTATOR', 'R_REVIEWER']
        }
      },
      {
        path: 'management',
        name: 'ProjectManagement',
        component: '/project/management/index-new',
        meta: {
          title: '项目管理',
          keepAlive: true,
          roles: ['R_SUPER', 'R_ADMIN']
        }
      },
      {
        path: 'management-old',
        name: 'ProjectManagementOld',
        component: '/project/management/index',
        meta: {
          title: '项目管理(旧版)',
          keepAlive: true,
          roles: ['R_SUPER', 'R_ADMIN'],
          isHide: true
        }
      },
      {
        path: 'task-pool',
        name: 'TaskPool',
        component: '/project/task-pool/index',
        meta: {
          title: '任务池',
          keepAlive: true,
          roles: ['R_SUPER', 'R_ADMIN', 'R_ANNOTATOR']
        }
      },
      {
        path: 'my-workspace',
        name: 'MyWorkspace',
        component: '/project/my-workspace/index',
        meta: {
          title: '我的工作台',
          keepAlive: true,
          roles: ['R_SUPER', 'R_ADMIN', 'R_ANNOTATOR']
        }
      },
      {
        path: 'task-review',
        name: 'TaskReview',
        component: '/project/task-review/index',
        meta: {
          title: '任务审核',
          keepAlive: true,
          roles: ['R_SUPER', 'R_ADMIN', 'R_REVIEWER']
        }
      },
      {
        path: 'user-management',
        name: 'UserManagement',
        component: '/project/user-management/index',
        meta: {
          title: '用户管理',
          keepAlive: true,
          roles: ['R_SUPER', 'R_ADMIN'],
          isHide: true
        }
      },
      {
        path: 'work-log',
        name: 'WorkLogManagement',
        component: RoutesAlias.WorkLogManagement,
        meta: {
          title: '工作日志',
          keepAlive: true,
          roles: ['R_SUPER', 'R_ADMIN', 'R_ANNOTATOR', 'R_REVIEWER'],
          isHide: true
        }
      },
      {
        path: 'work-log/:weekId',
        name: 'WorkLogWeekDetail',
        component: RoutesAlias.WorkLogWeekDetail,
        meta: {
          title: '工作周详情',
          keepAlive: false,
          roles: ['R_SUPER', 'R_ADMIN', 'R_ANNOTATOR', 'R_REVIEWER'],
          activePath: '/project/work-log',
          isHide: true // 隐藏在导航菜单中
        }
      },
      {
        path: 'collaboration',
        name: 'Collaboration',
        component: RoutesAlias.CollaborationManagement,
        meta: {
          title: '团队协作',
          keepAlive: true,
          roles: ['R_SUPER', 'R_ADMIN', 'R_ANNOTATOR', 'R_REVIEWER'],
          isHide: true
        }
      },
      // 创建协作文档路由已弃用，改为使用对话框创建
      // {
      //   path: 'collaboration/create',
      //   name: 'CollaborationCreate',
      //   component: RoutesAlias.CollaborationCreate,
      //   meta: {
      //     title: '创建协作文档',
      //     keepAlive: false,
      //     roles: ['R_SUPER', 'R_ADMIN', 'R_REVIEWER'],
      //     activePath: '/project/collaboration',
      //     isHide: true
      //   }
      // },
      {
        path: 'collaboration/:documentId',
        name: 'CollaborationDocument',
        component: () => import('@/views/collaboration/edit/index.vue'),
        meta: {
          title: '编辑协作文档',
          keepAlive: false,
          roles: ['R_SUPER', 'R_ADMIN', 'R_ANNOTATOR', 'R_REVIEWER'],
          activePath: '/project/collaboration',
          isHide: true // 隐藏在导航菜单中
        }
      },
      {
        path: 'meeting-notes',
        name: 'MeetingNotes',
        component: '/project/articles/meeting/index',
        meta: {
          title: '会议记录',
          keepAlive: true,
          // 移除 roles 限制，允许所有登录用户访问
          isHide: true
        }
      },
      {
        path: 'model-tests',
        name: 'ModelTests',
        component: '/project/articles/model-test/index',
        meta: {
          title: '模型测试',
          keepAlive: true,
          // 移除 roles 限制，允许所有登录用户访问
          isHide: true
        }
      },
      {
        path: 'article/create/:type',
        name: 'ArticleCreate',
        component: '/project/articles/create/index',
        meta: {
          title: '发布文章',
          keepAlive: false,
          // 移除 roles 限制，允许所有登录用户发布文章
          isHide: true
        }
      }
    ]
  }
]
