<!-- 项目分类标签组件 -->
<template>
  <el-tag
    v-if="category && subCategory"
    :type="tagType"
    :color="tagColor"
    effect="dark"
    :size="size"
    class="category-tag"
    :style="{
      color: '#ffffff',
      fontWeight: '600',
      textShadow: '0 1px 2px rgba(0,0,0,0.3)'
    }"
  >
    {{ displayText }}
  </el-tag>
  <span v-else class="text-gray-400">{{ emptyText }}</span>
</template>

<script setup lang="ts">
  import { computed } from 'vue'

  interface Props {
    category?: string
    subCategory?: string
    size?: 'large' | 'default' | 'small'
    emptyText?: string
  }

  const props = withDefaults(defineProps<Props>(), {
    size: 'small',
    emptyText: '-'
  })

  // 分类显示文本映射
  const categoryDisplayMap = {
    case: '病例',
    ai_annotation: 'AI标注'
  }

  const subCategoryDisplayMap = {
    trial: '试用',
    research: '研发', // 病例-研发
    paid: '收费',
    research_ai: '科研', // AI标注-科研 (更名避免歧义)
    daily: '日常'
  }

  // 标签类型映射
  type TagType = 'success' | 'warning' | 'info' | 'primary' | 'danger'
  const tagTypeMap: Record<string, TagType> = {
    'case-trial': 'info',
    'case-research': 'primary',
    'case-paid': 'success',
    'ai_annotation-research_ai': 'warning',
    'ai_annotation-daily': 'danger'
  }

  // 标签颜色映射 - 优化对比度
  const tagColorMap = {
    'case-trial': '#6c757d', // 深灰色 - 试用
    'case-research': '#0d6efd', // 深蓝色 - 研发
    'case-paid': '#198754', // 深绿色 - 收费
    'ai_annotation-research_ai': '#fd7e14', // 深橙色 - AI科研
    'ai_annotation-daily': '#dc3545' // 深红色 - AI日常
  }

  // 计算显示文本
  const displayText = computed(() => {
    if (!props.category || !props.subCategory) return ''

    const categoryText =
      categoryDisplayMap[props.category as keyof typeof categoryDisplayMap] || props.category
    const subCategoryText =
      subCategoryDisplayMap[props.subCategory as keyof typeof subCategoryDisplayMap] ||
      props.subCategory

    return `${categoryText}-${subCategoryText}`
  })

  // 计算标签类型
  const tagType = computed<TagType>(() => {
    if (!props.category || !props.subCategory) return 'info'

    const key = `${props.category}-${props.subCategory}`
    return tagTypeMap[key as keyof typeof tagTypeMap] || 'info'
  })

  // 计算标签颜色
  const tagColor = computed(() => {
    if (!props.category || !props.subCategory) return '#909399'

    const key = `${props.category}-${props.subCategory}`
    return tagColorMap[key as keyof typeof tagColorMap] || '#909399'
  })
</script>

<style scoped lang="scss">
  .category-tag {
    font-weight: 500;
    border-radius: 4px;

    &.el-tag--light {
      border-width: 1px;
    }
  }

  .text-gray-400 {
    color: #9ca3af;
    font-size: 12px;
  }
</style>
