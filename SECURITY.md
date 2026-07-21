# Security Policy

## 支持的版本

本项目是一个研究性技术报告仓库，安全更新仅应用于以下版本：

| Version | Supported          |
|---------|--------------------|
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## 报告漏洞

如果你发现安全漏洞，请**不要**通过公开 Issue 报告。

### 私密报告流程

1. **邮件报告**: 发送邮件至 **fengyigen@qq.com**
   - 主题: `[SECURITY] TsinghuaEmbodiedAI - <简短描述>`
   - 正文: 详细描述漏洞、复现步骤、影响范围

2. **加密通信**（可选）:
   - 如果漏洞敏感，请使用 PGP 加密邮件
   - PGP 公钥可向作者索取

3. **响应时间**:
   - 收到报告后 48 小时内确认
   - 7 天内提供初步评估
   - 30 天内发布修复（如适用）

### 报告内容

请包含以下信息（尽可能详细）：

- **漏洞类型**: 例如代码执行、信息泄露、权限提升
- **影响组件**: 例如 Dockerfile、Python 脚本、LaTeX 文件
- **复现步骤**: 详细步骤，最好附带最小可复现代码
- **影响范围**: 哪些用户/系统受影响
- **建议修复**: 如有建议（可选）

## 安全措施

本项目已采取的安全措施：

### 代码安全
- **CodeQL 扫描**: 每周自动扫描 Python 代码（`.github/workflows/codeql.yml`）
- **依赖检查**: Dependabot 自动检测过时依赖
- **敏感信息检查**: `.gitignore` 排除 `.env`、`.trae/`、cookies 等敏感文件

### Docker 安全
- **最小权限**: Dockerfile 使用 `--no-install-recommends` 安装最小依赖
- **非 root 用户**: （计划中）添加非 root 用户运行应用
- **镜像扫描**: （计划中）集成 Trivy 或 Snyk 镜像扫描

### 文档安全
- **脱敏处理**: `dsw_remote.py` 中的本地路径已替换为占位符
- **凭据管理**: 不在代码中硬编码 API key、token、密码
- **环境变量**: 通过 `os.getenv()` 读取敏感配置

## 已知安全考虑

### 1. 远程代码执行（DSW Remote）
- **风险**: `dsw_remote.py` 通过 JupyterLab API 执行远程代码
- **缓解**: 仅用于可信的 DSW 实例，不暴露到公网
- **建议**: 在隔离环境中运行，限制网络访问

### 2. Docker 容器权限
- **风险**: Docker 容器使用 `--gpus all`，访问宿主机 GPU
- **缓解**: 仅在可信宿主机上运行，不共享容器镜像
- **建议**: 使用 `--gpus '"device=0"'` 限制 GPU 访问

### 3. 模型文件来源
- **风险**: `download_models.py` 从外部源下载模型 checkpoint
- **缓解**: 提供 MD5 校验（如填入）
- **建议**: 下载后验证文件完整性

## 不在范围内的行为

以下行为不被视为安全漏洞：

- **Brute force**: 对公开 API 的暴力破解
- **DoS**: 对公开服务的拒绝服务攻击
- **Social engineering**: 针对维护者的社会工程
- **物理攻击**: 对基础设施的物理攻击
- **第三方服务**: 阿里云 DSW、GitHub、Docker Hub 等的漏洞

## 联系方式

- **安全邮箱**: fengyigen@qq.com
- **PGP 公钥**: 向作者索取
- **GitHub Security**: 使用 [GitHub Security Advisory](https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI/security/advisories/new) 私密报告

## 致谢

感谢所有报告安全漏洞的研究人员！你的贡献让本项目更安全。
