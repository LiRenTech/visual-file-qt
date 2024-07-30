from gitignore_parser import parse_gitignore

matches_function = parse_gitignore("D:/Projects/Project-Tools/CodeEmpire/.gitignore")

print(matches_function("D:/Projects/Project-Tools/CodeEmpire/tools/__pycache__"))
print(
    matches_function(
        "D:/Projects/Project-Tools/CodeEmpire/tools/__pycache__/string_tools.cpython-311.pyc"
    )
)
print(matches_function("D:/Projects/Project-Tools/CodeEmpire/requirements.txt"))
