<template>
  <div class="project-layout">
    <el-container>
      <el-aside width="200px">
        <el-menu :default-active="activeMenu" class="project-menu" router>
          <el-menu-item index="/project/dashboard">
            <el-icon><DataBoard /></el-icon>
            <span>项目仪表板</span>
          </el-menu-item>

          <el-menu-item index="/project/management">
            <el-icon><FolderOpened /></el-icon>
            <span>项目管理</span>
          </el-menu-item>

          <el-menu-item index="/project/task-pool">
            <el-icon><List /></el-icon>
            <span>任务池</span>
          </el-menu-item>

          <el-menu-item index="/project/my-workspace">
            <el-icon><User /></el-icon>
            <span>我的工作台</span>
          </el-menu-item>

          <el-menu-item index="/project/task-review">
            <el-icon><Check /></el-icon>
            <span>任务审核</span>
          </el-menu-item>

          <el-menu-item index="/project/user-management">
            <el-icon><UserFilled /></el-icon>
            <span>用户管理</span>
          </el-menu-item>

          <el-sub-menu index="performance">
            <template #title>
              <el-icon><TrendCharts /></el-icon>
              <span>绩效管理</span>
            </template>
            <el-menu-item index="/project/performance/team"> 团队绩效 </el-menu-item>
            <el-menu-item index="/project/performance/personal"> 个人绩效 </el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>

      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
  import { computed } from 'vue'
  import { useRoute } from 'vue-router'
  import {
    DataBoard,
    FolderOpened,
    List,
    User,
    Check,
    UserFilled,
    TrendCharts
  } from '@element-plus/icons-vue'

  const route = useRoute()

  const activeMenu = computed(() => route.path)
</script>

<style scoped lang="scss">
  .project-layout {
    height: 100vh;

    .el-container {
      height: 100%;
    }

    .el-aside {
      background-color: #f5f5f5;
      border-right: 1px solid #e6e6e6;
    }

    .project-menu {
      border-right: none;
      height: 100%;
    }

    .el-main {
      padding: 0;
      background-color: #fff;
    }
  }
</style>
