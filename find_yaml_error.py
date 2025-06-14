import yaml


def find_yaml_error():
    file_path = ".github/workflows/codeql.yml"

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")

        print(f"Total lines in file: {len(lines)}")
        print("\nLines around 310-312:")

        for i in range(305, min(320, len(lines))):
            line_num = i + 1
            line_content = lines[i] if i < len(lines) else ""
            print(f"{line_num:3d}: {line_content!r}")

        # Try to parse YAML
        yaml.safe_load(content)
        print("YAML is valid!")

    except yaml.YAMLError as e:
        print(f"\nYAML Error: {e}")
        if hasattr(e, "problem_mark"):
            mark = e.problem_mark
            print(f"Error at line {mark.line + 1}, column {mark.column + 1}")

            # Show context around the error
            lines = content.split("\n")
            start = max(0, mark.line - 5)
            end = min(len(lines), mark.line + 6)

            print("\nContext around error:")
            for i in range(start, end):
                marker = " >>> " if i == mark.line else "     "
                print(f"{marker}{i+1:3d}: {lines[i]}")

    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    find_yaml_error()
