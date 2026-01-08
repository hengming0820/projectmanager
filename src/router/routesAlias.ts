/**
 * 路由别名，方便快速找到页面，同时可以用作路由跳转
 */
export enum RoutesAlias {
  // 布局和认证
  Layout = '/index/index', // 布局容器
  Login = '/auth/login', // 登录
  Register = '/auth/register', // 注册
  ForgetPassword = '/auth/forget-password', // 忘记密码

  // 异常页面
  Exception403 = '/exception/403', // 403
  Exception404 = '/exception/404', // 404
  Exception500 = '/exception/500', // 500

  // 结果页面
  Success = '/result/success', // 成功
  Fail = '/result/fail', // 失败

  // 系统管理
  User = '/system/user', // 账户
  Role = '/system/role', // 角色
  UserCenter = '/system/user-center', // 用户中心
  Menu = '/system/menu', // 菜单

  // 项目管理
  ProjectManagement = '/project/management', // 项目管理
  TaskPool = '/project/task-pool', // 任务池
  MyWorkspace = '/project/my-workspace', // 我的工作台
  TaskReview = '/project/task-review', // 任务审核
  TeamPerformance = '/project/performance/team', // 全员绩效
  PersonalPerformance = '/project/performance/personal', // 个人绩效
  ProjectDashboard = '/project/dashboard', // 项目仪表板

  // 工作日志
  WorkLogManagement = '/work-log/index', // 工作日志管理
  WorkLogWeekDetail = '/work-log/week-detail', // 工作周详情

  // 团队协作
  CollaborationManagement = '/collaboration/index', // 团队协作管理
  CollaborationCreate = '/collaboration/create/index', // 创建协作文档（已弃用，改为对话框）
  CollaborationDocument = '/collaboration/edit/index' // 协作文档编辑
}
