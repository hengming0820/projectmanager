/**
 * 时间格式化工具
 * 解决后端返回UTC时间缺少'Z'标识导致的8小时时差问题
 */

/**
 * 修复UTC时间字符串（添加缺失的'Z'标识）
 * @param timeStr - 时间字符串
 * @returns 修复后的时间字符串
 */
export function fixUTCTimeString(timeStr: string | null | undefined): string | null {
  if (!timeStr) return null

  let fixedStr = timeStr.trim()

  // 1. 已经是标准UTC格式（带Z）：2025-10-31T10:00:00Z
  if (fixedStr.endsWith('Z')) {
    return fixedStr
  }

  // 2. 带时区偏移格式：2025-10-31T10:00:00+00:00 或 2025-10-31 10:00:00+00:00
  //    这是Redis缓存可能返回的格式（修复前）
  if (fixedStr.includes('+00:00') || fixedStr.includes('-00:00')) {
    // 替换空格为T，并将+00:00替换为Z
    return (
      fixedStr.replace(' ', 'T').replace('+00:00', 'Z').replace('-00:00', 'Z').split('.')[0] + 'Z'
    ) // 去除可能的毫秒部分
  }

  // 3. 包含其他时区偏移：2025-10-31T10:00:00+08:00
  //    保持原样，JavaScript的Date可以正确解析
  if (fixedStr.match(/[+-]\d{2}:\d{2}$/)) {
    return fixedStr.replace(' ', 'T')
  }

  // 4. 缺少时区标识但有T分隔符：2025-10-31T10:00:00
  //    假定为UTC时间，添加Z标识
  if (fixedStr.includes('T') && !fixedStr.includes('Z')) {
    return fixedStr.split('.')[0] + 'Z'
  }

  // 5. 空格分隔格式：2025-10-31 10:00:00
  //    假定为UTC时间，转换为ISO格式
  if (fixedStr.includes(' ') && !fixedStr.includes('Z')) {
    fixedStr = fixedStr.replace(' ', 'T')
    return fixedStr.split('.')[0] + 'Z'
  }

  // 6. 其他格式，原样返回
  return fixedStr
}

/**
 * 格式化日期时间为本地时间字符串
 * @param date - 日期字符串或Date对象
 * @param format - 格式化选项，默认为完整日期时间
 * @returns 格式化后的字符串
 *
 * @example
 * formatDateTime('2025-10-22T10:00:00') // '2025/10/22 18:00:00' (自动转换UTC+8)
 * formatDateTime('2025-10-22T10:00:00Z', 'date') // '2025-10-22'
 * formatDateTime('2025-10-22T10:00:00', 'time') // '18:00:00'
 */
export function formatDateTime(
  date: string | Date | null | undefined,
  format: 'datetime' | 'date' | 'time' | 'full' = 'datetime'
): string {
  if (!date) return '-'

  try {
    // 如果是字符串，先修复UTC时间标识
    let dateObj: Date
    if (typeof date === 'string') {
      const fixedStr = fixUTCTimeString(date)
      if (!fixedStr) return '-'
      dateObj = new Date(fixedStr)
    } else {
      dateObj = date
    }

    // 验证日期是否有效
    if (isNaN(dateObj.getTime())) {
      console.warn('⚠️ [TimeFormat] 无效的时间格式:', date)
      return '-'
    }

    // 根据格式返回不同的字符串
    switch (format) {
      case 'date':
        // YYYY-MM-DD
        const year = dateObj.getFullYear()
        const month = String(dateObj.getMonth() + 1).padStart(2, '0')
        const day = String(dateObj.getDate()).padStart(2, '0')
        return `${year}-${month}-${day}`

      case 'time':
        // HH:mm:ss
        const hours = String(dateObj.getHours()).padStart(2, '0')
        const minutes = String(dateObj.getMinutes()).padStart(2, '0')
        const seconds = String(dateObj.getSeconds()).padStart(2, '0')
        return `${hours}:${minutes}:${seconds}`

      case 'full':
        // 使用浏览器本地化格式
        return dateObj.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false
        })

      case 'datetime':
      default:
        // YYYY/MM/DD HH:mm:ss
        return dateObj
          .toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
          })
          .replace(/\//g, '-')
    }
  } catch (error) {
    console.error('❌ [TimeFormat] 格式化时间失败:', error, date)
    return '-'
  }
}

/**
 * 格式化相对时间（如"3分钟前"）
 * @param iso - ISO时间字符串
 * @returns 相对时间字符串
 *
 * @example
 * formatTimeAgo('2025-10-22T10:00:00') // '3小时前'
 */
export function formatTimeAgo(iso: string | null | undefined): string {
  if (!iso) return '未知时间'

  try {
    // 修复UTC时间标识
    const fixedStr = fixUTCTimeString(iso)
    if (!fixedStr) return '未知时间'

    // 解析时间
    const date = new Date(fixedStr)

    // 验证日期是否有效
    if (isNaN(date.getTime())) {
      console.warn('⚠️ [TimeFormat] 无效的时间格式:', iso)
      return '未知时间'
    }

    // 计算时间差（毫秒）
    const now = new Date()
    const diff = Math.max(0, now.getTime() - date.getTime())

    const seconds = Math.floor(diff / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)
    const days = Math.floor(hours / 24)
    const months = Math.floor(days / 30)
    const years = Math.floor(days / 365)

    if (seconds < 60) return '刚刚'
    if (minutes < 60) return `${minutes} 分钟前`
    if (hours < 24) return `${hours} 小时前`
    if (days < 30) return `${days} 天前`
    if (months < 12) return `${months} 个月前`
    return `${years} 年前`
  } catch (error) {
    console.error('❌ [TimeFormat] 计算相对时间失败:', error, iso)
    return '未知时间'
  }
}

/**
 * 格式化日期为 YYYY-MM-DD
 * @param date - 日期字符串或Date对象
 * @returns 格式化后的日期字符串
 */
export function formatDate(date: string | Date | null | undefined): string {
  return formatDateTime(date, 'date')
}

/**
 * 格式化时间为 HH:mm:ss
 * @param date - 日期字符串或Date对象
 * @returns 格式化后的时间字符串
 */
export function formatTime(date: string | Date | null | undefined): string {
  return formatDateTime(date, 'time')
}
