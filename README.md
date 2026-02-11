# MT4 多开管理工具（MVP）

本项目提供一个可视化的 MT4 多开管理后台（FastAPI + SQLite），面向模拟盘测试场景。

## 已实现能力（对应需求）

1. **一键创建 MT4 实例**：`POST /api/instances`，从模板目录复制并自动创建隔离目录结构。
2. **实例自定义命名**：创建时命名 + `PATCH /api/instances/{id}/rename`。
3. **一键克隆实例**：`POST /api/instances/clone`，支持“仅保留有用指标和EA”。
4. **自动识别 Experts/Indicators 路径 & 分发按钮**：实例记录内保存路径，页面提供“分发EA/分发指标”按钮，API 支持全量/按组/按实例分发。
5. **符号链接统一主目录**：`POST /api/symlink`，将实例 Experts/Indicators 链接到主目录。
6. **实时状态显示**：`POST /api/report/status` 上报，首页展示 EA 状态、账户余额等。
7. **实例分组管理**：字段 `group_name` + 按组查询/分发/启动。
8. **批量启动**：`POST /api/launch?group_name=xxx` 或不传参数启动全部。
9. **备注栏本地/远程协作同步**：实例 notes 可编辑；保存时写入 `CloudSyncEvent`，供云端轮询同步。
10. **云服务器多端同步**：API 天然可部署在云端，多端通过 `/api/cloud/events` 拉取事件。
11. **回测报告与对比**：`POST /api/backtests` 上传，`GET /api/backtests/compare` 多实例结果对比。
12. **操作日志**：统一写入 `OperationLog`，`GET /api/logs`。
13. **版本更新记录窗口**：`VersionRecord` + 首页“版本更新记录”模块。

## 启动

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python run.py
```

打开：<http://127.0.0.1:8000>

## 说明

- 该工具目标运行环境是 Windows（需要 `terminal.exe` / `metaeditor.exe`）。
- 在 Linux 容器里可完成 API 与逻辑测试，但无法真实启动 MT4。
- 自动编译通过 `metaeditor.exe /compile` 调用；若环境缺失可 fallback 到手工编译 ex4 后分发。
