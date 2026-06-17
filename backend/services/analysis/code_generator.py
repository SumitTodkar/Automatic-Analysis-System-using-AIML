import re
import os
import ast
import time
import pandas as pd
from typing import List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import google.generativeai as genai
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

from .utils import load_schema
from core.config.settings import get_settings
from core.config.paths import path_config
from core.logging.logger import get_logger, log_execution
from domain.exceptions.custom import CodeGenerationError

logger = get_logger(__name__)


class CodeGenerator:
    def __init__(self):
        settings = get_settings()

        self.response_dir = path_config.RESPONSE_DIR
        self.stats_dir = path_config.STATS_DIR
        self.graphs_dir = path_config.GRAPHS_DIR
        self.schema = load_schema()

        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            convert_system_message_to_human=True,
            temperature=0.1
        )

        self._setup_prompt_template()

    def _setup_prompt_template(self):
        # Fix 2: Stricter stats dict instructions in prompt
        system_content = (
            "You are a Python data analysis expert. Generate ONLY valid, executable Python code.\n"
            "No explanations. No markdown. No prose.\n\n"
            "THE CODE MUST USE THESE EXACT VARIABLES (already defined, do NOT redefine them):\n"
            "  graph_file  -> full path to save the PNG chart\n"
            "  stats_file  -> full path to save the JSON stats\n"
            "  QUESTION    -> the analysis question string\n"
            "  DATA_PATH   -> full path to the CSV file (ALWAYS use this to read data)\n\n"
            "STATS DICT - USE ONLY THIS EXACT FORMAT, nothing else:\n"
            "  stats = {{\n"
            "      'question': QUESTION,\n"
            "      'total': float(df['col'].sum()),\n"
            "      'mean': float(df['col'].mean()),\n"
            "      'median': float(df['col'].median()),\n"
            "      'std': float(df['col'].std()),\n"
            "      'min': float(df['col'].min()),\n"
            "      'max': float(df['col'].max()),\n"
            "      'count': int(len(df))\n"
            "  }}\n\n"
            "WARNING: Do NOT use list comprehensions, for loops, ternary operators,\n"
            "or nested dicts inside stats. Every value must be a single function call\n"
            "like float(...) or int(...). Missing commas WILL cause a crash.\n\n"
            "MANDATORY - end your code with EXACTLY these lines:\n"
            "  plt.savefig(graph_file, bbox_inches='tight', dpi=100)\n"
            "  plt.close()\n"
            "  with open(stats_file, 'w') as f: json.dump(stats, f, indent=4)\n\n"
            "RULES:\n"
            "- Convert ALL numpy values: float(x) or int(x)\n"
            "- Handle NaN: df.dropna() or fillna(0)\n"
            "- Use seaborn or matplotlib for charts\n"
        )

        self.code_prompt = ChatPromptTemplate.from_messages([
            ("system", system_content),
            (
                "human",
                "Task: {question}\n\n"
                "Columns: {columns}\n"
                "Data sample:\n{head_data}\n\n"
                "Data path: {data_path}\n"
                "Data types: {data_type}\n"
                "Schema: {schema}\n",
            ),
        ])

        self.chain = self.code_prompt | self.llm

    def _build_mandatory_header(self, question: str, safe_base: str, data_path: str = '') -> str:
        return (
            f'import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns\n'
            f'import warnings; warnings.filterwarnings("ignore")\n'
            f'sns.set()\n'
            f'plt.ioff()\n\n'
            f'RESPONSE_DIR = r"{self.response_dir}"\n'
            f'STATS_DIR = r"{self.stats_dir}"\n'
            f'GRAPHS_DIR = r"{self.graphs_dir}"\n\n'
            f'# ── Always use DATA_PATH to read the CSV ──\n'
            f'DATA_PATH = r"{data_path}"\n'
            f'QUESTION = """{question}"""\n'
            f'base_name = "{safe_base}"\n'
            f'graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")\n'
            f'stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")\n\n'
        )

    def _build_safe_fallback_footer(self) -> str:
        return (
            '\n# Fallback save - ensures files always get written\n'
            'if not os.path.exists(graph_file):\n'
            '    plt.savefig(graph_file, bbox_inches="tight", dpi=100)\n'
            '    plt.close()\n'
            'if not os.path.exists(stats_file):\n'
            '    if "stats" not in dir():\n'
            '        stats = {"question": QUESTION, "note": "No stats generated"}\n'
            '    with open(stats_file, "w") as f:\n'
            '        json.dump(stats, f, indent=4)\n'
        )

    def _strip_duplicates(self, code: str) -> str:
        skip_patterns = [
            r'^\s*import os\b', r'^\s*import json\b', r'^\s*import pandas\b',
            r'^\s*import numpy\b', r'^\s*import matplotlib\b', r'^\s*import seaborn\b',
            r'^\s*from os\b', r'^\s*sns\.set\(', r'^\s*plt\.ioff\(',
            r'^\s*RESPONSE_DIR\s*=', r'^\s*STATS_DIR\s*=', r'^\s*GRAPHS_DIR\s*=',
            r'^\s*base_name\s*=', r'^\s*graph_file\s*=', r'^\s*stats_file\s*=',
            r'^\s*QUESTION\s*=',
            r'^\s*DATA_PATH\s*=',
        ]
        lines = code.split("\n")
        filtered = [l for l in lines if not any(re.match(p, l) for p in skip_patterns)]
        return "\n".join(filtered).strip()

    @log_execution
    def remove_code_block_formatting(self, code: str) -> str:
        return re.sub(r"```(?:python)?\s*|\s*```", "", code).strip()

    def _validate_syntax(self, code: str) -> tuple:
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"

    def _auto_fix_stats_dict(self, code: str) -> str:
        # Fix 1: Use brace-counting instead of regex to find full stats dict
        start = code.find('stats = {')
        if start == -1:
            return code

        depth = 0
        end = -1
        for i, ch in enumerate(code[start:], start):
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break

        if end == -1:
            return code

        block = code[start:end]
        try:
            ast.parse(block)
            return code  # Valid, no fix needed
        except SyntaxError:
            logger.warning("Broken stats dict detected, replacing with safe fallback")
            safe_stats = (
                'stats = {\n'
                '    "question": QUESTION,\n'
                '    "mean": float(df.select_dtypes(include="number").mean().mean()) if not df.select_dtypes(include="number").empty else 0.0,\n'
                '    "count": int(len(df)),\n'
                '    "columns": str(list(df.columns))\n'
                '}'
            )
            return code[:start] + safe_stats + code[end:]

    def _build_minimal_safe_code(self, question: str, safe_base: str, data_path: str) -> str:
        """Last resort: guaranteed-working minimal analysis."""
        header = self._build_mandatory_header(question, safe_base)
        return header + (
            f'df = pd.read_csv(DATA_PATH)\n'
            f'df = df.dropna()\n\n'
            f'numeric_cols = df.select_dtypes(include="number").columns.tolist()\n'
            f'plt.figure(figsize=(10, 6))\n'
            f'if numeric_cols:\n'
            f'    df[numeric_cols[0]].plot(kind="hist", bins=20, color="steelblue")\n'
            f'    plt.title("Distribution of " + numeric_cols[0])\n'
            f'else:\n'
            f'    df.iloc[:, 0].value_counts().plot(kind="bar")\n'
            f'    plt.title("Value Counts")\n'
            f'plt.tight_layout()\n'
            f'plt.savefig(graph_file, bbox_inches="tight", dpi=100)\n'
            f'plt.close()\n\n'
            f'stats = {{\n'
            f'    "question": QUESTION,\n'
            f'    "rows": int(len(df)),\n'
            f'    "columns": str(list(df.columns)),\n'
            f'    "note": "Minimal fallback analysis"\n'
            f'}}\n'
            f'with open(stats_file, "w") as f:\n'
            f'    json.dump(stats, f, indent=4)\n'
        )

    @log_execution
    def generate_code_for_question(
        self,
        question: str,
        columns: List[str],
        head_data: pd.DataFrame,
        data_path: str,
        d_types: Dict[str, str],
        schema: Dict[str, Any],
    ) -> tuple:
        try:
            response = self.chain.invoke({
                "columns": columns,
                "head_data": head_data.to_string(),
                "question": question,
                "data_path": data_path,
                "data_type": d_types,
                "schema": schema,
            })

            safe_base = f"analysis_{int(time.time())}"

            # Step 1: Clean markdown
            code = self.remove_code_block_formatting(response.content)

            # Step 2: Strip duplicate imports/paths
            code = self._strip_duplicates(code)

            # Step 3: Auto-fix broken stats dict using brace-counting
            code = self._auto_fix_stats_dict(code)

            # Step 4: Build header (imports first, then paths, then vars)
            header = self._build_mandatory_header(question, safe_base, data_path)

            # Step 5: Add fallback footer
            footer = self._build_safe_fallback_footer()

            # Step 6: Assemble final code
            final_code = header + code + footer

            # Step 7: Validate syntax — use minimal safe code if still broken
            is_valid, error = self._validate_syntax(final_code)
            if not is_valid:
                logger.warning(f"Syntax error after assembly: {error}. Using minimal safe code.")
                final_code = self._build_minimal_safe_code(question, safe_base, data_path)

            filename = f"{safe_base}.png"
            return final_code, filename

        except Exception as e:
            raise CodeGenerationError(str(e))

    @log_execution
    def save_generated_code(self, code: str) -> str:
        code_path = path_config.CODE_DIR / "generated_analysis_code.py"
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code)
        return str(code_path)

    @log_execution
    def generate(self, provided_questions: List[str] = None) -> Dict[str, Any]:
        try:
            if not os.environ.get("DATA_FILE_PATH"):
                raise ValueError("No data file path provided")

            data_path = os.environ["DATA_FILE_PATH"]
            df = pd.read_csv(data_path)

            columns = df.columns.tolist()
            head_data = df.head()
            d_types = df.dtypes.apply(str).to_dict()

            generated_code = ""
            filenames = []

            for i, question in enumerate(provided_questions or []):
                code, filename = self.generate_code_for_question(
                    question, columns, head_data, data_path, d_types, self.schema
                )
                generated_code += (
                    f"# Question {i + 1}: {question}\n"
                    f"# Output: {filename}\n{code}\n\n"
                )
                filenames.append(filename)

            code_path = self.save_generated_code(generated_code)

            return {
                "code": generated_code,
                "filenames": filenames,
                "code_path": code_path,
                "status": "success",
            }

        except Exception as e:
            logger.error(str(e))
            raise CodeGenerationError(str(e))