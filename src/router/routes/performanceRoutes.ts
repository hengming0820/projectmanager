import { RoutesAlias } from '../routesAlias'
import { AppRouteRecord } from '@/types/router'

/**
 * 绩效系统路由配置
 */
export const performanceRoutes: AppRouteRecord[] = [
  {
    path: '/performance',
    name: 'Performance',
    component: RoutesAlias.Layout,
    meta: {
      title: '绩效系统',
      icon: '&#xe860;',
      roles: ['R_SUPER', 'R_ADMIN', 'R_ANNOTATOR', 'R_REVIEWER']
    },
    children: [
      // 全员绩效
      {
        path: 'team',
        name: 'TeamPerformance',
        component: () => import('@views/project/performance/team.vue'),
        meta: {
          title: '全员绩效',
          icon: '&#xe860;',
          keepAlive: true,
          roles: ['R_SUPER', 'R_ADMIN', 'R_REVIEWER']
        }
      },
      // 我的绩效
      {
        path: 'personal',
        name: 'PersonalPerformance',
        component: () => import('@views/project/performance/personal.vue'),
        meta: {
          title: '我的绩效',
          icon: '&#xe721;',
          keepAlive: true,
          roles: ['R_SUPER', 'R_ADMIN', 'R_ANNOTATOR', 'R_REVIEWER']
        }
      }
    ]
  }
]
