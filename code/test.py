import re
user_nickname="sal(-ut"
correct_user_name=re.match("[a-zA-Z0-9]+", user_nickname)
print correct_user_name