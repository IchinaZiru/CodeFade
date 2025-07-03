import os
import re
import random

# === 言語と拡張子マップ ===
EXT_LANG_MAP = {
    ".c": "c", ".cc": "cpp", ".cpp": "cpp", ".cxx": "cpp", ".h": "cpp", ".hpp": "cpp",
    ".py": "python", ".java": "java", ".js": "javascript", ".ts": "typescript",
    ".go": "go", ".rs": "rust", ".swift": "swift", ".cs": "csharp"
}

# === コメントパターンマップ ===
COMMENT_PATTERNS = {
    "c":    {"line": r'//.*',              "block": r'/\*[\s\S]*?\*/'},
    "cpp":  {"line": r'//.*',              "block": r'/\*[\s\S]*?\*/'},
    "java": {"line": r'//.*',              "block": r'/\*[\s\S]*?\*/'},
    "csharp": {"line": r'//.*',            "block": r'/\*[\s\S]*?\*/'},
    "go":   {"line": r'//.*',              "block": r'/\*[\s\S]*?\*/'},
    "rust": {"line": r'//.*',              "block": r'/\*[\s\S]*?\*/'},
    "swift":{"line": r'//.*',              "block": r'/\*[\s\S]*?\*/'},
    "javascript": {"line": r'//.*',        "block": r'/\*[\s\S]*?\*/'},
    "typescript": {"line": r'//.*',        "block": r'/\*[\s\S]*?\*/'},
    "python":{"line": r'#.*',              "block": r'("""[\s\S]*?""")|(\'\'\'[\s\S]*?\'\'\')'},
}

# === パラメータ設定 ===
SOURCE_DIR   = "./source"     # オリジナルソースのディレクトリ
OUTPUT_BASE  = "./output"# 出力先ベースディレクトリ
VERSIONS     = [5, 20, 75, 100]      # v0, v25, v50, v100

os.makedirs(OUTPUT_BASE, exist_ok=True)

# ファイル走査
for root, _, files in os.walk(SOURCE_DIR):
    for name in files:
        ext = os.path.splitext(name)[1].lower()
        lang = EXT_LANG_MAP.get(ext)
        if not lang or lang not in COMMENT_PATTERNS:
            continue

        patterns = COMMENT_PATTERNS[lang]
        src_path = os.path.join(root, name)
        with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()

        # コメント位置を抽出 (start, end のタプルリスト)
        comments = []
        if patterns.get("line"):
            for m in re.finditer(patterns["line"], code, re.MULTILINE):
                comments.append((m.start(), m.end()))
        if patterns.get("block"):
            for m in re.finditer(patterns["block"], code, re.MULTILINE | re.DOTALL):
                comments.append((m.start(), m.end()))

        comments = sorted(set(comments))

        # 各バージョンを生成
        for version in VERSIONS:
            keep_ratio = 1 - (version / 100)
            keep_count = int(len(comments) * keep_ratio)
            keep_idxs = set(random.sample(range(len(comments)), keep_count)) if keep_count else set()

            new_code = []
            last = 0
            for idx, (s, e) in enumerate(comments):
                if idx in keep_idxs:
                    continue
                new_code.append(code[last:s])
                last = e
            new_code.append(code[last:])

            rel = os.path.relpath(src_path, SOURCE_DIR).replace(os.sep, "_")
            out_dir = os.path.join(OUTPUT_BASE, f"v{version}")
            os.makedirs(out_dir, exist_ok=True)
            save_path = os.path.join(out_dir, rel)
            with open(save_path, "w", encoding="utf-8") as out:
                out.write(''.join(new_code))

print("段階的コメント削除ファイルを保存しました！")
