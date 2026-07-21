# Contributing to TsinghuaEmbodiedAI

感谢你对本项目的兴趣！欢迎通过 Issue 和 Pull Request 贡献代码、报告问题或提出建议。

## 行为准则

参与本项目的所有贡献者需遵守 [Code of Conduct](CODE_OF_CONDUCT.md)。请保持尊重和包容。

## 如何贡献

### 报告 Bug

1. 在 [Issues](https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI/issues) 页面搜索是否已有相同问题
2. 如果没有，点击 "New Issue" 选择 "Bug Report" 模板
3. 详细描述：
   - 复现步骤
   - 期望行为 vs 实际行为
   - 环境信息（OS、Python 版本、依赖版本）
   - 错误日志（如有）

### 提交功能建议

1. 在 [Issues](https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI/issues) 页面创建新 Issue
2. 描述功能用途、使用场景、预期效果
3. 如果可能，附上设计草图或伪代码

### 提交 Pull Request

1. **Fork 仓库** 到你的 GitHub 账号
2. **创建分支**：
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/issue-XXX
   ```
3. **编写代码**：
   - 遵循现有代码风格（PEP 8）
   - 添加必要的注释和 docstring
   - 新功能需附带测试
4. **运行测试**：
   ```bash
   # Python 语法检查
   python -m py_compile <your_file.py>

   # 如果有单元测试
   pytest tests/
   ```
5. **提交变更**：
   ```bash
   git add <files>
   git commit -m "feat: 添加 XXX 功能"  # 或 "fix: 修复 XXX 问题"
   ```
   - Commit message 遵循 [Conventional Commits](https://www.conventionalcommits.org/)
   - 前缀：`feat:`/`fix:`/`docs:`/`refactor:`/`test:`/`chore:`
6. **推送到你的 Fork**：
   ```bash
   git push origin feature/your-feature-name
   ```
7. **创建 Pull Request**：
   - 在 GitHub 页面点击 "Compare & pull request"
   - 填写 PR 描述：变更内容、关联 Issue、测试方式

## 开发环境

### 推荐配置

- Python 3.12
- MuJoCo 3.10.0
- NumPy 2.1.3 + Numba 0.66.0
- EGL 渲染（Linux）或 OSMesa（无 GPU 环境）

### 本地设置

```bash
# 克隆仓库
git clone https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI.git
cd TsinghuaEmbodiedAI

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 下载模型 checkpoint（如需复现 100/100）
python scripts/download_models.py --check-only
```

### Docker 环境

```bash
# 构建镜像
docker build -t jciiot:latest .

# 启动容器
docker-compose up -d
docker-compose exec jciiot bash
```

## 代码风格

- **Python**: 遵循 [PEP 8](https://peps.python.org/pep-0008/)
- **行宽**: 100 字符
- **缩进**: 4 空格（不使用 tab）
- **Import 顺序**: 标准库 → 第三方库 → 本地模块
- **Docstring**: Google 风格

```python
def example_function(param1: str, param2: int = 0) -> bool:
    """示例函数的简短描述.

    Args:
        param1: 第一个参数的描述.
        param2: 第二个参数的描述，默认为 0.

    Returns:
        返回值的描述.

    Raises:
        ValueError: 当 param1 为空时.
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    return True
```

## 测试

- 新功能需附带单元测试（位于 `tests/` 目录）
- 使用 `pytest` 作为测试框架
- 测试覆盖率目标：>70%

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_factory_sorting.py -v

# 生成覆盖率报告
pytest tests/ --cov=JCIIOT --cov-report=html
```

## 提交规范

### Commit Message 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `refactor`: 代码重构（无功能变化）
- `test`: 测试相关
- `chore`: 构建、依赖、配置等

**示例**:
```
feat(grasp): add tote skip-lift fallback for single-arm grasp

fix(quaternion): resolve sign flip in right_eef_quat for L3 policy

docs(readme): update 100/100 results table
```

### 分支命名

- `feature/<feature-name>`: 新功能
- `fix/<issue-number>`: Bug 修复
- `docs/<topic>`: 文档更新
- `refactor/<module>`: 代码重构

## 发布流程

本项目使用 [Semantic Versioning](https://semver.org/):

- `MAJOR.MINOR.PATCH`
- MAJOR: 不兼容的 API 变更
- MINOR: 向下兼容的新功能
- PATCH: 向下兼容的 Bug 修复

## 许可证

提交的代码将遵循 [MIT License](LICENSE)。

## 联系方式

- **作者**: Yigen Feng (fengyigen@qq.com)
- **Issues**: [GitHub Issues](https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI/issues)
- **邮件**: fengyigen@qq.com

再次感谢你的贡献！
