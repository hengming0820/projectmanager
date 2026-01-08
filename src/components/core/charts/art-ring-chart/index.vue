<!-- 环形图 -->
<template>
  <div
    ref="chartRef"
    class="art-ring-chart"
    :style="{ height: props.height }"
    v-loading="props.loading"
  >
  </div>
</template>

<script setup lang="ts">
  import type { EChartsOption } from 'echarts'
  import { useChartOps, useChartComponent } from '@/composables/useChart'
  import type { RingChartProps } from '@/types/component/chart'

  defineOptions({ name: 'ArtRingChart' })

  const props = withDefaults(defineProps<RingChartProps>(), {
    // 基础配置
    height: useChartOps().chartHeight,
    loading: false,
    isEmpty: false,
    colors: () => useChartOps().colors,

    // 数据配置
    data: () => [],
    radius: () => ['50%', '80%'],
    borderRadius: 10,
    centerText: '',
    showLabel: true,

    // 交互配置
    showTooltip: true,
    showLegend: false,
    legendPosition: 'right'
  })

  // 使用新的图表组件抽象
  const { chartRef, isDark, getAnimationConfig, getTooltipStyle, getLegendStyle } =
    useChartComponent({
      props,
      checkEmpty: () => {
        return !props.data?.length || props.data.every((item) => item.value === 0)
      },
      watchSources: [() => props.data, () => props.centerText],
      generateOptions: (): EChartsOption => {
        // 根据图例位置计算环形图中心位置
        const getCenterPosition = (): [string, string] => {
          if (!props.showLegend) return ['50%', '50%']

          switch (props.legendPosition) {
            case 'left':
              return ['60%', '50%']
            case 'right':
              return ['40%', '50%']
            case 'top':
              return ['50%', '58%']
            case 'bottom':
              return ['50%', '50%']
            default:
              return ['50%', '50%']
          }
        }

        const option: EChartsOption = {
          tooltip: props.showTooltip
            ? getTooltipStyle('item', {
                formatter: '{b}: {c} ({d}%)'
              })
            : undefined,
          legend: props.showLegend ? getLegendStyle(props.legendPosition) : undefined,
          series: [
            {
              name: '数据占比',
              type: 'pie',
              radius: props.radius,
              center: getCenterPosition(),
              avoidLabelOverlap: true,
              itemStyle: {
                borderRadius: props.borderRadius,
                borderColor: isDark.value ? '#2c2c2c' : '#fff',
                borderWidth: 0
              },
              label: {
                show: props.showLabel,
                formatter: function (params: any) {
                  // 所有扇形都显示标签
                  if (params.percent < 1) {
                    return '' // 小于1%不显示
                  } else if (params.percent < 4) {
                    return `${params.percent}%` // 只显示百分比
                  } else {
                    return `${params.name}\n${params.percent}%` // 显示名称和百分比
                  }
                },
                position: 'outside',
                color: isDark.value ? '#e5e7eb' : '#333',
                fontSize: 11,
                lineHeight: 14,
                fontWeight: 'bold',
                backgroundColor: isDark.value
                  ? 'rgba(30, 30, 30, 0.9)'
                  : 'rgba(255, 255, 255, 0.9)',
                borderColor: isDark.value ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.1)',
                borderWidth: 1,
                borderRadius: 3,
                padding: [2, 6],
                distanceToLabelLine: 3,
                alignTo: 'none',
                bleedMargin: 10
              },
              labelLine: {
                show: props.showLabel,
                length: 10,
                length2: 8,
                smooth: false,
                showAbove: true,
                lineStyle: {
                  color: isDark.value ? '#555' : '#999',
                  width: 1
                }
              },
              emphasis: {
                label: {
                  show: false,
                  fontSize: 14,
                  fontWeight: 'bold'
                }
              },
              // 删除重复的 labelLine 定义，保持上方定义
              data: props.data,
              color: props.colors,
              ...getAnimationConfig(),
              animationType: 'expansion'
            }
          ]
        }

        // 添加中心文字
        if (props.centerText) {
          const centerPos = getCenterPosition()
          option.title = {
            text: props.centerText,
            left: centerPos[0],
            top: centerPos[1],
            textAlign: 'center',
            textVerticalAlign: 'middle',
            textStyle: {
              fontSize: 18,
              fontWeight: 500,
              color: isDark.value ? '#9ca3af' : '#6b7280'
            }
          }
        }

        return option
      }
    })
</script>

<style lang="scss" scoped>
  .art-ring-chart {
    position: relative;
    width: 100%;
  }
</style>
