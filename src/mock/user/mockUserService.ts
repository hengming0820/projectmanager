import type { User } from '@/types/project'

// 模拟用户数据
const mockUsers: User[] = [
  {
    id: 'user0',
    username: 'Super',
    realName: '超级管理员',
    email: 'super@example.com',
    role: 'admin',
    roles: ['R_SUPER'],
    avatar: '',
    department: '技术部',
    status: 'active',
    createdAt: '2024-01-01T00:00:00Z'
  },
  {
    id: 'user1',
    username: 'Admin',
    realName: '系统管理员',
    email: 'admin@example.com',
    role: 'admin',
    roles: ['R_ADMIN'],
    avatar: '',
    department: '技术部',
    status: 'active',
    createdAt: '2024-01-01T00:00:00Z'
  },
  {
    id: 'user2',
    username: 'User',
    realName: '普通用户',
    email: 'user@example.com',
    role: 'annotator',
    roles: ['R_USER'],
    avatar: '',
    department: '业务部',
    status: 'active',
    createdAt: '2024-01-15T00:00:00Z'
  }
]

export class MockUserService {
  // 登录验证
  static async login(params: { userName: string; password: string }) {
    // 模拟API延迟
    await new Promise((resolve) => setTimeout(resolve, 500))

    const { userName, password } = params

    // 预设的测试账户
    const validAccounts = [
      { userName: 'Super', password: '123456', role: 'R_SUPER' },
      { userName: 'Admin', password: '123456', role: 'R_ADMIN' },
      { userName: 'User', password: '123456', role: 'R_USER' }
    ]

    const account = validAccounts.find(
      (acc) => acc.userName === userName && acc.password === password
    )

    if (account) {
      // 登录成功，返回模拟的token
      return {
        token: `mock_token_${account.role}_${Date.now()}`,
        refreshToken: `mock_refresh_token_${account.role}_${Date.now()}`
      }
    } else {
      // 登录失败
      throw new Error('用户名或密码错误')
    }
  }

  // 根据token获取用户信息
  static async getUserInfo(token: string) {
    // 模拟API延迟
    await new Promise((resolve) => setTimeout(resolve, 300))

    // 从token中解析用户角色
    const roleMatch = token.match(/mock_token_(.+)_/)
    if (!roleMatch) {
      throw new Error('无效的token')
    }

    const role = roleMatch[1]
    const user = mockUsers.find((u) => u.roles.includes(role))

    if (!user) {
      throw new Error('用户不存在')
    }

    return user
  }

  // 获取用户列表
  static async getUserList(params: any) {
    // 模拟API延迟
    await new Promise((resolve) => setTimeout(resolve, 200))

    let filteredUsers = [...mockUsers]

    // 模拟筛选
    if (params.role) {
      filteredUsers = filteredUsers.filter((user) => user.role === params.role)
    }
    if (params.status) {
      filteredUsers = filteredUsers.filter((user) => user.status === params.status)
    }

    // 模拟分页
    const { current = 1, size = 10 } = params
    const start = (current - 1) * size
    const end = start + size
    const paginatedUsers = filteredUsers.slice(start, end)

    return {
      list: paginatedUsers,
      total: filteredUsers.length
    }
  }
}
