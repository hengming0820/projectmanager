<template>
  <div class="performance-layout">
    <el-container>
      <el-aside width="200px">
        <el-menu :default-active="activeMenu" class="performance-menu" router>
          <el-menu-item index="/project/performance/team">
            <el-icon><UserFilled /></el-icon>
            <span>团队绩效</span>
          </el-menu-item>

          <el-menu-item index="/project/performance/personal">
            <el-icon><User /></el-icon>
            <span>个人绩效</span>
          </el-menu-item>
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
  import { UserFilled, User } from '@element-plus/icons-vue'

  const route = useRoute()

  const activeMenu = computed(() => route.path)
</script>

<style scoped lang="scss">
  .performance-layout {
    height: 100vh;

    .el-container {
      height: 100%;
    }

    .el-aside {
      background-color: #f5f5f5;
      border-right: 1px solid #e6e6e6;
    }

    .performance-menu {
      border-right: none;
      height: 100%;
    }

    .el-main {
      padding: 0;
      background-color: #fff;
    }
  }
</style>
