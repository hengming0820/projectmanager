<template>
  <div class="page-content user">
    <div class="content">
      <div class="left-wrap">
        <div class="user-wrap box-style">
          <img class="bg" src="@imgs/user/bg.webp" />
          <img class="avatar" :src="userCenterAvatar" />
          <div style="margin-top: 10px">
            <ElUpload
              :auto-upload="false"
              :show-file-list="false"
              :on-change="onAvatarSelect"
              accept="image/*"
            >
              <ElButton size="small">更换头像</ElButton>
            </ElUpload>
          </div>
          <h2 class="name">{{ userInfo.realName || userInfo.userName }}</h2>
          <p class="des">{{ userInfo.department || '—' }}</p>

          <div class="outer-info">
            <div>
              <i class="iconfont-sys">&#xe72e;</i>
              <span>{{ userInfo.email || '-' }}</span>
            </div>
            <div>
              <i class="iconfont-sys">&#xe608;</i>
              <span>{{ userInfo.role || '-' }}</span>
            </div>
            <div>
              <i class="iconfont-sys">&#xe736;</i>
              <span>四川省成都市</span>
            </div>
            <div>
              <i class="iconfont-sys">&#xe811;</i>
              <span
                >星像精准－{{ userInfo.department || '未知部门' }}－{{
                  userInfo.realName || userInfo.userName || '未知姓名'
                }}</span
              >
            </div>
            <div>
              <i class="iconfont-sys">&#xe747;</i>
              <span>入职时间：{{ formatHireDate(userInfo.hireDate) }}</span>
            </div>
          </div>

          <div class="lables">
            <h3>
              标签
              <el-button
                size="small"
                style="margin-left: 10px; font-size: 12px"
                @click="toggleEditLabels"
                :type="isEditLabels ? 'primary' : 'default'"
              >
                {{ isEditLabels ? '保存' : '编辑' }}
              </el-button>
            </h3>
            <div>
              <div
                v-for="(item, index) in lableList"
                :key="index"
                class="label-item"
                :class="{ editing: isEditLabels }"
              >
                <span v-if="!isEditLabels">{{ item }}</span>
                <el-input
                  v-else
                  v-model="lableList[index]"
                  size="small"
                  style="width: 80px; margin-right: 5px"
                />
                <el-button
                  v-if="isEditLabels"
                  size="small"
                  type="danger"
                  icon="Delete"
                  circle
                  style="margin-left: 5px; width: 20px; height: 20px"
                  @click="removeLabel(index)"
                />
              </div>
              <div v-if="isEditLabels" class="add-label">
                <el-button
                  size="small"
                  type="primary"
                  icon="Plus"
                  circle
                  style="width: 25px; height: 25px"
                  @click="addLabel"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- <el-carousel class="gallery" height="160px"
          :interval="5000"
          indicator-position="none"
        >
          <el-carousel-item class="item" v-for="item in galleryList" :key="item">
            <img :src="item"/>
          </el-carousel-item>
        </el-carousel> -->
      </div>
      <div class="right-wrap">
        <div class="info box-style">
          <h1 class="title">基本设置</h1>

          <ElForm
            :model="form"
            class="form"
            ref="ruleFormRef"
            :rules="rules"
            label-width="86px"
            label-position="top"
          >
            <ElRow>
              <ElFormItem label="姓名" prop="realName">
                <el-input v-model="form.realName" :disabled="!isEdit" />
              </ElFormItem>
              <ElFormItem label="性别" prop="sex" class="right-input">
                <ElSelect v-model="form.sex" placeholder="Select" :disabled="!isEdit">
                  <ElOption
                    v-for="item in options"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </ElSelect>
              </ElFormItem>
            </ElRow>

            <ElRow>
              <ElFormItem label="昵称" prop="nikeName">
                <ElInput v-model="form.nikeName" :disabled="!isEdit" />
              </ElFormItem>
              <ElFormItem label="邮箱" prop="email" class="right-input">
                <ElInput v-model="form.email" :disabled="!isEdit" />
              </ElFormItem>
            </ElRow>

            <ElRow>
              <ElFormItem label="手机" prop="mobile">
                <ElInput v-model="form.mobile" :disabled="!isEdit" />
              </ElFormItem>
              <ElFormItem label="地址" prop="address" class="right-input">
                <ElInput v-model="form.address" :disabled="!isEdit" />
              </ElFormItem>
            </ElRow>

            <ElFormItem label="个人介绍" prop="des" :style="{ height: '130px' }">
              <ElInput type="textarea" :rows="4" v-model="form.des" :disabled="!isEdit" />
            </ElFormItem>

            <div class="el-form-item-right">
              <ElButton type="primary" style="width: 90px" v-ripple @click="edit">
                {{ isEdit ? '保存' : '编辑' }}
              </ElButton>
            </div>
          </ElForm>
        </div>

        <div class="info box-style" style="margin-top: 20px">
          <h1 class="title">更改密码</h1>

          <ElForm :model="pwdForm" class="form" label-width="86px" label-position="top">
            <ElFormItem label="当前密码" prop="password">
              <ElInput
                v-model="pwdForm.password"
                type="password"
                :disabled="!isEditPwd"
                show-password
              />
            </ElFormItem>

            <ElFormItem label="新密码" prop="newPassword">
              <ElInput
                v-model="pwdForm.newPassword"
                type="password"
                :disabled="!isEditPwd"
                show-password
              />
            </ElFormItem>

            <ElFormItem label="确认新密码" prop="confirmPassword">
              <ElInput
                v-model="pwdForm.confirmPassword"
                type="password"
                :disabled="!isEditPwd"
                show-password
              />
            </ElFormItem>

            <div class="el-form-item-right">
              <ElButton type="primary" style="width: 90px" v-ripple @click="editPwd">
                {{ isEditPwd ? '保存' : '编辑' }}
              </ElButton>
            </div>
          </ElForm>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, computed, onMounted } from 'vue'
  import { useUserStore } from '@/store/modules/user'
  import { ElForm, FormInstance, FormRules } from 'element-plus'
  import defaultAvatar from '@/assets/img/user/avatar.webp'

  defineOptions({ name: 'UserCenter' })

  const userStore = useUserStore()
  const userInfo = computed(() => userStore.getUserInfo)
  const rewriteToProxy = (u?: string) =>
    u ? u.replace(/^https?:\/\/[^/]+\/medical-annotations\//, '/api/files/') : ''
  const userCenterAvatar = computed(
    () => rewriteToProxy((userInfo.value as any).avatar) || defaultAvatar
  )

  const isEdit = ref(false)
  const isEditPwd = ref(false)
  const isEditLabels = ref(false)
  const date = ref('')
  const form = reactive({
    realName: userInfo.value.realName || userInfo.value.userName || '',
    nikeName: userInfo.value.userName || '',
    email: userInfo.value.email || '',
    mobile: '',
    address: '',
    sex: '2',
    des: ''
  })

  const pwdForm = reactive({
    password: '',
    newPassword: '',
    confirmPassword: ''
  })

  const ruleFormRef = ref<FormInstance>()

  const rules = reactive<FormRules>({
    realName: [
      { required: true, message: '请输入昵称', trigger: 'blur' },
      { min: 2, max: 50, message: '长度在 2 到 30 个字符', trigger: 'blur' }
    ],
    nikeName: [
      { required: true, message: '请输入昵称', trigger: 'blur' },
      { min: 2, max: 50, message: '长度在 2 到 30 个字符', trigger: 'blur' }
    ],
    email: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
    mobile: [{ required: true, message: '请输入手机号码', trigger: 'blur' }],
    address: [{ required: true, message: '请输入地址', trigger: 'blur' }],
    sex: [{ type: 'array', required: true, message: '请选择性别', trigger: 'blur' }]
  })

  const options = [
    {
      value: '1',
      label: '男'
    },
    {
      value: '2',
      label: '女'
    }
  ]

  const lableList = ref<Array<string>>([])

  onMounted(async () => {
    getDate()
    loadUserTags()

    // 确保加载最新的用户信息（包括入职时间）
    try {
      await userStore.fetchMyProfile()
      console.log('📋 [UserCenter] 用户信息:', userInfo.value)
      console.log('📅 [UserCenter] 入职时间:', userInfo.value.hireDate)
    } catch (error) {
      console.error('❌ [UserCenter] 加载用户信息失败:', error)
    }
  })

  // 加载用户标签
  const loadUserTags = async () => {
    try {
      const { backendApi } = await import('@/utils/http/backendApi')
      const userProfile = await backendApi.get('/users/me/profile')
      if (userProfile.tags && Array.isArray(userProfile.tags)) {
        lableList.value = userProfile.tags
      } else {
        // 如果没有标签，设置默认标签
        lableList.value = ['专注设计', '很有想法', '辣~', '大长腿', '川妹子', '海纳百川']
      }
    } catch (error) {
      console.error('加载用户标签失败:', error)
      // 使用默认标签
      lableList.value = ['专注设计', '很有想法', '辣~', '大长腿', '川妹子', '海纳百川']
    }
  }

  // 格式化入职时间
  const formatHireDate = (hireDate?: string) => {
    if (!hireDate) return '未设置'
    try {
      // 支持多种日期格式
      const date = new Date(hireDate)
      if (isNaN(date.getTime())) return '日期格式错误'

      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')

      return `${year}年${month}月${day}日`
    } catch (error) {
      console.error('格式化入职时间失败:', error)
      return '未知'
    }
  }

  const getDate = () => {
    const d = new Date()
    const h = d.getHours()
    let text = ''

    if (h >= 6 && h < 9) {
      text = '早上好'
    } else if (h >= 9 && h < 11) {
      text = '上午好'
    } else if (h >= 11 && h < 13) {
      text = '中午好'
    } else if (h >= 13 && h < 18) {
      text = '下午好'
    } else if (h >= 18 && h < 24) {
      text = '晚上好'
    } else if (h >= 0 && h < 6) {
      text = '很晚了，早点睡'
    }

    date.value = text
  }

  const edit = async () => {
    if (!isEdit.value) {
      isEdit.value = true
      return
    }
    // 保存
    try {
      await userStore.updateUserProfile({
        real_name: form.realName,
        email: form.email,
        avatar_url: userInfo.value.avatar,
        department: userInfo.value.department
      })

      // 刷新用户信息
      await userStore.fetchMyProfile()
      console.log('✅ [UserCenter] 用户信息已更新并刷新')

      isEdit.value = false
    } catch (e) {
      console.error('❌ [UserCenter] 更新用户信息失败:', e)
      isEdit.value = true
    }
  }

  const editPwd = async () => {
    if (!isEditPwd.value) {
      isEditPwd.value = true
      return
    }
    if (!pwdForm.password || !pwdForm.newPassword || !pwdForm.confirmPassword) return
    if (pwdForm.newPassword !== pwdForm.confirmPassword) return
    try {
      const { userApi } = await import('@/api/userApi')
      await userApi.changeMyPassword({
        current_password: pwdForm.password,
        new_password: pwdForm.newPassword
      })
      // 提示
      const { ElMessage } = await import('element-plus')
      ElMessage.success('密码修改成功')
      isEditPwd.value = false
      pwdForm.password = ''
      pwdForm.newPassword = ''
      pwdForm.confirmPassword = ''
    } catch (e) {
      const { ElMessage } = await import('element-plus')
      ElMessage.error('密码修改失败')
      isEditPwd.value = true
    }
  }

  const onAvatarSelect = async (file: any) => {
    try {
      const form = new FormData()
      form.append('file', file.raw)
      const { backendApi } = await import('@/utils/http/backendApi')
      const res: any = await backendApi.post('/users/me/avatar', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      console.log('✅ [UserCenter] 头像上传成功，返回结果:', res)

      // 刷新用户信息
      await userStore.fetchMyProfile()
      console.log('✅ [UserCenter] 用户信息已刷新，新头像:', userInfo.value.avatar)

      const { ElMessage } = await import('element-plus')
      ElMessage.success('头像更新成功')
    } catch (e) {
      console.error('❌ [UserCenter] 头像更新失败:', e)
      const { ElMessage } = await import('element-plus')
      ElMessage.error('头像更新失败')
    }
  }

  // 标签编辑相关方法
  const toggleEditLabels = async () => {
    if (isEditLabels.value) {
      // 保存标签到后端
      try {
        const { backendApi } = await import('@/utils/http/backendApi')
        await backendApi.put('/users/me/profile', {
          tags: lableList.value
        })
        const { ElMessage } = await import('element-plus')
        ElMessage.success('标签保存成功')
      } catch (error) {
        console.error('保存标签失败:', error)
        const { ElMessage } = await import('element-plus')
        ElMessage.error('标签保存失败')
        return // 保存失败时不退出编辑模式
      }
    }
    isEditLabels.value = !isEditLabels.value
  }

  const addLabel = () => {
    lableList.value.push('新标签')
  }

  const removeLabel = (index: number) => {
    lableList.value.splice(index, 1)
  }
</script>

<style lang="scss">
  .user {
    .icon {
      width: 1.4em;
      height: 1.4em;
      overflow: hidden;
      vertical-align: -0.15em;
      fill: currentcolor;
    }
  }
</style>

<style lang="scss" scoped>
  .page-content {
    width: 100%;
    height: 100%;
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;

    $box-radius: calc(var(--custom-radius) + 4px);

    .box-style {
      border: 1px solid var(--art-border-color);
    }

    .content {
      position: relative;
      display: flex;
      justify-content: space-between;
      margin-top: 10px;

      .left-wrap {
        width: 450px;
        margin-right: 25px;

        .user-wrap {
          position: relative;
          height: 600px;
          padding: 35px 40px;
          overflow: hidden;
          text-align: center;
          background: var(--art-main-bg-color);
          border-radius: $box-radius;

          .bg {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 200px;
            object-fit: cover;
          }

          .avatar {
            position: relative;
            z-index: 10;
            width: 80px;
            height: 80px;
            margin-top: 120px;
            object-fit: cover;
            border: 2px solid #fff;
            border-radius: 50%;
          }

          .name {
            margin-top: 20px;
            font-size: 22px;
            font-weight: 400;
          }

          .des {
            margin-top: 20px;
            font-size: 14px;
          }

          .outer-info {
            width: 300px;
            margin: auto;
            margin-top: 30px;
            text-align: left;

            > div {
              margin-top: 10px;

              span {
                margin-left: 8px;
                font-size: 14px;
              }
            }
          }

          .lables {
            margin-top: 40px;

            h3 {
              display: flex;
              align-items: center;
              font-size: 15px;
              font-weight: 500;
            }

            > div {
              display: flex;
              flex-wrap: wrap;
              justify-content: flex-start;
              margin-top: 15px;
              max-height: 200px;
              overflow-y: auto;

              .label-item {
                display: flex;
                align-items: center;
                padding: 3px 6px;
                margin: 0 8px 8px 0;
                font-size: 12px;
                background: var(--art-main-bg-color);
                border: 1px solid var(--art-border-color);
                border-radius: 2px;
                transition: all 0.3s ease;
                min-width: 0;
                flex-shrink: 0;

                &.editing {
                  padding: 2px 4px;
                  background: var(--el-color-primary-light-9);
                  border-color: var(--el-color-primary);
                  min-width: 120px;
                }

                span {
                  white-space: nowrap;
                  overflow: hidden;
                  text-overflow: ellipsis;
                  max-width: 80px;
                }

                .el-input {
                  min-width: 80px;
                  max-width: 120px;
                }

                .el-button {
                  margin-left: 4px;
                  flex-shrink: 0;
                }
              }

              .add-label {
                display: flex;
                align-items: center;
                margin: 0 8px 8px 0;
                flex-shrink: 0;
              }
            }
          }
        }

        .gallery {
          margin-top: 25px;
          border-radius: 10px;

          .item {
            img {
              width: 100%;
              height: 100%;
              object-fit: cover;
            }
          }
        }
      }

      .right-wrap {
        flex: 1;
        overflow: hidden;
        border-radius: $box-radius;

        .info {
          background: var(--art-main-bg-color);
          border-radius: $box-radius;

          .title {
            padding: 15px 25px;
            font-size: 20px;
            font-weight: 400;
            color: var(--art-text-gray-800);
            border-bottom: 1px solid var(--art-border-color);
          }

          .form {
            box-sizing: border-box;
            padding: 30px 25px;

            > .el-row {
              .el-form-item {
                width: calc(50% - 10px);
              }

              .el-input,
              .el-select {
                width: 100%;
              }
            }

            .right-input {
              margin-left: 20px;
            }

            .el-form-item-right {
              display: flex;
              align-items: center;
              justify-content: end;

              .el-button {
                width: 110px !important;
              }
            }
          }
        }
      }
    }
  }

  @media only screen and (max-width: $device-ipad-vertical) {
    .page-content {
      .content {
        display: block;
        margin-top: 5px;

        .left-wrap {
          width: 100%;
        }

        .right-wrap {
          width: 100%;
          margin-top: 15px;
        }
      }
    }
  }
</style>
