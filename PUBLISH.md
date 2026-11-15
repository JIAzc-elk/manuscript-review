# 发布说明

## 当前状态

- 版本：`0.1.2`（beta）
- 结构测试：`python3 -m unittest discover -s tests` → 12 项通过
- 报告检查：`python3 .agents/skills/manuscript-review/scripts/check_report.py examples/sample_report.md` → 通过
- 已包含：素材交接门、故事设计透镜（Craft Scorecard / Craft Index）、七角色、三端适配、只读契约、示例与测试

## 发布前检查

- [x] `VERSION` 与 `CHANGELOG.md` 一致
- [x] `LICENSE`（MIT）与 `THIRD_PARTY_NOTICES.md`
- [x] 未包含用户设定库、小说正文或私人材料
- [x] 未包含 API key、token、个人绝对路径
- [x] 12 项结构测试通过
- [x] 示例报告通过 `check_report.py`

## 推送到 GitHub

本目录已经是一个本地 Git 仓库。创建远程仓库后，任选一种方式：

### 方式 A：已安装 GitHub CLI

```bash
gh repo create manuscript-review --public --source=. --remote=origin --push
```

建议描述：

> 正文审核器：多角色、只读的正文审核 skill；输出故事设计评分、证据锚点与修改报告。

### 方式 B：手动创建仓库

先在 GitHub 网页创建空仓库（不要勾选 README / .gitignore / LICENSE），然后：

```bash
git remote add origin git@github.com:<你的用户名>/manuscript-review.git
git branch -M main
git push -u origin main
```

HTTPS 方式同理，把 remote 换成 `https://github.com/<你的用户名>/manuscript-review.git`。

## 发布后建议

1. 在仓库 About 中填写描述与 topics：`novel`、`writing`、`review`、`skill`、`opencode`、`claude-code`、`codex`。
2. 若要做正式 Release，打 tag：`git tag v0.1.2 && git push origin v0.1.2`。
3. 若未来加入第三方方法卡或参考作品，先更新 `THIRD_PARTY_NOTICES.md`。
4. 不要把用户的设定库、小说正文或私人项目提交进本仓库。
