"""
个人绩效PDF报告导出服务
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # 使用非GUI后端
import matplotlib.pyplot as plt
from matplotlib import font_manager
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# 注册中文字体（支持Windows和Linux/Docker环境）
def register_fonts():
    """注册中文字体，支持多平台"""
    import os
    import platform
    
    # 尝试Windows字体
    if platform.system() == 'Windows':
        try:
            win_font_paths = [
                ('C:/Windows/Fonts/simhei.ttf', 'SimHei'),
                ('C:/Windows/Fonts/simsun.ttc', 'SimSun'),
                ('C:/Windows/Fonts/msyh.ttc', 'Microsoft YaHei')
            ]
            for font_path, font_name in win_font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    logger.info(f"✅ 成功加载字体: {font_name} from {font_path}")
            
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
            plt.rcParams['axes.unicode_minus'] = False
            return 'SimHei', 'SimSun'
        except Exception as e:
            logger.warning(f"⚠️ Windows字体加载失败: {e}")
    
    # 尝试Linux/Docker字体（文泉驿字体）
    try:
        linux_font_paths = [
            ('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 'WQYZenHei'),
            ('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 'WQYMicroHei'),
            ('/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc', 'WQYZenHei'),
            ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 'NotoSans')
        ]
        
        font_loaded = False
        for font_path, font_name in linux_font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    logger.info(f"✅ 成功加载字体: {font_name} from {font_path}")
                    if not font_loaded:  # 设置第一个成功的字体为matplotlib默认
                        plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'DejaVu Sans']
                        plt.rcParams['axes.unicode_minus'] = False
                        font_loaded = True
                    break
                except Exception as e:
                    logger.warning(f"⚠️ 加载字体 {font_name} 失败: {e}")
        
        if font_loaded:
            return 'WQYZenHei', 'WQYZenHei'
    except Exception as e:
        logger.error(f"❌ Linux字体加载失败: {e}")
    
    # 降级方案：使用Helvetica
    logger.error("❌ 无法加载任何中文字体，PDF中文可能显示为乱码！")
    return 'Helvetica', 'Helvetica'

# 注册字体
FONT_NAME, FONT_NAME_SONG = register_fonts()
logger.info(f"📝 使用字体: {FONT_NAME} (正文), {FONT_NAME_SONG} (宋体)")


class PersonalPerformancePDFService:
    """个人绩效PDF报告生成服务"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """设置自定义样式"""
        # 标题样式
        self.styles.add(ParagraphStyle(
            name='ChineseTitle',
            parent=self.styles['Title'],
            fontName=FONT_NAME,
            fontSize=24,
            textColor=colors.HexColor('#1a73e8'),
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        # 副标题样式
        self.styles.add(ParagraphStyle(
            name='ChineseHeading1',
            parent=self.styles['Heading1'],
            fontName=FONT_NAME,
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # 正文样式
        self.styles.add(ParagraphStyle(
            name='ChineseBody',
            parent=self.styles['Normal'],
            fontName=FONT_NAME_SONG,
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            alignment=TA_LEFT
        ))
        
        # 表格标题样式
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontName=FONT_NAME,
            fontSize=10,
            textColor=colors.white,
            alignment=TA_CENTER
        ))
    
    def generate_personal_report(
        self,
        user_info: Dict[str, Any],
        overview_data: Dict[str, Any],
        trend_data: List[Dict[str, Any]],
        category_data: List[Dict[str, Any]],
        period_type: str = "monthly",
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> BytesIO:
        """
        生成个人绩效PDF报告
        
        Args:
            user_info: 用户信息 {username, real_name, department, hire_date}
            overview_data: 概览数据 {total_tasks, avg_time, fastest_time, daily_avg, daily_max}
            trend_data: 趋势数据 [{date, count}, ...]
            category_data: 分类统计 [{category, count}, ...]
            period_type: 报告类型 "monthly" 或 "yearly"
            year: 年份
            month: 月份（月度报告时使用）
        """
        buffer = BytesIO()
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # 构建PDF内容
        story = []
        
        # 1. 报告标题
        story.extend(self._create_title(period_type, year, month))
        
        # 2. 个人信息
        story.extend(self._create_user_info(user_info))
        
        # 3. 个人概览
        story.extend(self._create_overview(overview_data))
        
        # 4. 任务完成趋势图
        story.extend(self._create_trend_chart(trend_data, period_type))
        
        # 5. 分类统计图
        story.extend(self._create_category_chart(category_data))
        
        # 6. 页脚
        story.append(Spacer(1, 2*cm))
        story.append(Paragraph(
            f"报告生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}",
            self.styles['ChineseBody']
        ))
        
        # 生成PDF
        doc.build(story)
        buffer.seek(0)
        
        logger.info(f"✅ [PDFExport] 个人绩效报告生成成功: {user_info.get('real_name', 'Unknown')}")
        return buffer
    
    def _create_title(self, period_type: str, year: Optional[int], month: Optional[int]) -> List:
        """创建报告标题"""
        elements = []
        
        # 确定标题文本
        if period_type == "monthly":
            year = year or datetime.now().year
            month = month or datetime.now().month
            title = f"{year}年{month}月个人绩效报告"
        else:
            year = year or datetime.now().year
            title = f"{year}年度个人绩效报告"
        
        elements.append(Paragraph(title, self.styles['ChineseTitle']))
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _create_user_info(self, user_info: Dict[str, Any]) -> List:
        """创建个人信息部分"""
        elements = []
        
        elements.append(Paragraph("一、个人信息", self.styles['ChineseHeading1']))
        elements.append(Paragraph(
            "本节展示员工的基本信息，包括姓名、工号、所属部门和入职时间等关键信息。",
            self.styles['ChineseBody']
        ))
        elements.append(Spacer(1, 0.3*cm))
        
        # 创建信息表格
        data = [
            ['姓名', user_info.get('real_name', '-'), '部门', user_info.get('department', '-')],
            ['工号', user_info.get('username', '-'), '入职时间', user_info.get('hire_date', '-')]
        ]
        
        table = Table(data, colWidths=[3*cm, 5*cm, 3*cm, 5*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME_SONG),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
            ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#666666')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f5f5f5')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 1*cm))
        
        return elements
    
    def _create_overview(self, overview_data: Dict[str, Any]) -> List:
        """创建个人概览部分"""
        elements = []
        
        elements.append(Paragraph("二、绩效概览", self.styles['ChineseHeading1']))
        elements.append(Paragraph(
            "本节汇总了统计期内的核心绩效指标，包括任务完成总数、平均完成时间、最快完成时间以及日均完成量等关键数据，全面反映员工的工作效率和产出能力。",
            self.styles['ChineseBody']
        ))
        elements.append(Spacer(1, 0.3*cm))
        
        # 创建概览数据表格
        data = [
            ['指标', '数值'],
            ['完成总任务数', f"{overview_data.get('total_tasks', 0)} 个"],
            ['任务平均完成时间', f"{overview_data.get('avg_time', 0):.1f} 小时"],
            ['最快完成时间', f"{overview_data.get('fastest_time', 0):.1f} 小时"],
            ['每天平均完成数量', f"{overview_data.get('daily_avg', 0):.1f} 个"],
            ['单日最多完成数量', f"{overview_data.get('daily_max', 0)} 个"]
        ]
        
        table = Table(data, colWidths=[8*cm, 8*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME_SONG),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 10),
            # 斑马纹
            ('BACKGROUND', (0, 1), (-1, 1), colors.white),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#f5f5f5')),
            ('BACKGROUND', (0, 3), (-1, 3), colors.white),
            ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#f5f5f5')),
            ('BACKGROUND', (0, 5), (-1, 5), colors.white),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 1*cm))
        
        return elements
    
    def _create_trend_chart(self, trend_data: List[Dict[str, Any]], period_type: str) -> List:
        """创建任务完成趋势图"""
        elements = []
        
        elements.append(Paragraph("三、任务完成趋势", self.styles['ChineseHeading1']))
        elements.append(Paragraph(
            "本节通过折线图展示统计期内任务完成数量的时间趋势，帮助直观了解工作负荷的变化情况和工作节奏的稳定性。",
            self.styles['ChineseBody']
        ))
        elements.append(Spacer(1, 0.3*cm))
        
        if not trend_data:
            elements.append(Paragraph("暂无趋势数据", self.styles['ChineseBody']))
            return elements
        
        # 生成趋势图
        fig, ax = plt.subplots(figsize=(10, 4))
        
        dates = [item['date'] for item in trend_data]
        counts = [item['count'] for item in trend_data]
        
        ax.plot(dates, counts, marker='o', linewidth=2, color='#1a73e8', markersize=4)
        ax.fill_between(dates, counts, alpha=0.3, color='#1a73e8')
        
        ax.set_xlabel('日期', fontsize=10)
        ax.set_ylabel('完成任务数', fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_facecolor('#fafafa')
        
        # 旋转x轴标签
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # 保存图表到内存
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)
        
        # 添加图表到PDF
        img = Image(img_buffer, width=16*cm, height=6.4*cm)
        elements.append(img)
        elements.append(Spacer(1, 1*cm))
        
        return elements
    
    def _create_category_chart(self, category_data: List[Dict[str, Any]]) -> List:
        """创建分类统计图"""
        elements = []
        
        elements.append(Paragraph("四、分类统计", self.styles['ChineseHeading1']))
        elements.append(Paragraph(
            "本节按项目分类统计任务完成情况，通过饼图展示各分类任务的占比分布，通过柱状图展示各分类的具体任务数量，帮助了解工作重点和业务结构。",
            self.styles['ChineseBody']
        ))
        elements.append(Spacer(1, 0.3*cm))
        
        if not category_data:
            elements.append(Paragraph("暂无分类数据", self.styles['ChineseBody']))
            return elements
        
        # 生成饼图和柱状图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        categories = [item['category'] or '未分类' for item in category_data]
        counts = [item['count'] for item in category_data]
        
        # 饼图
        colors_pie = plt.cm.Set3(range(len(categories)))
        ax1.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90, colors=colors_pie)
        ax1.set_title('任务分类占比', fontsize=11)
        
        # 柱状图
        bars = ax2.bar(categories, counts, color='#1a73e8', alpha=0.7)
        ax2.set_xlabel('分类', fontsize=10)
        ax2.set_ylabel('任务数量', fontsize=10)
        ax2.set_title('任务分类数量', fontsize=11)
        ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        # 在柱状图上显示数值
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # 保存图表到内存
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)
        
        # 添加图表到PDF
        img = Image(img_buffer, width=16*cm, height=6.4*cm)
        elements.append(img)
        
        return elements


class TeamPerformancePDFService:
    """团队绩效PDF报告生成服务"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """设置自定义样式"""
        # 标题样式
        self.styles.add(ParagraphStyle(
            name='ChineseTitle',
            parent=self.styles['Title'],
            fontName=FONT_NAME,
            fontSize=24,
            textColor=colors.HexColor('#1a73e8'),
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        # 副标题样式
        self.styles.add(ParagraphStyle(
            name='ChineseHeading1',
            parent=self.styles['Heading1'],
            fontName=FONT_NAME,
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # 正文样式
        self.styles.add(ParagraphStyle(
            name='ChineseBody',
            parent=self.styles['Normal'],
            fontName=FONT_NAME_SONG,
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            alignment=TA_LEFT
        ))
    
    def generate_team_report(
        self,
        team_overview: Dict[str, Any],
        trend_data: List[Dict[str, Any]],
        ranking_data: List[Dict[str, Any]],
        member_details: List[Dict[str, Any]],
        category_data: List[Dict[str, Any]],
        period_type: str = "monthly",
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> BytesIO:
        """
        生成团队绩效PDF报告
        
        Args:
            team_overview: 团队概览 {total_members, total_tasks, skipped_tasks, completed_projects}
            trend_data: 趋势数据 [{date, count}, ...]
            ranking_data: 排行榜 [{rank, name, tasks, score}, ...]
            member_details: 成员详情 [{name, tasks, categories}, ...]
            category_data: 分类统计 [{category, count}, ...]
            period_type: 报告类型 "monthly" 或 "yearly"
            year: 年份
            month: 月份（月度报告时使用）
        """
        buffer = BytesIO()
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # 构建PDF内容
        story = []
        
        # 1. 报告标题
        story.extend(self._create_title(period_type, year, month))
        
        # 2. 团队概览
        story.extend(self._create_team_overview(team_overview))
        
        # 3. 团队趋势图
        story.extend(self._create_team_trend_chart(trend_data, period_type))
        
        # 4. 绩效排行榜
        story.extend(self._create_ranking_table(ranking_data))
        
        # 5. 成员详细数据
        story.extend(self._create_member_details(member_details))
        
        # 6. 分类统计
        story.extend(self._create_category_chart(category_data))
        
        # 7. 页脚
        story.append(Spacer(1, 2*cm))
        story.append(Paragraph(
            f"报告生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}",
            self.styles['ChineseBody']
        ))
        
        # 生成PDF
        doc.build(story)
        buffer.seek(0)
        
        logger.info(f"✅ [PDFExport] 团队绩效报告生成成功")
        return buffer
    
    def _create_title(self, period_type: str, year: Optional[int], month: Optional[int]) -> List:
        """创建报告标题"""
        elements = []
        
        # 确定标题文本
        if period_type == "monthly":
            year = year or datetime.now().year
            month = month or datetime.now().month
            title = f"{year}年{month}月团队绩效报告"
        else:
            year = year or datetime.now().year
            title = f"{year}年度团队绩效报告"
        
        elements.append(Paragraph(title, self.styles['ChineseTitle']))
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _create_team_overview(self, overview: Dict[str, Any]) -> List:
        """创建团队概览部分"""
        elements = []
        
        elements.append(Paragraph("一、团队概览", self.styles['ChineseHeading1']))
        elements.append(Paragraph(
            "本节汇总了团队整体绩效数据，包括团队总人数、完成任务总数、跳过任务数以及完成的项目数量，全面反映团队的整体工作成果。",
            self.styles['ChineseBody']
        ))
        elements.append(Spacer(1, 0.3*cm))
        
        # 创建概览数据表格
        data = [
            ['指标', '数值'],
            ['团队总人数', f"{overview.get('total_members', 0)} 人"],
            ['完成总任务数', f"{overview.get('total_tasks', 0)} 个"],
            ['跳过任务数', f"{overview.get('skipped_tasks', 0)} 个"],
            ['完成项目数', f"{overview.get('completed_projects', 0)} 个"]
        ]
        
        table = Table(data, colWidths=[8*cm, 8*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME_SONG),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, 1), colors.white),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#f5f5f5')),
            ('BACKGROUND', (0, 3), (-1, 3), colors.white),
            ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#f5f5f5')),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 1*cm))
        
        return elements
    
    def _create_team_trend_chart(self, trend_data: List[Dict[str, Any]], period_type: str) -> List:
        """创建团队任务完成趋势图"""
        elements = []
        
        elements.append(Paragraph("二、任务完成趋势", self.styles['ChineseHeading1']))
        elements.append(Paragraph(
            "本节通过折线图展示团队在统计期内的任务完成数量趋势，帮助了解团队整体的工作负荷变化和产出节奏。",
            self.styles['ChineseBody']
        ))
        elements.append(Spacer(1, 0.3*cm))
        
        if not trend_data:
            elements.append(Paragraph("暂无趋势数据", self.styles['ChineseBody']))
            return elements
        
        # 生成趋势图
        fig, ax = plt.subplots(figsize=(10, 4))
        
        dates = [item['date'] for item in trend_data]
        counts = [item['count'] for item in trend_data]
        
        ax.plot(dates, counts, marker='o', linewidth=2, color='#1a73e8', markersize=4)
        ax.fill_between(dates, counts, alpha=0.3, color='#1a73e8')
        
        ax.set_xlabel('日期', fontsize=10)
        ax.set_ylabel('完成任务数', fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_facecolor('#fafafa')
        
        # 旋转x轴标签
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # 保存图表到内存
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)
        
        # 添加图表到PDF
        img = Image(img_buffer, width=16*cm, height=6.4*cm)
        elements.append(img)
        elements.append(Spacer(1, 1*cm))
        
        return elements
    
    def _create_ranking_table(self, ranking_data: List[Dict[str, Any]]) -> List:
        """创建绩效排行榜"""
        elements = []
        
        elements.append(Paragraph("三、绩效排行榜", self.styles['ChineseHeading1']))
        elements.append(Paragraph(
            "本节展示团队成员绩效排名，根据任务完成数量和质量评分综合排序，激励优秀员工，促进团队竞争氛围。",
            self.styles['ChineseBody']
        ))
        elements.append(Spacer(1, 0.3*cm))
        
        if not ranking_data:
            elements.append(Paragraph("暂无排行数据", self.styles['ChineseBody']))
            return elements
        
        # 创建排行榜表格
        table_data = [['排名', '姓名', '完成任务数', '综合评分']]
        
        for item in ranking_data[:20]:  # 最多显示前20名
            rank = item.get('rank', '-')
            name = item.get('name', '-')
            tasks = item.get('tasks', 0)
            score = item.get('score', 0)
            table_data.append([str(rank), name, f"{tasks} 个", f"{score:.1f}"])
        
        table = Table(table_data, colWidths=[3*cm, 5*cm, 4*cm, 4*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME_SONG),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
            # 前三名特殊标记
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#fff3cd')),  # 金色
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#e8f4f8')),  # 银色
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#ffe4c4')),  # 铜色
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 1*cm))
        
        return elements
    
    def _create_member_details(self, member_details: List[Dict[str, Any]]) -> List:
        """创建成员详细数据"""
        elements = []
        
        elements.append(Paragraph("四、成员详细数据", self.styles['ChineseHeading1']))
        elements.append(Paragraph(
            "本节展示每位团队成员的详细绩效数据，通过柱状图和数据表直观对比各成员的任务完成情况。",
            self.styles['ChineseBody']
        ))
        elements.append(Spacer(1, 0.3*cm))
        
        if not member_details:
            elements.append(Paragraph("暂无成员数据", self.styles['ChineseBody']))
            return elements
        
        # 生成成员柱状图
        fig, ax = plt.subplots(figsize=(10, 5))
        
        names = [item['name'] for item in member_details[:15]]  # 最多显示15人
        tasks = [item['tasks'] for item in member_details[:15]]
        
        bars = ax.bar(names, tasks, color='#1a73e8', alpha=0.7)
        ax.set_xlabel('成员', fontsize=10)
        ax.set_ylabel('完成任务数', fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        # 在柱状图上显示数值
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=8)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # 保存图表到内存
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)
        
        # 添加图表到PDF
        img = Image(img_buffer, width=16*cm, height=8*cm)
        elements.append(img)
        elements.append(Spacer(1, 0.5*cm))
        
        # 添加详细数据表
        table_data = [['姓名', '完成任务数', '主要项目分类']]
        for item in member_details[:15]:
            name = item.get('name', '-')
            task_count = item.get('tasks', 0)
            categories = item.get('categories', '-')
            table_data.append([name, f"{task_count} 个", categories])
        
        table = Table(table_data, colWidths=[5*cm, 5*cm, 6*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME_SONG),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 1*cm))
        
        return elements
    
    def _create_category_chart(self, category_data: List[Dict[str, Any]]) -> List:
        """创建分类统计图"""
        elements = []
        
        elements.append(Paragraph("五、项目分类统计", self.styles['ChineseHeading1']))
        elements.append(Paragraph(
            "本节按项目分类统计团队任务完成情况，通过饼图展示各分类任务的占比分布，通过柱状图展示各分类的具体任务数量，帮助了解团队工作重点和业务结构。",
            self.styles['ChineseBody']
        ))
        elements.append(Spacer(1, 0.3*cm))
        
        if not category_data:
            elements.append(Paragraph("暂无分类数据", self.styles['ChineseBody']))
            return elements
        
        # 生成饼图和柱状图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        categories = [item['category'] or '未分类' for item in category_data]
        counts = [item['count'] for item in category_data]
        
        # 饼图
        colors_pie = plt.cm.Set3(range(len(categories)))
        ax1.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90, colors=colors_pie)
        ax1.set_title('任务分类占比', fontsize=11)
        
        # 柱状图
        bars = ax2.bar(categories, counts, color='#1a73e8', alpha=0.7)
        ax2.set_xlabel('分类', fontsize=10)
        ax2.set_ylabel('任务数量', fontsize=10)
        ax2.set_title('任务分类数量', fontsize=11)
        ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        # 在柱状图上显示数值
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # 保存图表到内存
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)
        
        # 添加图表到PDF
        img = Image(img_buffer, width=16*cm, height=6.4*cm)
        elements.append(img)
        
        return elements


class ProjectReportPDFService:
    """项目报告PDF生成服务"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """设置自定义样式"""
        # 标题样式
        self.styles.add(ParagraphStyle(
            name='ChineseTitle',
            parent=self.styles['Title'],
            fontName=FONT_NAME,
            fontSize=24,
            textColor=colors.HexColor('#1a73e8'),
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        # 副标题样式
        self.styles.add(ParagraphStyle(
            name='ChineseHeading1',
            parent=self.styles['Heading1'],
            fontName=FONT_NAME,
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # 二级标题样式
        self.styles.add(ParagraphStyle(
            name='ChineseHeading2',
            parent=self.styles['Heading2'],
            fontName=FONT_NAME,
            fontSize=13,
            textColor=colors.HexColor('#1a73e8'),
            spaceAfter=8,
            spaceBefore=8
        ))
        
        # 正文样式
        self.styles.add(ParagraphStyle(
            name='ChineseBody',
            parent=self.styles['Normal'],
            fontName=FONT_NAME_SONG,
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            alignment=TA_LEFT
        ))
    
    def generate_project_report(
        self,
        project_info: Dict[str, Any],
        task_stats: Dict[str, Any],
        task_status_distribution: List[Dict[str, Any]],
        annotator_distribution: List[Dict[str, Any]],
        annotator_task_stats: List[Dict[str, Any]],
        task_list: List[Dict[str, Any]],
        article_chart_data: List[Dict[str, Any]] = None,
        article_stats: List[Dict[str, Any]] = None
    ) -> BytesIO:
        """
        生成项目报告PDF
        
        Args:
            project_info: 项目信息 {name, status, priority, category, sub_category, start_date, end_date, description, created_at}
            task_stats: 任务统计 {total, pending, in_progress, submitted, completed, rejected, skipped, completion_rate}
            task_status_distribution: 任务状态分布 [{name, value}, ...]
            annotator_distribution: 标注员完成分布 [{name, value}, ...]
            annotator_task_stats: 标注员任务统计 [{name, completed, in_progress, submitted, rejected, skipped, pending}, ...]
            task_list: 任务列表 [{title, status, assigned_to_name, priority, created_at}, ...]
            article_chart_data: 文章类型统计（柱状图用）[{type, count}, ...]
            article_stats: 文章详细统计 [{type, count, articles: [{title, author, status, created_at}]}, ...]
        """
        buffer = BytesIO()
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # 构建PDF内容
        story = []
        
        # 1. 报告标题
        story.extend(self._create_title(project_info))
        
        # 2. 项目信息
        story.extend(self._create_project_info(project_info))
        
        # 3. 项目进度统计
        story.extend(self._create_progress_stats(task_stats))
        
        # 4. 任务状态分布
        story.extend(self._create_task_status_chart(task_status_distribution))
        
        # 5. 标注员完成情况
        story.extend(self._create_annotator_chart(annotator_distribution))
        
        # 6. 标注员参与度分析
        story.extend(self._create_annotator_stats(annotator_task_stats))
        
        # 7. 任务列表
        story.extend(self._create_task_list(task_list))
        
        # 8. 文章统计
        if article_chart_data and article_stats:
            story.extend(self._create_article_stats(article_chart_data, article_stats))
        
        # 9. 页脚
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(
            f"报告生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}",
            self.styles['ChineseBody']
        ))
        
        # 生成PDF
        doc.build(story)
        buffer.seek(0)
        
        logger.info(f"✅ [PDFExport] 项目报告生成成功: {project_info.get('name', 'Unknown')}")
        return buffer
    
    def _create_title(self, project_info: Dict[str, Any]) -> List:
        """创建报告标题"""
        elements = []
        
        title = f"{project_info.get('name', '未知项目')} - 项目报告"
        elements.append(Paragraph(title, self.styles['ChineseTitle']))
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _create_project_info(self, project_info: Dict[str, Any]) -> List:
        """创建项目信息部分"""
        elements = []
        
        elements.append(Paragraph("一、项目信息", self.styles['ChineseHeading1']))
        elements.append(Paragraph(
            "本节展示项目的基本信息，包括项目名称、状态、优先级、分类、时间范围和描述等关键信息。",
            self.styles['ChineseBody']
        ))
        elements.append(Spacer(1, 0.2*cm))
        
        # 分类中英文映射
        status_map = {'active': '进行中', 'completed': '已完成', 'paused': '已暂停', 'cancelled': '已取消'}
        priority_map = {'low': '低', 'medium': '中', 'high': '高', 'urgent': '紧急'}
        category_map = {'case': '病例', 'ai_annotation': 'AI标注'}
        sub_category_map = {'trial': '试用', 'research': '研发', 'paid': '收费', 'research_ai': '科研', 'daily': '日常'}
        
        status_cn = status_map.get(project_info.get('status', ''), project_info.get('status', '-'))
        priority_cn = priority_map.get(project_info.get('priority', ''), project_info.get('priority', '-'))
        
        category = project_info.get('category', '')
        sub_category = project_info.get('sub_category', '')
        if category:
            category_cn = category_map.get(category, category)
            if sub_category:
                sub_category_cn = sub_category_map.get(sub_category, sub_category)
                category_display = f"{category_cn}-{sub_category_cn}"
            else:
                category_display = category_cn
        else:
            category_display = '-'
        
        # 创建信息表格
        data = [
            ['项目名称', project_info.get('name', '-'), '项目状态', status_cn],
            ['优先级', priority_cn, '项目分类', category_display],
            ['开始日期', project_info.get('start_date', '-'), '结束日期', project_info.get('end_date', '-')],
            ['创建时间', project_info.get('created_at', '-')[:10] if project_info.get('created_at') else '-', '', '']
        ]
        
        # 添加描述（单独一行）
        if project_info.get('description'):
            data.append(['项目描述', project_info.get('description', '-'), '', ''])
        
        table = Table(data, colWidths=[3*cm, 5*cm, 3*cm, 5*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME_SONG),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
            ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#666666')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f5f5f5')),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('SPAN', (3, -2), (-1, -2)),  # 合并创建时间行的后两列
        ]))
        
        # 如果有描述，合并描述行
        if project_info.get('description'):
            table.setStyle(TableStyle([
                ('SPAN', (1, -1), (-1, -1)),  # 合并描述行的后三列
            ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _create_progress_stats(self, task_stats: Dict[str, Any]) -> List:
        """创建项目进度统计部分"""
        elements = []
        
        elements.append(Paragraph("二、项目进度统计", self.styles['ChineseHeading1']))
        elements.append(Paragraph(
            "本节汇总了项目的任务完成情况，包括各状态的任务数量和整体完成率，直观展示项目进展。",
            self.styles['ChineseBody']
        ))
        elements.append(Spacer(1, 0.2*cm))
        
        # 创建统计数据表格
        data = [
            ['指标', '数值', '指标', '数值'],
            ['总任务数', f"{task_stats.get('total', 0)} 个", '待分配', f"{task_stats.get('pending', 0)} 个"],
            ['进行中', f"{task_stats.get('in_progress', 0)} 个", '已提交', f"{task_stats.get('submitted', 0)} 个"],
            ['已完成', f"{task_stats.get('completed', 0)} 个", '已驳回', f"{task_stats.get('rejected', 0)} 个"],
            ['已跳过', f"{task_stats.get('skipped', 0)} 个", '完成率', f"{task_stats.get('completion_rate', 0)}%"]
        ]
        
        table = Table(data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME_SONG),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, 1), colors.white),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#f5f5f5')),
            ('BACKGROUND', (0, 3), (-1, 3), colors.white),
            ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#f5f5f5')),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _create_task_status_chart(self, task_status_distribution: List[Dict[str, Any]]) -> List:
        """创建任务状态分布图"""
        elements = []
        
        elements.append(Paragraph("三、任务状态分布", self.styles['ChineseHeading1']))
        elements.append(Paragraph(
            "本节通过饼图展示各状态任务的数量分布，帮助了解项目当前的任务状态构成。",
            self.styles['ChineseBody']
        ))
        elements.append(Spacer(1, 0.2*cm))
        
        if not task_status_distribution:
            elements.append(Paragraph("暂无任务数据", self.styles['ChineseBody']))
            return elements
        
        # 生成饼图 - 使用正方形画布确保饼图是正圆
        fig, ax = plt.subplots(figsize=(5, 5))
        
        names = [item['name'] for item in task_status_distribution]
        values = [item['value'] for item in task_status_distribution]
        
        # 使用与页面一致的颜色
        color_map = {
            '待分配': '#f59e0b',
            '进行中': '#3b82f6',
            '已提交': '#8b5cf6',
            '已完成': '#10b981',
            '已驳回': '#ef4444',
            '已跳过': '#94a3b8'
        }
        colors_pie = [color_map.get(name, '#cccccc') for name in names]
        
        ax.pie(values, labels=names, autopct='%1.1f%%', startangle=90, colors=colors_pie, 
               textprops={'fontsize': 15})
        ax.set_title('任务状态分布', fontsize=18, pad=15)
        ax.axis('equal')  # 确保饼图是正圆
        
        plt.tight_layout()
        
        # 保存图表到内存
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)
        
        # 添加图表到PDF - 使用正方形尺寸（缩小到10cm）
        img = Image(img_buffer, width=8*cm, height=8*cm)
        elements.append(img)
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _create_annotator_chart(self, annotator_distribution: List[Dict[str, Any]]) -> List:
        """创建标注员完成情况图"""
        elements = []
        
        elements.append(Paragraph("四、标注员完成情况", self.styles['ChineseHeading1']))
        elements.append(Paragraph(
            "本节通过饼图展示各标注员已完成任务的数量分布。注：此处只统计已完成（approved）状态的任务。",
            self.styles['ChineseBody']
        ))
        elements.append(Spacer(1, 0.2*cm))
        
        if not annotator_distribution:
            elements.append(Paragraph("暂无标注员数据", self.styles['ChineseBody']))
            return elements
        
        # 只显示前10名
        top_annotators = annotator_distribution[:10]
        
        # 生成饼图 - 使用正方形画布确保饼图是正圆
        fig, ax = plt.subplots(figsize=(5, 5))
        
        names = [item['name'] for item in top_annotators]
        values = [item['value'] for item in top_annotators]
        
        colors_pie = plt.cm.Set2(range(len(names)))
        ax.pie(values, labels=names, autopct='%1.1f%%', startangle=90, colors=colors_pie,
               textprops={'fontsize': 15})
        
        # 添加总数显示
        total = sum(values)
        ax.set_title(f'标注员完成情况（Top 10）\n已完成任务总数: {total}', fontsize=18, pad=15)
        ax.axis('equal')  # 确保饼图是正圆
        
        plt.tight_layout()
        
        # 保存图表到内存
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)
        
        # 添加图表到PDF - 使用正方形尺寸（缩小到10cm）
        img = Image(img_buffer, width=8*cm, height=8*cm)
        elements.append(img)
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _create_annotator_stats(self, annotator_task_stats: List[Dict[str, Any]]) -> List:
        """创建标注员参与度分析"""
        elements = []
        
        elements.append(Paragraph("五、标注员参与度分析", self.styles['ChineseHeading1']))
        elements.append(Paragraph(
            "本节通过堆叠柱状图展示各标注员的任务状态分布，包含所有状态（待分配、进行中、已提交、已完成、已驳回、已跳过），全面了解每位成员的工作情况。",
            self.styles['ChineseBody']
        ))
        elements.append(Spacer(1, 0.2*cm))
        
        if not annotator_task_stats:
            elements.append(Paragraph("暂无标注员数据", self.styles['ChineseBody']))
            return elements
        
        # 显示所有标注员，不限制数量
        top_annotators = annotator_task_stats
        
        # 生成堆叠柱状图 - 根据人数动态调整图表大小
        num_annotators = len(top_annotators)
        fig_width = max(10, min(20, 3 + num_annotators * 1.5))  # 最小10，最大20
        fig_height = max(6, min(10, 5 + num_annotators * 0.3))  # 最小6，最大10
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        names = [item['name'] for item in top_annotators]
        pending = [item.get('pending', 0) for item in top_annotators]
        in_progress = [item.get('in_progress', 0) for item in top_annotators]
        submitted = [item.get('submitted', 0) for item in top_annotators]
        completed = [item.get('completed', 0) for item in top_annotators]
        rejected = [item.get('rejected', 0) for item in top_annotators]
        skipped = [item.get('skipped', 0) for item in top_annotators]
        
        x = range(len(names))
        width = max(0.4, min(0.7, 0.8 - num_annotators * 0.03))  # 根据人数调整柱子宽度
        
        # 堆叠柱状图（与页面一致的颜色）
        colors_stack = ['#f59e0b', '#3b82f6', '#8b5cf6', '#10b981', '#ef4444', '#94a3b8']
        
        ax.bar(x, pending, width, label='待分配', color=colors_stack[0])
        ax.bar(x, in_progress, width, bottom=pending, label='进行中', color=colors_stack[1])
        
        bottom = [p + i for p, i in zip(pending, in_progress)]
        ax.bar(x, submitted, width, bottom=bottom, label='已提交', color=colors_stack[2])
        
        bottom = [b + s for b, s in zip(bottom, submitted)]
        ax.bar(x, completed, width, bottom=bottom, label='已完成', color=colors_stack[3])
        
        bottom = [b + c for b, c in zip(bottom, completed)]
        ax.bar(x, rejected, width, bottom=bottom, label='已驳回', color=colors_stack[4])
        
        bottom = [b + r for b, r in zip(bottom, rejected)]
        ax.bar(x, skipped, width, bottom=bottom, label='已跳过', color=colors_stack[5])
        
        ax.set_xlabel('标注员', fontsize=11)
        ax.set_ylabel('任务数量', fontsize=11)
        ax.set_title(f'标注员参与度分析（共 {len(top_annotators)} 人）', fontsize=13, pad=15)
        ax.set_xticks(x)
        # 根据人数调整字体大小
        label_fontsize = max(7, min(10, 11 - num_annotators * 0.2))
        ax.set_xticklabels(names, rotation=45, ha='right', fontsize=label_fontsize)
        ax.legend(loc='upper right', fontsize=9, ncol=2)
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        plt.tight_layout()
        
        # 保存图表到内存
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)
        
        # 添加图表到PDF - 根据人数动态调整大小
        img_width = min(17, max(12, 10 + num_annotators * 0.5))
        img_height = min(12, max(8, 7 + num_annotators * 0.3))
        img = Image(img_buffer, width=img_width*cm, height=img_height*cm)
        elements.append(img)
        elements.append(Spacer(1, 0.5*cm))
        
        # 添加说明文字
        elements.append(Paragraph(
            "注：与上方「标注员完成情况」的区别是，此处统计包含所有任务状态，而「标注员完成情况」只统计已完成的任务。",
            self.styles['ChineseBody']
        ))
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _create_task_list(self, task_list: List[Dict[str, Any]]) -> List:
        """创建任务列表"""
        elements = []
        
        elements.append(Paragraph("六、任务列表", self.styles['ChineseHeading1']))
        elements.append(Paragraph(
            f"本节列出项目的所有任务详情，包括任务名称、状态、负责人、优先级和创建时间。共 {len(task_list)} 个任务。",
            self.styles['ChineseBody']
        ))
        elements.append(Spacer(1, 0.2*cm))
        
        if not task_list:
            elements.append(Paragraph("暂无任务", self.styles['ChineseBody']))
            return elements
        
        # 状态和优先级映射
        status_map = {
            'pending': '待分配',
            'in_progress': '进行中',
            'submitted': '已提交',
            'approved': '已完成',
            'rejected': '已驳回',
            'skipped': '已跳过'
        }
        
        priority_map = {'low': '低', 'medium': '中', 'high': '高', 'urgent': '紧急'}
        
        # 创建任务表格 - 显示所有任务，分页处理
        # 如果任务太多，分成多个表格以避免单页内容过多
        tasks_per_page = 50  # 每页显示50个任务
        
        for page_start in range(0, len(task_list), tasks_per_page):
            page_end = min(page_start + tasks_per_page, len(task_list))
            page_tasks = task_list[page_start:page_end]
            
            # 如果不是第一页，添加分页标题
            if page_start > 0:
                elements.append(PageBreak())
                elements.append(Paragraph(
                    f"任务列表（续）- 第 {page_start + 1} 至 {page_end} 个任务",
                    self.styles['ChineseHeading1']
                ))
                elements.append(Spacer(1, 0.3*cm))
            
            table_data = [['序号', '任务名称', '状态', '标注员', '优先级', '创建时间']]
            
            for idx, task in enumerate(page_tasks, start=page_start + 1):
                table_data.append([
                    str(idx),
                    task.get('title', '-')[:25],  # 限制长度避免表格过宽
                    status_map.get(task.get('status', ''), task.get('status', '-')),
                    task.get('assigned_to_name', '-')[:12],
                    priority_map.get(task.get('priority', ''), task.get('priority', '-')),
                    task.get('created_at', '-')[:10] if task.get('created_at') else '-'
                ])
            
            table = Table(table_data, colWidths=[1.5*cm, 4.5*cm, 2*cm, 2.5*cm, 1.8*cm, 3*cm])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), FONT_NAME_SONG),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # 序号居中
                ('ALIGN', (2, 1), (-1, -1), 'CENTER'),  # 状态、标注员、优先级、时间居中
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 4),
                # 交替行背景色
                *[('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f9f9f9')) 
                  for i in range(2, len(table_data), 2)]
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _create_article_stats(self, article_chart_data: List[Dict[str, Any]], article_stats: List[Dict[str, Any]]) -> List:
        """创建文章统计章节"""
        elements = []
        
        elements.append(Paragraph("七、项目文章统计", self.styles['ChineseHeading1']))
        elements.append(Paragraph(
            f"本节统计隶属于当前项目的文章，按类型分组展示。共 {sum([item['count'] for item in article_chart_data])} 篇文章。",
            self.styles['ChineseBody']
        ))
        elements.append(Spacer(1, 0.2*cm))
        
        if not article_chart_data:
            elements.append(Paragraph("暂无文章数据", self.styles['ChineseBody']))
            return elements
        
        # 生成柱状图
        fig, ax = plt.subplots(figsize=(12, 6))
        
        types = [item['type'] for item in article_chart_data]
        counts = [item['count'] for item in article_chart_data]
        
        x = range(len(types))
        bars = ax.bar(x, counts, width=0.6, color='#3b82f6', alpha=0.8)
        
        # 在柱子上显示数值
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax.set_xlabel('文章类型', fontsize=12)
        ax.set_ylabel('文章数量', fontsize=12)
        ax.set_title('文章类型分布', fontsize=14, pad=15, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(types, fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        # 设置y轴从0开始
        ax.set_ylim(bottom=0)
        
        plt.tight_layout()
        
        # 保存图表到内存
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)
        
        # 添加图表到PDF
        img = Image(img_buffer, width=16*cm, height=8*cm)
        elements.append(img)
        elements.append(Spacer(1, 0.5*cm))
        
        # 为每种类型创建详细表格
        for stat in article_stats:
            if stat['count'] == 0:
                continue
            
            elements.append(Paragraph(
                f"{stat['type']}（{stat['count']} 篇）",
                self.styles['ChineseHeading2']
            ))
            elements.append(Spacer(1, 0.2*cm))
            
            # 创建文章列表表格
            table_data = [['序号', '文章标题', '作者', '状态', '创建时间']]
            
            for idx, article in enumerate(stat['articles'][:20], start=1):  # 每种类型最多显示20篇
                table_data.append([
                    str(idx),
                    article.get('title', '-')[:30],  # 限制标题长度
                    article.get('author', '-')[:15],
                    article.get('status', '-'),
                    article.get('created_at', '-')[:10] if article.get('created_at') else '-'
                ])
            
            table = Table(table_data, colWidths=[1.5*cm, 6*cm, 3*cm, 2*cm, 3*cm])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), FONT_NAME_SONG),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # 序号居中
                ('ALIGN', (3, 1), (-1, -1), 'CENTER'),  # 状态、时间居中
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 6),
                # 交替行背景色
                *[('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f9f9f9')) 
                  for i in range(2, len(table_data), 2)]
            ]))
            
            elements.append(table)
            
            # 如果文章超过20篇，添加提示
            if len(stat['articles']) > 20:
                elements.append(Spacer(1, 0.2*cm))
                elements.append(Paragraph(
                    f"注：该类型共有 {len(stat['articles'])} 篇文章，此处仅显示前 20 篇。",
                    self.styles['ChineseBody']
                ))
            
            elements.append(Spacer(1, 0.3*cm))
        
        return elements


# 创建全局服务实例
pdf_service = PersonalPerformancePDFService()
team_pdf_service = TeamPerformancePDFService()
project_pdf_service = ProjectReportPDFService()


class WorkLogWeekPDFService:
    """工作周统计报告PDF导出服务"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """设置自定义样式"""
        # 标题样式
        self.styles.add(ParagraphStyle(
            name='ChineseTitle',
            parent=self.styles['Title'],
            fontName=FONT_NAME,
            fontSize=24,
            textColor=colors.HexColor('#1a73e8'),
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        # 副标题样式
        self.styles.add(ParagraphStyle(
            name='ChineseHeading1',
            parent=self.styles['Heading1'],
            fontName=FONT_NAME,
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # 正文样式
        self.styles.add(ParagraphStyle(
            name='ChineseBody',
            parent=self.styles['Normal'],
            fontName=FONT_NAME_SONG,
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            alignment=TA_LEFT
        ))
        
        # 表格标题样式
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontName=FONT_NAME,
            fontSize=10,
            textColor=colors.white,
            alignment=TA_CENTER
        ))
    
    def generate_work_week_report(
        self,
        work_week_info: Dict[str, Any],
        overall_stats: Dict[str, Any],
        user_summaries: List[Dict[str, Any]],
        work_type_stats: Dict[str, Any]
    ) -> BytesIO:
        """
        生成工作周统计报告PDF
        
        Args:
            work_week_info: 工作周信息 {title, week_start_date, week_end_date, status, year, week_number}
            overall_stats: 整体统计 {total_users, total_planned_hours, total_actual_hours, efficiency}
            user_summaries: 用户统计列表 [{user_name, total_actual_hours, work_type_hours, entries_count}, ...]
            work_type_stats: 工作类型统计 {work_type: total_hours, ...}
        """
        buffer = BytesIO()
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # 构建PDF内容
        story = []
        
        # 1. 报告标题
        story.extend(self._create_title(work_week_info))
        
        # 2. 工作周信息
        story.extend(self._create_week_info(work_week_info))
        
        # 3. 整体统计概览
        story.extend(self._create_overall_stats(overall_stats))
        
        # 4. 工作类型分布图
        story.extend(self._create_work_type_chart(work_type_stats))
        
        # 5. 计划工时 vs 实际工时对比图
        story.extend(self._create_hours_compare_chart(user_summaries))
        
        # 6. 用户详细统计表格
        story.extend(self._create_user_detail_table(user_summaries))
        
        # 7. 页脚
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(
            f"报告生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}",
            self.styles['ChineseBody']
        ))
        
        # 生成PDF
        doc.build(story)
        buffer.seek(0)
        
        logger.info(f"✅ [PDFExport] 工作周统计报告生成成功: {work_week_info.get('title', 'Unknown')}")
        return buffer
    
    def _create_title(self, work_week_info: Dict[str, Any]) -> List:
        """创建报告标题"""
        elements = []
        
        title = work_week_info.get('title', '工作周统计报告')
        elements.append(Paragraph(title, self.styles['ChineseTitle']))
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _create_week_info(self, work_week_info: Dict[str, Any]) -> List:
        """创建工作周信息"""
        elements = []
        
        elements.append(Paragraph("工作周信息", self.styles['ChineseHeading1']))
        
        # 创建信息表格
        info_data = [
            ['工作周期', f"{work_week_info.get('week_start_date', '')} 至 {work_week_info.get('week_end_date', '')}"],
            ['年度/周数', f"{work_week_info.get('year', '')}年 第{work_week_info.get('week_number', '')}周"],
            ['状态', work_week_info.get('status_text', '进行中')],
        ]
        
        table = Table(info_data, colWidths=[4*cm, 12*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.8*cm))
        
        return elements
    
    def _create_overall_stats(self, overall_stats: Dict[str, Any]) -> List:
        """创建整体统计概览"""
        elements = []
        
        elements.append(Paragraph("整体工时统计", self.styles['ChineseHeading1']))
        
        # 创建统计卡片
        stats_data = [
            ['参与人数', f"{overall_stats.get('total_users', 0)} 人"],
            ['计划工时', f"{overall_stats.get('total_planned_hours', 0)} 小时"],
            ['实际工时', f"{overall_stats.get('total_actual_hours', 0)} 小时"],
            ['工时完成率', f"{overall_stats.get('efficiency', 0)}%"],
        ]
        
        table = Table(stats_data, colWidths=[8*cm, 8*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.8*cm))
        
        return elements
    
    def _create_work_type_chart(self, work_type_stats: Dict[str, Any]) -> List:
        """创建工作类型分布饼图"""
        elements = []
        
        if not work_type_stats:
            return elements
        
        elements.append(Paragraph("工作类型分布", self.styles['ChineseHeading1']))
        
        # 创建饼图
        fig, ax = plt.subplots(figsize=(8, 6))
        
        labels = list(work_type_stats.keys())
        sizes = list(work_type_stats.values())
        
        # 定义颜色
        colors_list = ['#409eff', '#67c23a', '#17a2b8', '#ff9800', '#9c27b0', 
                       '#f56c6c', '#909399', '#e6a23c', '#f59e0b', '#ef4444']
        
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, 
               colors=colors_list[:len(labels)])
        ax.axis('equal')
        plt.title('工作类型工时分布', fontsize=14, pad=20)
        
        # 保存图表为图片
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        img_buffer.seek(0)
        
        # 添加图片到PDF
        img = Image(img_buffer, width=14*cm, height=10*cm)
        elements.append(img)
        elements.append(Spacer(1, 0.8*cm))
        
        return elements
    
    def _create_hours_compare_chart(self, user_summaries: List[Dict[str, Any]]) -> List:
        """创建计划工时 vs 实际工时对比柱状图"""
        elements = []
        
        if not user_summaries:
            return elements
        
        elements.append(Paragraph("计划工时 vs 实际工时对比", self.styles['ChineseHeading1']))
        
        # 准备数据
        user_names = [user['user_name'] for user in user_summaries]
        planned_hours = [40] * len(user_summaries)  # 固定40小时
        actual_hours = [user['total_actual_hours'] for user in user_summaries]
        
        # 创建柱状图
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = range(len(user_names))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], planned_hours, width, label='计划工时', color='#409eff')
        ax.bar([i + width/2 for i in x], actual_hours, width, label='实际工时', color='#67c23a')
        
        ax.set_xlabel('员工', fontsize=12)
        ax.set_ylabel('工时（小时）', fontsize=12)
        ax.set_title('计划工时 vs 实际工时对比', fontsize=14, pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(user_names, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # 保存图表为图片
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        img_buffer.seek(0)
        
        # 添加图片到PDF（分页显示）
        elements.append(PageBreak())
        img = Image(img_buffer, width=16*cm, height=10*cm)
        elements.append(img)
        elements.append(Spacer(1, 0.8*cm))
        
        return elements
    
    def _create_user_detail_table(self, user_summaries: List[Dict[str, Any]]) -> List:
        """创建用户详细统计表格"""
        elements = []
        
        if not user_summaries:
            return elements
        
        elements.append(Paragraph("用户详细统计", self.styles['ChineseHeading1']))
        
        # 构建表格数据
        table_data = [
            [
                Paragraph('<b>姓名</b>', self.styles['TableHeader']),
                Paragraph('<b>计划工时</b>', self.styles['TableHeader']),
                Paragraph('<b>实际工时</b>', self.styles['TableHeader']),
                Paragraph('<b>完成率</b>', self.styles['TableHeader']),
                Paragraph('<b>工作类型分布</b>', self.styles['TableHeader']),
                Paragraph('<b>日志条目数</b>', self.styles['TableHeader'])
            ]
        ]
        
        for user in user_summaries:
            # 计算完成率
            actual = user['total_actual_hours']
            efficiency = round((actual / 40) * 100, 1) if actual > 0 else 0
            
            # 工作类型分布
            work_type_hours = user.get('work_type_hours', {})
            work_type_str = ', '.join([f"{wt}: {h}h" for wt, h in work_type_hours.items() if h > 0])
            if not work_type_str:
                work_type_str = '-'
            
            row = [
                Paragraph(user['user_name'], self.styles['ChineseBody']),
                Paragraph('40h', self.styles['ChineseBody']),
                Paragraph(f"{actual}h", self.styles['ChineseBody']),
                Paragraph(f"{efficiency}%", self.styles['ChineseBody']),
                Paragraph(work_type_str, self.styles['ChineseBody']),
                Paragraph(str(user.get('entries_count', 0)), self.styles['ChineseBody'])
            ]
            table_data.append(row)
        
        # 创建表格
        table = Table(table_data, colWidths=[3*cm, 2.5*cm, 2.5*cm, 2.5*cm, 5*cm, 2*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (3, -1), 'CENTER'),
            ('ALIGN', (5, 1), (5, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
            # 交替行背景色
            *[('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f9f9f9')) 
              for i in range(2, len(table_data), 2)]
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5*cm))
        
        return elements


# 创建工作日志导出服务实例
work_log_pdf_service = WorkLogWeekPDFService()

