---
name: reorder-model
description: >
  智能补货决策模型手册。基于库存预警快照（replenish_stock_snapshot）计算
  再订货点（ROP）、安全库存缺口、建议补货量、ABC 分类与优先级排序，
  并生成补货建议报告与待审批的补货清单。当需要"补货建议"、"缺货分析"、
  "该订多少"、"库存补充计划"、"再订货点"时加载此技能。
---

# 智能补货决策模型（操作手册）

你负责把库存预警数据转化为可执行的补货建议。核心链路：
**取数（MCP 聚合工具）→ 计算（本技能脚本）→ 报告（图表）→ 提交（人工审批）**。

## 适用场景
- "哪些物料需要补货、各补多少" —— 全量快照分析
- "刹车片还能撑几天、什么时候下单" —— 单物料深挖（配合 replenish_part_history）
- "本季度补货预算要多少" —— 建议清单金额汇总

## 工作流程（5 步）

### 第 1 步：获取分析原料
调用 `replenish_stock_snapshot`（无参数）。返回库存预警 × 近 12 个月采购历史的
聚合快照，每行含：currentQuantity / safetyStock / monthlyConsumption /
avgUnitPrice12m / purchasePrice / supplierId 等字段。

### 第 2 步：保存快照到沙箱
把上一步的 JSON 数组保存为文件（供脚本读取，避免超长参数）：
```
write_file("/analysis/temp/replenish_input.json", <JSON字符串>)
```

### 第 3 步：运行补货模型
```
execute("python /skills/replenish/reorder-model/reorder_calc.py --input /analysis/temp/replenish_input.json --output /analysis/temp/replenish_result.json")
```
脚本计算以下指标（公式见脚本内注释，此处为速查）：

| 指标 | 公式 | 说明 |
|------|------|------|
| 再订货点 ROP | 月消耗 × (提前期/30) + 安全库存 | 提前期默认 14 天 |
| 缺口 gap | max(0, ROP − 当前库存) | 低于 ROP 即需补货 |
| 建议量 suggest | max(gap, 安全库存 − 当前库存) 向上取整 | 兜底不低于安全线 |
| 紧急度 urgency | 缺货天数 = (当前库存 / 月消耗) × 30 | ≤7 天为 critical |
| ABC 类 | 年采购金额帕累托累计 80%/95% 分界 | A 类重点管控 |
| 优先级 | critical(4) > high(3) > medium(2) > low(1) | 按 ABC 与缺货天数联合定级 |

### 第 4 步：生成报告与图表
1. `read_file("/analysis/temp/replenish_result.json")` 读取计算结果
2. 首次调用图表前 `read_file("/skills/procurement/chart_params.md")` 获取图表参数速查
3. 建议图表组合：
   - 补货量 TOP10 物料 → `generate_visualization(chart_type="bar", ...)`
   - 各类别补货金额占比 → `generate_visualization(chart_type="pie", ...)`
   - ABC 分类物料数 → `generate_visualization(chart_type="column", ...)`
4. 报告写入 `/analysis/report_replenish_{时间戳}.md`

### 第 5 步：提交补货清单（人工审批）
把**建议补货的物料清单**（建议量 > 0 的行）整理为 list 传给：
```
replenish_submit(replenishment_plan=[{partId, partName, suggestQuantity, unitPrice, estimatedAmount, supplierId, urgency, abcClass, reason}, ...], remark="...")
```
**注意**：该工具执行前会触发**人工审批中断**——任务暂停，等待用户在对话中
回复批准（approve）或拒绝（reject）。批准后清单才写入沙箱存档；拒绝则不写入。

## 脚本执行失败时的处理协议（按序尝试，最多 3 轮）

execute 运行脚本（含 reorder_calc.py 及自写分析脚本）报错时，**不要**盲目重试或直接放弃，
按以下协议循环修复（此路径已在真实轨迹中验证可行，照走即可）：

1. 读完整 traceback，先分类再动手：
   - `ModuleNotFoundError` → 优先确认是常用数据分析包（pandas/numpy/matplotlib 等）
     → `pip install 包名` 后**原样重跑**（沙箱缺 pandas 时即此路）。
     **安全约束**：白名单外的包会被安全策略拦截（返回"供应链防线"错误）——
     **重试无效，也不要换渠道绕过**；如实向用户报告所需包名与用途，
     由用户决定是否扩充白名单
   - `SyntaxError` / `NameError` → `read_file` 定位出错代码行，修复后重跑
   - `KeyError` / 数据为空 → 是**上游查询问题**（参数错/数据没取到），回第 1 步重新取数，
     **不要**改脚本硬编数据糊弄过去
   - `File already exists`（写输出文件被占）→ 先确认旧文件可删再 `rm`，重跑
2. 同一类错误连续 2 次未解决 → 停止重试，**如实报告失败原因与已尝试的内容**，
   让用户决定下一步（失败也是合法终态，不是必须硬撑到成功）
3. 每轮重试前用一句话记录"本轮假设 → 验证结果"（自我观察，防止原地空转烧 token）

## 报告模板

```markdown
# 智能补货建议报告
## 1. 总览（预警物料数、需补货物料数、建议总额）
## 2. 紧急补货清单（critical/high，表格：物料/缺口/建议量/预计金额）
## 3. 常规补货清单（medium/low）
## 4. ABC 分类洞察（A 类物料的库存策略建议）
## 5. 结论与建议（3-5 条）
```

## 返回主 Agent 格式

```
【报告路径】/analysis/report_replenish_xxx.md
【摘要】（300 字内：预警 N 项、需补货 M 项、建议总额 ¥X）
【紧急项】critical 清单一行摘要
【审批状态】补货清单已提交人工审批 / 已批准并存档 / 已拒绝
```

## 关键原则
- **数据真实**：所有结论基于 snapshot 真实数据，绝不编造
- **模型一致**：计算一律走 reorder_calc.py，不在回复里手算替代
- **审批前置**：replenish_submit 必须在报告生成后调用，且接受中断等待
- **按需深挖**：用户关注单一物料时用 replenish_part_history 补充节奏分析
