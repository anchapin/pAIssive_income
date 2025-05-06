[1mdiff --git a/fix_indentation_issues.py b/fix_indentation_issues.py[m
[1mindex c1490f3..2bcffff 100644[m
[1m--- a/fix_indentation_issues.py[m
[1m+++ b/fix_indentation_issues.py[m
[36m@@ -111,20 +111,20 @@[m [mdef should_ignore(file_path: str, ignore_patterns: Set[str]) -> bool:[m
         if pattern.endswith("/"):[m
             # Directory pattern[m
             if pattern[:-1] in file_path.split("/"):[m
[31m-                    return True[m
[32m+[m[32m                return True[m
         elif pattern.startswith("**/"):[m
             # Match anywhere in path[m
             if file_path.endswith(pattern[3:]):[m
[31m-                    return True[m
[32m+[m[32m                return True[m
         elif pattern.startswith("/"):[m
             # Match from root[m
             if file_path.startswith(pattern[1:]):[m
[31m-                    return True[m
[32m+[m[32m                return True[m
         else:[m
             # Simple pattern[m
             if pattern in file_path:[m
[31m-                    return True[m
[31m-        return False[m
[32m+[m[32m                return True[m
[32m+[m[32m    return False[m
 [m
 [m
 def find_python_files(directory='.') -> List[Path]:[m
[36m@@ -152,7 +152,7 @@[m [mdef find_python_files(directory='.') -> List[Path]:[m
     # Also apply gitignore patterns[m
     ignore_patterns = get_gitignore_patterns()[m
 [m
[31m-        return [[m
[32m+[m[32m    return [[m
         file_path for file_path in all_python_files[m
         if not should_ignore(str(file_path.relative_to(directory)), ignore_patterns)[m
     ][m
[36m@@ -167,7 +167,7 @@[m [mdef main():[m
             fix_indentation_issues(file_path)[m
         else:[m
             print(f"Error: {file_path} is not a Python file.")[m
[31m-                return 1[m
[32m+[m[32m            return 1[m
     else:[m
         # Fix all Python files[m
         python_files = find_python_files()[m
[36m@@ -182,8 +182,8 @@[m [mdef main():[m
 [m
         print(f"\nFixed {fixed_count} files.")[m
 [m
[31m-            return 0[m
[32m+[m[32m    return 0[m
 [m
 [m
 if __name__ == "__main__":[m
[31m-    sys.exit(main()[m
[32m+[m[32m    sys.exit(main())[m
