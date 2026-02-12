# MT4 多开管理工具（v1.0）

本项目提供一个可视化 MT4 多实例管理后台（FastAPI + SQLite），用于模拟盘批量测试与运维。

## 已实现能力

1. 一键创建实例（隔离目录）
2. 自动发现实例（扫描 root_path 下 terminal.exe）
3. 一键克隆实例（可仅保留 MQL4/EA/指标等有用资产）
4. 实例命名、改组、删除（可选同时删除实例目录）
5. 自动识别 Experts/Indicators 路径，支持按实例、按组、全量分发
6. MQ4 一键编译后批量分发 EX4
7. 一键把实例 Experts/Indicators 指向统一主目录（符号链接）
8. 显示 EA 运行状态、账户余额、净值（由 MT4 端脚本上报）
9. 分组管理（按组查询/分发/启动）
10. 批量启动全部或按组启动
11. 备注栏支持多端协作同步（云事件流）
12. 云端同步接口（`/api/cloud/events`）
13. 回测报告上传与同策略多实例对比
14. 操作日志记录
15. 版本更新记录窗口

## 关键接口

- `GET /health` 健康检查
- `POST /api/instances` 创建实例
- `POST /api/instances/discover` 自动发现实例
- `POST /api/instances/clone` 克隆实例
- `DELETE /api/instances/{id}?delete_files=true|false` 删除实例
- `PATCH /api/instances/{id}/rename` 重命名
- `PATCH /api/instances/{id}/group` 修改分组
- `POST /api/distribute` 分发 EA/指标（支持 all/group/ids）
- `POST /api/distribute/compile` 编译 MQ4 并分发 EX4
- `POST /api/symlink` 统一符号链接
- `POST /api/report/status` 实时状态上报
- `POST /api/launch` / `POST /api/instances/{id}/launch` 启动
- `POST /api/backtests` + `GET /api/backtests/compare`
- `GET /api/logs` / `GET /api/versions` / `GET /api/cloud/events`

## 启动

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python run.py
```

访问：<http://127.0.0.1:8000>

## 交付物

- Windows 部署手册：`docs/windows_deploy.md`
- MT4 状态上报 EA 模板：`mt4_templates/MT4StatusReporter.mq4`

## 说明

- 目标运行环境：Windows（依赖 `terminal.exe`、`metaeditor.exe`）。
- Linux 容器可做 API 验证，但无法真实拉起 MT4。
- MQ4 自动编译通过 `metaeditor.exe /compile:<file>`，异常时可回退为手工编译 EX4 后分发。
