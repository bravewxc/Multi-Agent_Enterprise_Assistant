# Multi-Agent Enterprise Procurement Assistant

基于 [LangGraph](https://github.com/langchain-ai/langgraph) / [deepagents](https://github.com/langchain-ai/deepagents) 构建的多智能体企业采购助手：主 Agent 负责对话与任务编排，将耗时分析委派给后台异步子 Agent，通过 MCP 调用汽车配件 ERP 的查询与订单工具，在 OpenSandbox 沙箱中执行分析脚本，并在关键操作前强制人工审批（HITL）。

项目实现了完整的 **Agent 循环工程（Loop Engineering）** 与**纵深防御安全体系**：LLM-as-Judge 运行时质量评审、Reflexion 重写循环、审批协商循环、错误分类重试协议、间接注入扫描、供应链包白名单、记忆写入双信任校验等。

## 功能特性

- **多智能体协作**：主 Agent + 采购分析 / 智能补货两个后台异步子 Agent（Agent Protocol 独立进程）+ 订单同步子 Agent，任务级工具前缀隔离（最小权限）
- **人工在环审批（HITL）**：补货清单提交（replenish_submit）与订单创建/修改（order_create / order_update）执行前均强制中断等待 approve/reject；拒绝理由可透传给模型驱动清单修订协商（最多 3 轮），审批参数有指纹回归锁
- **运行时质量评审 + Reflexion 重写**：审批通过的清单经确定性算术校验 + 异构 LLM 语义评分（1/4/7/10 锚点 rubric）双层评审，不达标批评意见回流驱动模型修订重报（最多 2 轮），分数落库可回放
- **沙箱代码执行**：补货决策模型（ROP/安全库存/ABC 分类）在 OpenSandbox 沙箱内运行，脚本失败有结构化修复协议
- **长期记忆**：从对话中抽取用户偏好（供应商/查询历史），写入前做双信任级校验（防幻觉实体、防外部内容投毒）
- **错误分类重试协议**：工具错误自动分类 transient/permanent 并附带可执行修正指引与重试预算，替代裸错误字符串
- **安全纵深防御**：外部检索结果结构化包裹 + 注入特征扫描、pip 包白名单（供应链防线）、凭据双通道脱敏、三重资源预算（模型/工具调用/单工具重试上限）
- **可观测性**：每次工具调用的成败/耗时/错误按 thread_id 落 MongoDB（2,300+ 条遥测），评估体系含黄金集回归与基线门控（baselines.json）

## 系统架构

```
+--------------+     +----------------------------------------------+
|   Vue 前端   |     |        FastAPI 后端 (api_view, :8090)        |
|   (:3000)    | SSE |    会话管理 / 异步任务状态 / 审批中断检测    |
+--------------+     |         SSE 流式输出 / 审批中断透出          |
                ---->|                                              |
                     +-----------------------+----------------------+
                                             |  langgraph_sdk
                                             v
+------------------------------------------------------------------------------------------+
|                                  主 Agent (deepagents)                                   |
|                            路由 / 委派 / 工具编排 / 长期记忆                             |
|        中间件链: 指标>重试指引>异常转换>图片防护>沙箱健康>记忆更新>质量评审>脱敏         |
+------------+-------------------------------+-------------------------------+-------------+
             |  Agent Protocol :2024         |                               | task 工具
             v                               v                               v
+--------------------------+    +--------------------------+    +--------------------------+
|  异步子Agent · 采购分析  |    |  异步子Agent · 智能补货  |    |  同步子Agent · 采购订单  |
|   Agent Protocol :2024   |    |   Agent Protocol :2024   |    |  task 工具(主图内同步)   |
|   供应商比价/行情报告    |    |     ROP/ABC/补货建议     |    |    订单创建/修改/查询    |
|   后台异步,不阻塞对话    |    |  HITL: replenish_submit  |    |      HITL: 订单审批      |
+------------+-------------+    +------------+-------------+    +------------+-------------+
             |  MCP 调用(前缀过滤)                 |                               |
+------------------------------------------------------------------------------------------+
|                            ERP MCP Server (mcp_server, :8000)                            |
|                   supplier_/part_/inventory_/order_/replenish_ 工具族                    |
+--------------------------------------------+---------------------------------------------+
                                             |  HTTP
                                             v
                          +--------------------------------------+
                          | Java ERP 后端 (本仓库外, 需自行部署) |
                          +--------------------------------------+

配套基础设施: MongoDB(:27017) 持久化 | OpenSandbox(:8080) 沙箱执行 | 图表MCP(:1122) AntV
```

## 技术栈

| 层 | 技术 |
|---|---|
| Agent 框架 | LangGraph · deepagents · langchain |
| 模型接入 | OpenAI 兼容协议（DeepSeek 官网 / 阿里百炼 DashScope，OpenAI / GLM / Qwen 多模型可切换） |
| 工具协议 | FastMCP（自建 ERP MCP Server）· MCP over streamable-http（图表服务） |
| 沙箱 | OpenSandbox（opensandbox-server） |
| 后端 | FastAPI · uvicorn · langgraph-sdk（异步子 Agent 通信） |
| 前端 | Vue 3 · Vite（SSE 流式响应） |
| 存储 | MongoDB（checkpoint / Store / 指标遥测） |
| 测试与评估 | pytest 风格自研回归套件（HITL 7 用例 / 记忆合并 / 路由黄金集 / Judge 评审） |

## 环境要求

- Python 3.12+（建议 venv 虚拟环境）
- Node.js 18+（前端构建 + AntV 图表 MCP）
- MongoDB 6.0+（Docker 部署即可）
- Windows / Linux / macOS（启动命令以 Windows PowerShell 为例，其他平台等价替换）
- 一个汽车配件 ERP 后端（Java，本仓库不包含；`motorparts_db.sql` 为其数据库结构与演示数据，需自行部署后端服务并保证 `/api` 接口可用）

## 快速开始

### 1. 克隆并安装依赖

```powershell
git clone <repo-url>
cd Multi-Agent-Enterprise-Procurement-Assistant

# Python 依赖
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -U "langgraph-cli[inmem]"   # 异步子 Agent 的 langgraph dev 运行器

# 前端依赖
cd frontend; npm install; cd ..
```

### 2. 配置环境变量

```powershell
copy .env.example .env
# 编辑 .env：填入你的模型 API Key、ERP 后端地址、MongoDB 连接串
```

### 3. 启动基础设施

```powershell
# MongoDB（Docker）
docker start procurement-mongo
# 首次部署：docker run -d --name procurement-mongo -p 27017:27017 \
#   -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=<your-password> mongo
```

### 4. 启动服务（两种方式任选）

**方式 A：一键启动（推荐）**

```powershell
# 按依赖顺序拉起 MCP → 沙箱预热 → 异步子 Agent(2024) → 后端(8090) → 前端(3000)
python start_web.py
```

**方式 B：手动分窗口启动**

MongoDB（步骤 3）保持运行，以下 6 个服务各占一个独立窗口（PowerShell），按顺序启动：

```powershell
# 1) OpenSandbox 沙箱服务端 (:8080)
$env:OPENSANDBOX_INSECURE_SERVER='YES'
& ".venv\Scripts\opensandbox-server.exe" --config .sandbox.toml

# 2) ERP MCP Server (:8000)
& ".venv\Scripts\python.exe" -m mcp_server.server_main

# 3) 图表 MCP (:1122)  —— npm 全局目录用 `npm root -g` 查询
node "$(npm root -g)/@antv/mcp-server-chart/build/index.js" --transport streamable --port 1122 --host 127.0.0.1

# 4) 异步子 Agent (Agent Protocol, :2024)
$env:PYTHONUTF8='1'
& ".venv\Scripts\langgraph.exe" dev --allow-blocking --no-browser --port 2024 --host 127.0.0.1

# 5) 后端 (:8090)
& ".venv\Scripts\python.exe" -m uvicorn api_view.web_main:app --host 127.0.0.1 --port 8090

# 6) 前端 (:3000)
cd frontend; npm run dev
```

### 5. 访问

浏览器打开 `http://localhost:3000`，开始对话。试试：

- "对比一下博世和电装的火花塞报价" → 触发采购分析异步任务
- "对刹车类预警物料给出补货建议" → 触发智能补货 → 分析完成后弹出**人工审批**，批准/拒绝（拒绝时说明理由，如"总额砍到 1 万以内"，Agent 会修订清单重新提交）

## 项目结构

```
├── src/
│   ├── agent/                  # Agent 核心
│   │   ├── main_agent.py       #   主 Agent（工具池/中间件栈/子 Agent 编排）
│   │   ├── async_procurement_analyst.py    # 采购分析异步子 Agent
│   │   ├── async_procurement_replenish.py  # 智能补货异步子 Agent（HITL 审批）
│   │   ├── middlewares/        #   中间件：指标采集/错误重试指引/异常转换/
│   │   │                       #   图片防护/沙箱健康/记忆更新/质量评审/脱敏
│   │   ├── tools/              #   web_search / resume_async_task / 图表 / 下载
│   │   ├── backends/           #   OpenSandbox 沙箱后端（含 pip 包白名单）
│   │   ├── skills/             #   技能文件（补货决策模型手册等）
│   │   ├── subagents/configs/  #   子 Agent 配置（提示词/interrupt_on）
│   │   └── memory/             #   AGENTS.md / 系统提示词
│   ├── mcp_server/             # ERP MCP Server（:8000）
│   ├── api_view/               # FastAPI 后端（:8090）
│   ├── eval/                   # 评估体系（黄金集/Judge/回归/基线）
│   └── test/                   # 回归测试（HITL 7 用例/记忆合并/路由）
├── frontend/                   # Vue 3 前端
├── motorparts_db.sql           # ERP 数据库结构与演示数据（Java 后端用）
├── .sandbox.toml               # OpenSandbox 沙箱配置
├── langgraph.json              # 异步子 Agent 图定义
├── start_web.py                # 一键启动器
└── .env.example                # 环境变量模板
```

## 测试与评估

```powershell
# HITL 审批链路回归（7 用例：必中断/摘要提取/审批存档/拒绝不存档/
# 决策白名单/重复审批拒绝/审批参数指纹——需全栈服务在线）
$env:PYTHONPATH='src'; .venv\Scripts\python.exe -m test.test_hitl_approval

# 记忆合并逻辑单测（离线，零 LLM 成本）
$env:PYTHONPATH='src'; .venv\Scripts\python.exe -m test.test_memory_merge unit

# 路由黄金集回归（多数票 + 基线门控，详见 src/eval/）
$env:PYTHONPATH='src'; .venv\Scripts\python.exe -m eval.regression
```

## 安全设计亮点

本项目按纵深防御框架组织 Agent 安全，值得关注的实现：

- **输入侧**：外部检索结果 `<external_data>` 结构化包裹 + 注入特征规则扫描（指令劫持/角色冒充/诱导外发三类）
- **执行侧**：HITL 审批（枚举决策白名单 + 参数指纹回归锁）、工具前缀级最小权限、沙箱 pip 包白名单（含 `-r` 文件型绕过拦截）、三重资源预算
- **记忆侧**：写入前双信任级校验——只有用户亲口提过的实体才进长期记忆
- **输出侧**：错误消息（给模型）与指标落库（持久化）双通道凭据脱敏

## License

本项目仅供学习与研究使用。商用请联系作者。
