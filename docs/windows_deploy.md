# MT4 多开管理工具 - Windows 部署手册

> 目标：在 Windows 上将本项目作为本地管理器运行，并让多个 MT4 实例上报实时状态。

## 1. 环境准备

1. 安装 Python 3.11+
2. 准备一个目录，例如：`D:\mt4_manager`
3. 将项目代码放入该目录

## 2. 创建虚拟环境并安装依赖

在 PowerShell 执行：

```powershell
cd D:\mt4_manager
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## 3. 启动服务

```powershell
python run.py
```

默认监听：`http://127.0.0.1:8000`

可先验证：

```powershell
curl http://127.0.0.1:8000/health
```

看到 `{"ok": true, "version": "1.0.0"}` 说明服务正常。

## 4. 首次导入 MT4 实例

方式 A（推荐）：在页面里使用“自动发现实例”，填写 MT4 根目录。  
方式 B：用“创建实例”按模板复制。  
方式 C：用“克隆实例”快速复制已有策略实例。

## 5. 接入 MT4 状态上报 EA

1. 打开模板文件：`mt4_templates/MT4StatusReporter.mq4`
2. 在 MT4 的 `MQL4/Experts` 下放入并编译
3. 将 EA 挂到每个需要上报的图表
4. EA 参数中设置：
   - `ManagerUrl = http://127.0.0.1:8000`
   - `InstanceId = 管理器中的实例ID`
5. 确保 MT4 已开启：
   - “允许 DLL 导入”（如你的策略依赖）
   - “允许 WebRequest”
   - 并在 MT4 里添加白名单 URL：`http://127.0.0.1:8000`

## 6. 日常操作建议

- 新 EA 发布：优先用“MQ4 编译并分发”
- 稳定发布：先在 1 个实例验证，再按组分发
- 指标统一：可用“统一符号链接”让所有实例共享同一主目录
- 清理实例：删除时优先“仅注销不删目录”，确认后再硬删除

## 7. 开机自启（可选）

可建立 `start_manager.bat`：

```bat
@echo off
cd /d D:\mt4_manager
call .venv\Scripts\activate.bat
python run.py
```

将其加入“启动”文件夹即可。

## 8. 常见问题

1. **编译失败：`metaeditor.exe not found`**  
   检查源实例目录下是否存在 `metaeditor.exe`。

2. **上报失败：403 / 无响应**  
   检查 MT4 WebRequest 白名单和本机防火墙。

3. **分发成功但策略未更新**  
   MT4 可能需刷新导航器或重启终端。
