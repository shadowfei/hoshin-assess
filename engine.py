from questions_data import DIM_NAMES

DIMENSION_MAP = {
    1: (1, 8, "战略预备度与外部环境"),
    2: (9, 15, "领导力与组织文化"),
    3: (16, 23, "流程管理与改善能力"),
    4: (24, 30, "执行、对齐与数字化基础"),
}

SCORE_LABELS = {
    1: {"label": "初始级", "desc": "完全缺失或无序（Ad-hoc）"},
    3: {"label": "规划级", "desc": "有初步意识或尝试，缺乏系统性"},
    6: {"label": "规范级", "desc": "已系统化实施，形成流程标准"},
    9: {"label": "优化级", "desc": "标准化闭环，融入文化持续改善"},
}

QUADRANT_ADVICE = {
    "A": {"label": "A象限（有渴望，无能力）", "advice": "创始人有雄心但缺乏组织流程。建议先建立沟通平台，统一管理层对如何共同管理组织的共识，避免专家文化导致的短期行为。从极小、能快速见效的低垂果实开始。", "focus": "建机制、立规矩、拿快赢"},
    "B": {"label": "B象限（无渴望，无能力）", "advice": "处于生存模式，依赖老板个人能力。建议从极小的、能快速见效的挑战开始，通过成功来激发改变的愿望。不要急于导入复杂体系。", "focus": "找亮点、树信心、活下来"},
    "C": {"label": "C象限（有渴望，有能力）", "advice": "最理想的实施对象。建议直接导入完整的年度方针管理循环（Annual Cycle），包括 X-Matrix、Catchball、月度评审等完整体系。", "focus": "全面推进、系统导入、持续优化"},
    "D": {"label": "D象限（无渴望，有能力）", "advice": "流程高效但缺乏战略眼光。建议引入战略扫描工具（如Porter矩阵），帮助管理层抬头看天，识别外部风险和机遇。", "focus": "看外部、找方向、定战略"},
}

ALL_QUADRANTS = [
    {"key": "D", "label": "D 有能无力", "cn": "流程高效但缺方向", "en": "Efficient but Visionless", "style": "info"},
    {"key": "C", "label": "C 有能有愿", "cn": "理想导入对象", "en": "Ideal Candidate", "style": "success"},
    {"key": "A", "label": "A 有愿无能", "cn": "有雄心缺流程", "en": "Eager but Weak", "style": "danger"},
    {"key": "B", "label": "B 无愿无能", "cn": "生存模式", "en": "Survival Mode", "style": "warning"},
]


class AssessmentEngine:
    @staticmethod
    def calculate(items):
        if not items:
            return {}
        scores = {i: {} for i in range(1, 5)}
        for item in items:
            scores[item.dimension][item.question_no] = item.score
        dim_avgs = {}
        for dim, (start, end, name) in DIMENSION_MAP.items():
            dim_scores_list = [scores[dim].get(q, 0) for q in range(start, end + 1)]
            valid = [s for s in dim_scores_list if s > 0]
            dim_avgs[dim] = round(sum(valid) / len(valid), 1) if valid else 0
        desire_qs = list(range(1, 5)) + list(range(9, 13))
        capacity_qs = list(range(5, 9)) + list(range(13, 31))
        desire_scores = [item.score for item in items if item.question_no in desire_qs and item.score > 0]
        capacity_scores = [item.score for item in items if item.question_no in capacity_qs and item.score > 0]
        desire_avg = round(sum(desire_scores) / len(desire_scores), 1) if desire_scores else 0
        capacity_avg = round(sum(capacity_scores) / len(capacity_scores), 1) if capacity_scores else 0
        if desire_avg >= 4.5 and capacity_avg < 4.5:
            qk = "A"
        elif desire_avg < 4.5 and capacity_avg < 4.5:
            qk = "B"
        elif desire_avg >= 4.5 and capacity_avg >= 4.5:
            qk = "C"
        else:
            qk = "D"
        qi = QUADRANT_ADVICE[qk]

        # 渴望度/能力值诊断一句话
        if desire_avg >= 6:
            desire_diagnosis = "企业有强烈的变革意愿和清晰的方向感"
        elif desire_avg >= 3:
            desire_diagnosis = "企业有改善意愿但尚未形成统一共识"
        else:
            desire_diagnosis = "企业当前缺乏变革动力，需要外部刺激唤醒意识"

        if capacity_avg >= 6:
            capacity_diagnosis = "组织已具备支撑战略落地的体系化能力"
        elif capacity_avg >= 3:
            capacity_diagnosis = "组织有一定基础但系统性和执行力度有待加强"
        else:
            capacity_diagnosis = "组织能力薄弱，需要从基础管理开始夯实内功"

        # 优势：按梯队
        score_9 = [{"no": i.question_no, "text": i.question_text, "score": i.score, "dim": i.dimension} for i in items if i.score == 9]
        score_6 = [{"no": i.question_no, "text": i.question_text, "score": i.score, "dim": i.dimension} for i in items if i.score == 6]
        # 劣势：按梯队
        score_1 = [{"no": i.question_no, "text": i.question_text, "score": i.score, "dim": i.dimension} for i in items if i.score == 1]
        score_3 = [{"no": i.question_no, "text": i.question_text, "score": i.score, "dim": i.dimension} for i in items if i.score == 3]

        # 各维度分析
        dim_analysis = {}
        for dim, (start, end, name) in DIMENSION_MAP.items():
            avg = dim_avgs[dim]
            cn_name, en_name = DIM_NAMES.get(dim, (name, ""))
            if avg >= 6:
                comment = f"{cn_name}方面基础扎实，建议在保持优势的同时向更高标准看齐"
                level = "strong"
            elif avg >= 3:
                comment = f"{cn_name}方面已有一定基础，建议聚焦薄弱环节重点突破"
                level = "medium"
            else:
                comment = f"{cn_name}方面是当前主要短板，建议作为方针导入的首批改善对象"
                level = "weak"
            # 维度内优势：优先9分，无则取6分（最多3条）
            dim_items = [i for i in items if i.dimension == dim]
            dim_strong = sorted([i for i in dim_items if i.score == 9], key=lambda x: x.question_no)
            if not dim_strong:
                dim_strong = sorted([i for i in dim_items if i.score == 6], key=lambda x: x.question_no)[:3]
            # 维度内劣势：优先1分，无则取3分（最多3条）
            dim_weak = sorted([i for i in dim_items if i.score == 1], key=lambda x: x.question_no)
            if not dim_weak:
                dim_weak = sorted([i for i in dim_items if i.score == 3], key=lambda x: x.question_no)[:3]

            dim_analysis[dim] = {
                "cn": cn_name, "en": en_name, "avg": avg, "level": level, "comment": comment,
                "strong": [{"no": i.question_no, "text": i.question_text, "score": i.score} for i in dim_strong],
                "weak": [{"no": i.question_no, "text": i.question_text, "score": i.score} for i in dim_weak],
            }

        warnings = []
        for dim, (start, end, name) in DIMENSION_MAP.items():
            vals = [scores[dim].get(q, 0) for q in range(start, end + 1)]
            valid = [s for s in vals if s > 0]
            if valid and (max(valid) - min(valid) > 3):
                cn_name = DIM_NAMES.get(dim, (name, ""))[0]
                warnings.append(f"「{cn_name}」维度内分差较大，可能存在内部对齐问题")
        overall = round((desire_avg + capacity_avg) / 2, 1)

        # ========== 总结板块 ==========
        # 总体水平
        if overall >= 7:
            overall_level = "先进水平 (Advanced)"
            overall_summary = "企业在方针管理的多个维度已具备较成熟的体系化能力，战略对齐与执行力良好。"
        elif overall >= 4.5:
            overall_level = "发展中水平 (Developing)"
            overall_summary = "企业已有一定基础，部分维度表现良好，但在系统性和全组织对齐方面仍有提升空间。"
        else:
            overall_level = "初级阶段 (Initial)"
            overall_summary = "企业方针管理体系建设尚处早期，建议从基础管理工作入手，逐步建立标准化、可视化和目标对齐机制。"

        # 推荐路线周期：短期版（6-12月）+ 长期版（3-5年）
        weak_dims = sorted([(dim_avgs[d], d) for d in dim_avgs if dim_avgs[d] <= 3])
        strong_dims = sorted([(dim_avgs[d], d) for d in dim_avgs if dim_avgs[d] >= 6])

        if qk == "C":
            short_term = [
                {"phase": "第1-3月", "title": "体系导入", "action": "建立X-Matrix战略矩阵与年度方针循环"},
                {"phase": "第3-6月", "title": "目标对齐", "action": "实施Catchball双向协商，对齐各层级目标"},
                {"phase": "第6-12月", "title": "月度评审", "action": "建立月度方针评审机制，A3驱动问题解决"},
            ]
            long_term = [
                {"phase": "第1年", "title": "夯实体系", "action": "完整运行一轮方针管理年度循环，培养PDCA文化"},
                {"phase": "第2-3年", "title": "深化融合", "action": "将方针管理融入日常管理，建立战略与执行的无缝衔接"},
                {"phase": "第3-5年", "title": "自主进化", "action": "组织具备自我诊断与持续进化能力，形成学习型组织"},
            ]
        elif qk == "A":
            short_term = [
                {"phase": "第1-2月", "title": "统一共识", "action": "建立管理团队定期沟通平台，对齐管理语言"},
                {"phase": "第2-4月", "title": "速赢试点", "action": "选择1-2个跨职能挑战，3个月内拿到可见成果"},
                {"phase": "第4-12月", "title": "建机制", "action": "导入标准化作业、可视化管理、每日晨会等基础工具"},
            ]
            long_term = [
                {"phase": "第1年", "title": "打地基", "action": "建立基础管理秩序，培养改善习惯和问题解决能力"},
                {"phase": "第2-3年", "title": "系统导入", "action": "在基础管理成型后，逐步导入方针管理完整循环"},
                {"phase": "第3-5年", "title": "文化沉淀", "action": "从工具驱动转向文化驱动，全员具备持续改善意识"},
            ]
        elif qk == "B":
            short_term = [
                {"phase": "第1月", "title": "生存优先", "action": "聚焦最紧迫的业务痛点，用精益工具快速改善"},
                {"phase": "第2-4月", "title": "建立信心", "action": "选1个小范围改进，用数据证明改善效果"},
                {"phase": "第5-12月", "title": "培养能力", "action": "通过TWI培训培养一线管理者的改善能力"},
            ]
            long_term = [
                {"phase": "第1年", "title": "活下来", "action": "稳定运营，建立基本的管理秩序和改善信心"},
                {"phase": "第2-3年", "title": "站起来", "action": "从生存模式转向发展模式，建立标准化管理基础"},
                {"phase": "第3-5年", "title": "跑起来", "action": "导入策略规划意识，逐步迈向方针管理"},
            ]
        else:  # D
            short_term = [
                {"phase": "第1-2月", "title": "战略扫描", "action": "引入Porter五力等工具，识别外部风险与机遇"},
                {"phase": "第3-5月", "title": "愿景共识", "action": "组织战略研讨会，重新梳理使命与突破性目标"},
                {"phase": "第6-12月", "title": "策略部署", "action": "将新战略分解到各执行层级，建立评审机制"},
            ]
            long_term = [
                {"phase": "第1年", "title": "定方向", "action": "建立清晰的战略规划流程和年度目标分解机制"},
                {"phase": "第2-3年", "title": "建体系", "action": "将战略管理与日常运营深度整合，建立持续改进文化"},
                {"phase": "第3-5年", "title": "扩影响", "action": "战略执行力成为组织核心竞争力，驱动行业影响力提升"},
            ]

        summary = {
            "overall_level": overall_level,
            "overall_summary": overall_summary,
            "short_term_roadmap": short_term,
            "long_term_roadmap": long_term,
            "weak_dim_count": len(weak_dims),
            "strong_dim_count": len(strong_dims),
        }

        return {
            "dim_avgs": dim_avgs,
            "dim_analysis": dim_analysis,
            "desire_score": desire_avg,
            "desire_diagnosis": desire_diagnosis,
            "capacity_score": capacity_avg,
            "capacity_diagnosis": capacity_diagnosis,
            "quadrant_key": qk,
            "quadrant_label": qi["label"],
            "quadrant_advice": qi["advice"],
            "quadrant_focus": qi["focus"],
            "overall_score": overall,
            "score_9_items": score_9,
            "score_6_items": score_6,
            "score_1_items": score_1,
            "score_3_items": score_3,
            "alignment_warnings": warnings,
            "summary": summary,
        }
