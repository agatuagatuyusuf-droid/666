# MT4 多开管理工具（MVP+）

本项目提供一个可视化 MT4 多实例管理后台（FastAPI + SQLite），用于模拟盘批量测试与运维。

## 覆盖能力

1. 一键创建实例（隔离目录）
2. 实例自定义命名
3. 一键克隆实例（可仅保留 MQL4/EA/指标等有用资产）
4. 自动识别 Experts/Indicators 路径，支持按实例、按组、全量分发
5. 一键把实例 Experts/Indicators 指向统一主目录（符号链接）
6. 显示 EA 运行状态、账户余额、净值（由 MT4 端脚本上报）
7. 分组管理（按组查询/分发/启动）
8. 批量启动全部或按组启动
9. 备注栏支持多端协作同步（云事件流）
10. 云端同步接口（`/api/cloud/events`）
11. 回测报告上传与同策略多实例对比
12. 操作日志记录
13. 版本更新记录窗口

## 关键接口

- `POST /api/instances` 创建实例
- `POST /api/instances/clone` 克隆实例
- `POST /api/distribute` 分发 EA/指标（支持 all/group/ids）
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

## 说明

- 目标运行环境：Windows（依赖 `terminal.exe`、`metaeditor.exe`）。
- Linux 容器可做 API 验证，但无法真实拉起 MT4。
- MQ4 自动编译通过 `metaeditor.exe /compile:<file>`，异常时可回退为手工编译 EX4 后分发。
