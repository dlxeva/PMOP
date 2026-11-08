This directory is an inventory target only. It contains no project and no `SKILL.md`.

```sh
python3 scripts/capability_index.py --root ./examples --format json
```

The command returns an empty skill list. `scripts/demo.py` uses its own temporary directory and does not write here.

本目录只作为盘点目标，不含项目，也没有 `SKILL.md`。

上面的命令会得到空的技能列表。`scripts/demo.py` 使用自己的临时目录，不会往这里写文件。
