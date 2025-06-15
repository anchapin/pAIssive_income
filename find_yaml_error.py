import yaml


def find_yaml_error() -> None:
    file_path = ".github/workflows/codeql.yml"

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")


        for i in range(305, min(320, len(lines))):
            i + 1
            lines[i] if i < len(lines) else ""

        # Try to parse YAML
        yaml.safe_load(content)

    except yaml.YAMLError as e:
        if hasattr(e, "problem_mark"):
            mark = e.problem_mark

            # Show context around the error
            lines = content.split("\n")
            start = max(0, mark.line - 5)
            end = min(len(lines), mark.line + 6)

            for i in range(start, end):
                pass

    except Exception:
        pass

if __name__ == "__main__":
    find_yaml_error()
