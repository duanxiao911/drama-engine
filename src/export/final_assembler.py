"""
最终文档组装器

将8个专家的输出组装成专业剧本格式文档：
一、基础信息（来自§8项目配置）
二、人物小传（来自§1角色铸造）
三、分集大纲（来自§3结构建筑师）
四、分场剧本（来自§5分集编剧）
五、对白语料库（来自§4对白大师）
六、视觉方案（来自§13视觉导演）

输入：result.json
输出：组装后的markdown文件
"""

import json
import os
from typing import Dict, Optional
from pathlib import Path


class FinalAssembler:
    """最终文档组装器"""

    def __init__(self, result_json_path: str, output_dir: Optional[str] = None):
        self.result_json_path = result_json_path
        self.output_dir = output_dir or os.path.dirname(result_json_path)
        self.data = {}
        self._load_result()

    def _load_result(self):
        """加载result.json"""
        with open(self.result_json_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def _get_step_output(self, expert_id: str) -> Dict:
        """获取指定专家的输出（兼容outputs和step_outputs两种结构）"""
        outputs = self.data.get("outputs", {}) or self.data.get("step_outputs", {})
        return outputs.get(expert_id, {})

    def _get_content(self, expert_id: str) -> str:
        """获取指定专家的内容"""
        output = self._get_step_output(expert_id)
        # 优先从structured_data.raw获取
        sd = output.get("structured_data", {})
        if sd.get("raw"):
            return sd["raw"]
        if output.get("content"):
            return output["content"]
        return ""

    def assemble_markdown(self) -> str:
        """组装完整markdown文档"""
        sections = []

        # 标题
        context = self.data.get("context", {})
        project_name = context.get("project_name", "") or context.get("story_direction", "")[:30]
        sections.append(f"# {project_name}\n")
        sections.append("> 本文档由云匠·精品短剧创作引擎自动生成\n")
        sections.append(f"> 工作流ID: {self.data.get('workflow_id', '')}\n")

        # 一、基础信息
        sections.append("---\n")
        sections.append("## 一、基础信息\n")
        config_content = self._get_content("§8")
        if config_content:
            sections.append(config_content)
        sections.append("\n")

        # 二、人物小传
        sections.append("---\n")
        sections.append("## 二、人物小传\n")
        char_content = self._get_content("§1")
        if char_content:
            sections.append(char_content)
        sections.append("\n")

        # 三、分集大纲
        sections.append("---\n")
        sections.append("## 三、分集大纲\n")
        outline_content = self._get_content("§3")
        if outline_content:
            sections.append(outline_content)
        sections.append("\n")

        # 四、分场剧本（核心产出）
        sections.append("---\n")
        sections.append("## 四、分场剧本\n")
        script_content = self._get_content("§5")
        if script_content:
            sections.append(script_content)
        sections.append("\n")

        # 五、对白语料库
        sections.append("---\n")
        sections.append("## 五、对白语料库\n")
        dialogue_content = self._get_content("§4")
        if dialogue_content:
            sections.append(dialogue_content)
        sections.append("\n")

        # 六、视觉方案
        sections.append("---\n")
        sections.append("## 六、视觉方案\n")
        visual_content = self._get_content("§13")
        if visual_content:
            sections.append(visual_content)
        sections.append("\n")

        return "\n".join(sections)

    def assemble_and_save(self, filename: Optional[str] = None) -> str:
        """组装并保存markdown文件"""
        md_content = self.assemble_markdown()
        if not filename:
            wf_id = self.data.get("workflow_id", "output")
            filename = f"{wf_id}_完整剧本.md"
        output_path = os.path.join(self.output_dir, filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"[FinalAssembler] 文档已保存: {output_path}")
        print(f"[FinalAssembler] 文档长度: {len(md_content)} 字符")
        return output_path


def assemble_from_result(result_json_path: str, output_dir: Optional[str] = None) -> str:
    """快捷函数：从result.json组装文档"""
    assembler = FinalAssembler(result_json_path, output_dir)
    return assembler.assemble_and_save()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python final_assembler.py <result.json路径> [输出目录]")
        sys.exit(1)
    result_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else None
    output = assemble_from_result(result_path, out_dir)
    print(f"输出文件: {output}")
