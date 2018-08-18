import re

str = '-0.11'
str = re.sub(r'[^-.0-9]', '', str)
print(str)