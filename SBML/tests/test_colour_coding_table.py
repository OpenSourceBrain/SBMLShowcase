import pandas as pd

emoji_pass = "✅"
emoji_fail = "❌"

data = {"A": [1, 2, 3, 4], "B": [5, 6, 7, 8], "C": [9, 10, 11, 12], "D": [13, 14, 15, 16]}
table = pd.DataFrame(data)

table = table.applymap(lambda x: f"{emoji_pass} {x}" if x > 10 else f"{emoji_fail} {x}" if x < 5 else x)
print(table)
table.to_markdown("table.md")