<!-- 统计卡片 -->
<template>
  <el-card class="stats-card art-custom-card" :style="{ backgroundColor: backgroundColor }">
    <div
      v-if="icon"
      class="stats-card__icon"
      :style="{ backgroundColor: iconBgColor, borderRadius: iconBgRadius + 'px' }"
    >
      <i
        class="iconfont-sys"
        v-html="icon"
        :style="{
          color: iconColor,
          fontSize: iconSize + 'px'
        }"
      ></i>
    </div>
    <div class="stats-card__content">
      <p class="stats-card__title" :style="{ color: textColor }" v-if="title">
        {{ title }}
      </p>
      <p v-if="value !== undefined" class="stats-card__count" :style="{ color: textColor }">
        {{ value }}
      </p>
      <ArtCountTo
        v-else-if="count !== undefined"
        class="stats-card__count"
        :target="count"
        :duration="2000"
        :decimals="decimals"
        :separator="separator"
      />
      <p class="stats-card__description" :style="{ color: textColor }" v-if="description">{{
        description
      }}</p>
    </div>
    <div class="stats-card__arrow" v-if="showArrow">
      <i class="iconfont-sys">&#xe703;</i>
    </div>
  </el-card>
</template>

<script setup lang="ts">
  defineOptions({ name: 'ArtStatsCard' })

  interface StatsCardProps {
    /** 图标 */
    icon?: string
    /** 标题 */
    title?: string
    /** 文本值 (优先显示) */
    value?: string | number
    /** 数值 (动画显示) */
    count?: number
    /** 小数位 */
    decimals?: number
    /** 分隔符 */
    separator?: string
    /** 描述 */
    description: string
    /** 图标颜色 */
    iconColor?: string
    /** 图标背景颜色 */
    iconBgColor?: string
    /** 图标圆角大小 */
    iconBgRadius?: number
    /** 图标大小 */
    iconSize?: number
    /** 文本颜色 */
    textColor?: string
    /** 背景颜色 */
    backgroundColor?: string
    /** 是否显示箭头 */
    showArrow?: boolean
  }

  withDefaults(defineProps<StatsCardProps>(), {
    iconSize: 30,
    iconBgRadius: 50,
    decimals: 0,
    separator: ','
  })
</script>

<style lang="scss" scoped>
  .stats-card {
    cursor: pointer;
    transition: transform 0.2s ease;

    &:hover {
      transform: translateY(-2px);
    }

    :deep(.el-card__body) {
      display: flex;
      align-items: center;
      height: 8rem;
      padding: 0 20px;
    }

    &__icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 46px;
      height: 46px;
      margin-right: 16px;
      border-radius: 50%;

      i {
        font-size: 30px;
      }
    }

    &__content {
      flex: 1;
    }

    &__title {
      margin: 0;
      font-size: 14px;
      font-weight: 500;
      color: var(--art-gray-600);
      margin-bottom: 8px;
    }

    &__count {
      margin: 0;
      font-size: 36px;
      font-weight: 700;
      color: var(--art-gray-900);
      line-height: 1.2;
    }

    &__description {
      margin: 6px 0 0;
      font-size: 13px;
      color: var(--art-gray-500);
      opacity: 0.85;
    }

    &__arrow {
      i {
        font-size: 18px;
        color: var(--art-gray-600);
      }
    }
  }
</style>
