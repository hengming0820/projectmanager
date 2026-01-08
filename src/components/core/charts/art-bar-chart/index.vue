<!-- 柱状图 -->
<template>
  <div ref="chartRef" :style="{ height: props.height }" v-loading="props.loading"> </div>
</template>

<script setup lang="ts">
  import { useChartOps, useChartComponent } from '@/composables/useChart'
  import { getCssVar } from '@/utils/ui'
  import type { EChartsOption } from 'echarts'
  import type { BarChartProps, BarDataItem } from '@/types/component/chart'
  import * as echarts from 'echarts'

  defineOptions({ name: 'ArtBarChart' })

  const props = withDefaults(defineProps<BarChartProps>(), {
    // 基础配置
    height: useChartOps().chartHeight,
    loading: false,
    isEmpty: false,
    colors: () => useChartOps().colors,
    borderRadius: 4,

    // 数据配置
    data: () => [0, 0, 0, 0, 0, 0, 0],
    xAxisData: () => [],
    barWidth: '40%',
    stack: false,
    barGap: '30%', // 柱间距离
    barCategoryGap: '20%', // 类目间距离
    showLabel: true, // 默认显示数据标签

    // 轴线显示配置
    showAxisLabel: true,
    showAxisLine: true,
    showSplitLine: true,

    // 交互配置
    showTooltip: true,
    showLegend: false,
    legendPosition: 'bottom'
  })

  // 判断是否为多数据
  const isMultipleData = computed(() => {
    return (
      Array.isArray(props.data) &&
      props.data.length > 0 &&
      typeof props.data[0] === 'object' &&
      'name' in props.data[0]
    )
  })

  // 获取颜色配置
  const getColor = (customColor?: string, index?: number) => {
    if (customColor) return customColor

    if (index !== undefined) {
      return props.colors![index % props.colors!.length]
    }

    // 默认渐变色
    return new echarts.graphic.LinearGradient(0, 0, 0, 1, [
      {
        offset: 0,
        color: getCssVar('--el-color-primary-light-4')
      },
      {
        offset: 1,
        color: getCssVar('--el-color-primary')
      }
    ])
  }

  // 创建渐变色
  const createGradientColor = (color: string) => {
    return new echarts.graphic.LinearGradient(0, 0, 0, 1, [
      {
        offset: 0,
        color: color
      },
      {
        offset: 1,
        color: color
      }
    ])
  }

  // 获取基础样式配置
  const getBaseItemStyle = (color: any) => ({
    borderRadius: props.borderRadius,
    color: typeof color === 'string' ? createGradientColor(color) : color
  })

  // 创建系列配置
  const createSeriesItem = (config: {
    name?: string
    data: number[]
    color?: string | echarts.graphic.LinearGradient
    barWidth?: string | number
    stack?: string
    barGap?: string
    barCategoryGap?: string
  }) => {
    const animationConfig = getAnimationConfig()

    return {
      name: config.name,
      data: config.data,
      type: 'bar' as const,
      stack: config.stack,
      itemStyle: getBaseItemStyle(config.color),
      barWidth: config.barWidth || props.barWidth,
      barGap: config.barGap,
      barCategoryGap: config.barCategoryGap,
      label: props.showLabel
        ? {
            show: true,
            position: config.stack ? ('inside' as const) : ('top' as const),
            color: config.stack ? '#fff' : isDark.value ? '#e5e7eb' : '#333',
            fontSize: 11,
            fontWeight: 600,
            distance: 5,
            backgroundColor: config.stack
              ? 'transparent'
              : isDark.value
                ? 'rgba(30, 30, 30, 0.8)'
                : 'rgba(255, 255, 255, 0.8)',
            borderColor: config.stack
              ? 'transparent'
              : isDark.value
                ? 'rgba(255, 255, 255, 0.15)'
                : 'rgba(0, 0, 0, 0.1)',
            borderWidth: config.stack ? 0 : 1,
            borderRadius: 2,
            padding: [2, 4],
            formatter: function (params: any) {
              // 只显示非0值的标签，避免0值标签遮挡
              return params.value > 0 ? params.value : ''
            }
          }
        : {
            show: false
          },
      ...animationConfig
    }
  }

  // 使用新的图表组件抽象
  const {
    chartRef,
    isDark,
    getAxisLineStyle,
    getAxisLabelStyle,
    getAxisTickStyle,
    getSplitLineStyle,
    getAnimationConfig,
    getTooltipStyle,
    getLegendStyle,
    getGridWithLegend
  } = useChartComponent({
    props,
    checkEmpty: () => {
      // 检查单数据情况
      if (Array.isArray(props.data) && typeof props.data[0] === 'number') {
        const singleData = props.data as number[]
        return !singleData.length || singleData.every((val) => val === 0)
      }

      // 检查多数据情况
      if (Array.isArray(props.data) && typeof props.data[0] === 'object') {
        const multiData = props.data as BarDataItem[]
        return (
          !multiData.length ||
          multiData.every((item) => !item.data?.length || item.data.every((val) => val === 0))
        )
      }

      return true
    },
    watchSources: [() => props.data, () => props.xAxisData, () => props.colors],
    generateOptions: (): EChartsOption => {
      const options: EChartsOption = {
        grid: getGridWithLegend(props.showLegend && isMultipleData.value, props.legendPosition, {
          top: 35, // 增加顶部空间以显示标签
          right: 0,
          left: 0,
          bottom: 20 // 确保底部也有足够空间
        }),
        tooltip: props.showTooltip ? getTooltipStyle() : undefined,
        xAxis: {
          type: 'category',
          data: props.xAxisData,
          axisTick: getAxisTickStyle(),
          axisLine: getAxisLineStyle(props.showAxisLine),
          axisLabel: getAxisLabelStyle(props.showAxisLabel)
        },
        yAxis: {
          type: 'value',
          axisLabel: getAxisLabelStyle(props.showAxisLabel),
          axisLine: getAxisLineStyle(props.showAxisLine),
          splitLine: getSplitLineStyle(props.showSplitLine)
        }
      }

      // 添加图例配置
      if (props.showLegend && isMultipleData.value) {
        options.legend = getLegendStyle(props.legendPosition)
      }

      // 生成系列数据
      if (isMultipleData.value) {
        const multiData = props.data as BarDataItem[]
        options.series = multiData.map((item, index) => {
          const computedColor = getColor(props.colors[index], index)

          return createSeriesItem({
            name: item.name,
            data: item.data,
            color: computedColor,
            barWidth: item.barWidth,
            stack: props.stack ? item.stack || 'total' : undefined,
            barGap: index === 0 ? (props as any).barGap : undefined,
            barCategoryGap: index === 0 ? (props as any).barCategoryGap : undefined
          })
        })
      } else {
        // 单数据情况
        const singleData = props.data as number[]

        // 如果提供了多个颜色，为每个柱子设置不同颜色
        if (props.colors && props.colors.length > 1) {
          const dataWithColors = singleData.map((value, index) => ({
            value: value,
            itemStyle: {
              color: createGradientColor(props.colors[index % props.colors.length]),
              borderRadius: props.borderRadius
            }
          }))

          options.series = [
            {
              data: dataWithColors,
              type: 'bar' as const,
              barWidth: props.barWidth,
              label: props.showLabel
                ? {
                    show: true,
                    position: 'top' as const,
                    color: isDark.value ? '#e5e7eb' : '#333',
                    fontSize: 11,
                    fontWeight: 600,
                    distance: 5,
                    backgroundColor: isDark.value
                      ? 'rgba(30, 30, 30, 0.8)'
                      : 'rgba(255, 255, 255, 0.8)',
                    borderColor: isDark.value ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.1)',
                    borderWidth: 1,
                    borderRadius: 2,
                    padding: [2, 4],
                    formatter: function (params: any) {
                      return params.value > 0 ? params.value : ''
                    }
                  }
                : {
                    show: false
                  },
              ...getAnimationConfig()
            }
          ]
        } else {
          // 使用默认颜色
          const computedColor = getColor()
          options.series = [
            createSeriesItem({
              data: singleData,
              color: computedColor
            })
          ]
        }
      }

      return options
    }
  })
</script>
