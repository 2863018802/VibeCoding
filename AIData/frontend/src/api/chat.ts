import client from './client'

export interface StreamChunk {
  type: 'content' | 'sql' | 'chart_data' | 'done'
  content: string
}

// Mock data for Phase 2 demo
const MOCK_DATA: Record<string, { data: Record<string, unknown>[]; description: string }> = {
  '各品类销售额统计': {
    description: '各品类销售额统计',
    data: [
      { 品类: 'Electronics', 销售额: 58496 },
      { 品类: 'Home Appliances', 销售额: 29394 },
      { 品类: 'Cosmetics', 销售额: 30026 },
      { 品类: 'Fashion', 销售额: 39994 },
      { 品类: 'Books & Media', 销售额: 14289 },
    ],
  },
  'VIP客户订单分析': {
    description: 'VIP客户订单分析',
    data: [
      { 客户: '张伟', 订单数: 28, 消费额: 58932 },
      { 客户: '王芳', 订单数: 24, 消费额: 51204 },
      { 客户: '周杰', 订单数: 21, 消费额: 43891 },
      { 客户: '赵雷', 订单数: 19, 消费额: 39102 },
      { 客户: '胡歌', 订单数: 17, 消费额: 35120 },
    ],
  },
  '月销量趋势': {
    description: '月销量趋势',
    data: [
      { 月份: '1月', 订单数: 128, 销售额: 89234 },
      { 月份: '2月', 订单数: 142, 销售额: 98456 },
      { 月份: '3月', 订单数: 135, 销售额: 92100 },
      { 月份: '4月', 订单数: 158, 销售额: 110234 },
      { 月份: '5月', 订单数: 162, 销售额: 115678 },
    ],
  },
  '产品库存预警': {
    description: '产品库存预警',
    data: [
      { 产品: '戴森V15吸尘器', 库存: 35, 预警阈值: 50 },
      { 产品: 'Apple Watch Ultra 2', 库存: 60, 预警阈值: 80 },
      { 产品: 'MacBook Pro 16"', 库存: 45, 预警阈值: 60 },
      { 产品: 'Nike Air Max', 库存: 250, 预警阈值: 200 },
      { 产品: '施华洛世奇项链', 库存: 80, 预警阈值: 100 },
    ],
  },
}

function getMockChartData(query: string): Record<string, unknown>[] | null {
  for (const key of Object.keys(MOCK_DATA)) {
    if (query.includes(key.slice(0, 4))) return MOCK_DATA[key].data
  }
  return MOCK_DATA['月销量趋势'].data
}

function getMockResponse(query: string): string {
  if (query.includes('品类') || query.includes('分类')) {
    return '根据查询，我为您统计了各品类的销售额。Electronics（电子产品）以约58,496元位居第一，其次是Fashion（时尚）和Cosmetics（美妆）。'
  }
  if (query.includes('VIP') || query.includes('客户')) {
    return '以下是VIP客户的订单分析。可以看到张伟、王芳、周杰三位金卡客户的消费额最高，建议重点维护。'
  }
  if (query.includes('月') || query.includes('趋势')) {
    return '从近5个月的销量趋势来看，订单数和销售额整体呈上升趋势。5月达到峰值，约115,678元。'
  }
  if (query.includes('库存') || query.includes('预警')) {
    return '库存预警分析完成。以下产品的当前库存低于预警阈值，建议及时补货。'
  }
  return '好的，我来分析这个问题。以下是查询结果的汇总：'
}

export const chatApi = {
  stream: async function* (
    sessionId: number,
    query: string,
    onChunk: (chunk: string) => void
  ): AsyncGenerator<string, void, unknown> {
    // Mock streaming: simulate typing effect
    const response = getMockResponse(query)
    const chartData = getMockChartData(query)

    for (const char of response) {
      onChunk(char)
      yield char
      await new Promise((r) => setTimeout(r, 20))
    }

    // Simulate a pause, then done
    onChunk('')
  },

  getMockChartData,
}
