#!/usr/bin/env python3
"""
SuperClaude Command Hook
사용자 프롬프트가 /sc: 로 시작하면 자동으로 Skill tool 사용을 안내
"""
import json
import sys
import re


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    prompt = input_data.get("prompt", "").strip()

    # /sc:command 패턴 매칭 (프롬프트 시작 부분)
    match = re.match(r"^/sc:([\w-]+)(?:\s+(.*))?$", prompt, re.DOTALL)

    if match:
        command = match.group(1)
        args = match.group(2) or ""

        # stderr로 알림 메시지 출력
        print(f"✅ SuperClaude Hook: /sc:{command} 감지됨", file=sys.stderr)

        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": f"""
[SUPERCLAUDE COMMAND DETECTED]
User is invoking SuperClaude command: /sc:{command}
Arguments: {args.strip() if args else '(none)'}

IMPORTANT: You MUST use the Skill tool to execute this command.
- skill: "sc:{command}"
- args: "{args.strip()}"

Execute this skill immediately without asking for confirmation.
""",
            }
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
