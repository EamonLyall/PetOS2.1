# ============================================================
# 数据库工具：导出 / 导入 / 重置 / 统计（SQLite）
#
# 用途（答辩前给队友同步同一份演示数据）：
#   1) 导出当前数据库为 SQL 脚本，随项目提交，队友拉代码后导入即可得到完全一致的数据：
#        python scripts/db_tool.py export
#        python scripts/db_tool.py import --force
#   2) 重置为初始种子数据（清空所有互动/聊天/开关状态）：
#        python scripts/db_tool.py reset --yes
#   3) 查看各表行数，确认数据完整：
#        python scripts/db_tool.py stats
#
# 说明：
#   - 导出使用 sqlite3 官方 iterdump，包含建表语句与全部 INSERT，可直接用 sqlite3 执行；
#   - 导入会覆盖当前 backend/petos.db，请先确认已在项目根目录备份；
#   - 所有命令均在 backend 目录下执行。
# ============================================================

import argparse
import sqlite3
import sys
from pathlib import Path

# 保证以 `python scripts/db_tool.py` 运行时能导入 app 包
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.database import DB_PATH, init_db  # noqa: E402

# 默认导出路径：backend/sql/petos_companion_sqlite.sql
DEFAULT_EXPORT = BACKEND_DIR / "sql" / "petos_companion_sqlite.sql"


def cmd_export(out: Path) -> None:
    """把当前数据库完整导出为 SQL 脚本。"""
    if not DB_PATH.exists():
        raise SystemExit(f"数据库不存在：{DB_PATH}，请先启动一次后端生成种子数据。")

    out.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        lines = list(conn.iterdump())
    finally:
        conn.close()

    header = [
        "-- ============================================================",
        "-- PetOS 陪伴系统 · SQLite 数据快照（由 scripts/db_tool.py 自动导出）",
        "-- 导入方式：python scripts/db_tool.py import --force",
        "-- 说明：包含建表语句与全部业务数据，导入后与导出时状态完全一致。",
        "-- ============================================================",
        "",
    ]
    out.write_text("\n".join(header + lines) + "\n", encoding="utf-8")
    print(f"[OK] 已导出 {len(lines)} 条 SQL 语句 -> {out}")


def cmd_import(src: Path, force: bool) -> None:
    """用 SQL 快照覆盖当前数据库。"""
    if not src.exists():
        raise SystemExit(f"SQL 文件不存在：{src}")
    if DB_PATH.exists() and not force:
        raise SystemExit(f"数据库已存在：{DB_PATH}；确认覆盖请加 --force")

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(src.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()

    # 导入后执行一次建表/迁移，兼容旧快照
    init_db()
    print(f"[OK] 已从 {src} 导入数据库 -> {DB_PATH}")


def cmd_reset(confirmed: bool) -> None:
    """删除数据库并重新灌入种子数据。"""
    if not confirmed:
        raise SystemExit("重置会清空当前数据库；确认请加 --yes")
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()
    print(f"[OK] 已重置数据库（种子数据已重新写入）-> {DB_PATH}")


def cmd_stats() -> None:
    """打印各表行数，便于答辩前确认数据完整。"""
    if not DB_PATH.exists():
        raise SystemExit(f"数据库不存在：{DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    try:
        tables = [
            r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        print(f"数据库：{DB_PATH}")
        for table in tables:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {table:<22} {count:>4} 行")
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="PetOS SQLite 数据库导出 / 导入 / 重置工具")
    sub = parser.add_subparsers(dest="command", required=True)

    p_export = sub.add_parser("export", help="导出当前数据库为 SQL 快照")
    p_export.add_argument("--out", type=Path, default=DEFAULT_EXPORT, help="导出文件路径")

    p_import = sub.add_parser("import", help="从 SQL 快照导入数据库")
    p_import.add_argument("--in", dest="src", type=Path, default=DEFAULT_EXPORT, help="SQL 文件路径")
    p_import.add_argument("--force", action="store_true", help="覆盖已存在的数据库")

    p_reset = sub.add_parser("reset", help="重置为初始种子数据")
    p_reset.add_argument("--yes", action="store_true", help="确认清空当前数据库")

    sub.add_parser("stats", help="查看各表行数")

    args = parser.parse_args()
    if args.command == "export":
        cmd_export(args.out)
    elif args.command == "import":
        cmd_import(args.src, args.force)
    elif args.command == "reset":
        cmd_reset(args.yes)
    elif args.command == "stats":
        cmd_stats()


if __name__ == "__main__":
    main()
