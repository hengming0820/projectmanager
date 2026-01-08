<template>
  <el-header height="auto" :class="['art-page-header', `theme-${theme}`]">
    <div class="header-content">
      <div class="header-left">
        <div class="title-wrapper">
          <h2>
            <span v-if="icon" class="title-icon">{{ icon }}</span>
            {{ title }}
          </h2>
          <span v-if="badge" class="title-badge">{{ badge }}</span>
        </div>
        <p v-if="description">{{ description }}</p>
      </div>
      <div class="header-right">
        <slot name="actions"></slot>
      </div>
    </div>
  </el-header>
</template>

<script setup lang="ts">
  interface Props {
    title: string
    description?: string
    icon?: string
    badge?: string
    theme?: 'purple' | 'blue' | 'green' | 'orange' | 'red' | 'cyan' | 'pink' | 'default'
  }

  withDefaults(defineProps<Props>(), {
    theme: 'default'
  })
</script>

<style scoped lang="scss">
  .art-page-header {
    padding: 20px 24px;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    margin-bottom: 20px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;

    &:hover {
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 20px;

      .header-left {
        flex: 1;
        min-width: 0;

        .title-wrapper {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 6px;

          h2 {
            margin: 0;
            font-size: 20px;
            font-weight: 600;
            color: #111827; // Gray-900
            display: flex;
            align-items: center;
            gap: 8px;
            letter-spacing: -0.025em;

            .title-icon {
              font-size: 24px;
              display: flex;
              align-items: center;
              justify-content: center;
            }
          }

          .title-badge {
            display: inline-flex;
            align-items: center;
            padding: 2px 10px;
            font-size: 12px;
            font-weight: 500;
            border-radius: 9999px;
            white-space: nowrap;
          }
        }

        p {
          margin: 0;
          font-size: 14px;
          color: #6b7280; // Gray-500
          line-height: 1.5;
        }
      }

      .header-right {
        display: flex;
        gap: 12px;
        align-items: center;
        flex-shrink: 0;
      }
    }

    // Theme Variations (Minimalist)
    // Defines accent colors for icon and badge
    
    &.theme-purple {
      .title-icon { color: #8b5cf6; }
      .title-badge { background: #f5f3ff; color: #7c3aed; border: 1px solid #ddd6fe; }
    }

    &.theme-blue {
      .title-icon { color: #3b82f6; }
      .title-badge { background: #eff6ff; color: #2563eb; border: 1px solid #dbeafe; }
    }

    &.theme-green {
      .title-icon { color: #10b981; }
      .title-badge { background: #ecfdf5; color: #059669; border: 1px solid #d1fae5; }
    }

    &.theme-orange {
      .title-icon { color: #f97316; }
      .title-badge { background: #fff7ed; color: #ea580c; border: 1px solid #ffedd5; }
    }

    &.theme-red {
      .title-icon { color: #ef4444; }
      .title-badge { background: #fef2f2; color: #dc2626; border: 1px solid #fee2e2; }
    }

    &.theme-cyan {
      .title-icon { color: #06b6d4; }
      .title-badge { background: #ecfeff; color: #0891b2; border: 1px solid #cffafe; }
    }

    &.theme-pink {
      .title-icon { color: #ec4899; }
      .title-badge { background: #fdf2f8; color: #db2777; border: 1px solid #fce7f3; }
    }
    
    &.theme-default {
       .title-icon { color: #6b7280; }
       .title-badge { background: #f3f4f6; color: #4b5563; border: 1px solid #e5e7eb; }
    }
  }
</style>