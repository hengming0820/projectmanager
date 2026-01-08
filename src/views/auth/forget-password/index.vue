<template>
  <div class="login register">
    <LoginLeftView></LoginLeftView>
    <div class="right-wrap">
      <div class="header">
        <ArtLogo class="icon" />
        <h1>{{ systemName }}</h1>
      </div>
      <div class="login-wrap">
        <div class="form">
          <h3 class="title">{{ $t('forgetPassword.title') }}</h3>
          <p class="sub-title">{{ $t('forgetPassword.subTitle') }}</p>
          <div class="input-wrap">
            <span class="input-label" v-if="showInputLabel">账号</span>
            <ElInput :placeholder="$t('forgetPassword.placeholder')" v-model.trim="username" />
          </div>
          <div class="input-wrap" style="margin-top: 12px">
            <span class="input-label" v-if="showInputLabel">当前密码</span>
            <ElInput
              placeholder="请输入当前密码"
              v-model.trim="currentPassword"
              type="password"
              show-password
            />
          </div>
          <div class="input-wrap" style="margin-top: 12px">
            <span class="input-label" v-if="showInputLabel">新密码</span>
            <ElInput
              placeholder="请输入新密码"
              v-model.trim="newPassword"
              type="password"
              show-password
            />
          </div>
          <div class="input-wrap" style="margin-top: 12px">
            <span class="input-label" v-if="showInputLabel">确认新密码</span>
            <ElInput
              placeholder="请再次输入新密码"
              v-model.trim="confirmPassword"
              type="password"
              show-password
            />
          </div>

          <div style="margin-top: 15px">
            <ElButton
              class="login-btn"
              type="primary"
              @click="handleChangePassword"
              :loading="loading"
              v-ripple
            >
              {{ $t('forgetPassword.submitBtnText') }}
            </ElButton>
          </div>

          <div style="margin-top: 15px">
            <ElButton class="back-btn" plain @click="toLogin">
              {{ $t('forgetPassword.backBtnText') }}
            </ElButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import AppConfig from '@/config'
  import { RoutesAlias } from '@/router/routesAlias'

  defineOptions({ name: 'ForgetPassword' })

  const router = useRouter()
  const showInputLabel = ref(false)

  const systemName = AppConfig.systemInfo.name
  const username = ref('')
  const currentPassword = ref('')
  const newPassword = ref('')
  const confirmPassword = ref('')
  const loading = ref(false)

  const handleChangePassword = async () => {
    if (!username.value || !currentPassword.value || !newPassword.value || !confirmPassword.value)
      return
    if (newPassword.value !== confirmPassword.value) return
    try {
      loading.value = true
      const { userApi } = await import('@/api/userApi')
      // 如果未登录，这里需要先登录以获取 token；否则后端需要支持使用账号+当前密码直接改。
      // 简化实现：如果已登录则直接改；未登录则尝试调用登录再改。
      try {
        await userApi.changeMyPassword({
          current_password: currentPassword.value,
          new_password: newPassword.value
        })
      } catch (e) {
        // 未登录时不支持，跳转至登录
        router.push(RoutesAlias.Login)
        return
      }
      router.push(RoutesAlias.Login)
    } finally {
      loading.value = false
    }
  }

  const toLogin = () => {
    router.push(RoutesAlias.Login)
  }
</script>

<style lang="scss" scoped>
  @use '../login/index';
</style>
