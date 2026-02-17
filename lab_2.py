import re

# 1. Логин
def validate_login(login):
    pattern = r'^[a-zA-Z][a-zA-Z0-9_]{3,18}[a-zA-Z0-9]$'
    return bool(re.match(pattern, login))

# 2. Даты
def find_dates(text):
    pattern = r'\b(?:(?:(?:0?[1-9]|[12][0-9]|30)[./-](?:0?[13-9]|1[0-2])|(?:0?[1-9]|[12][0-9]|30)[./-](?:0?[13-9]|1[0-2])|31[./-](?:0?[13578]|1[02])|(?:0?[1-9]|1[0-9]|2[0-8])[./-]0?2)[./-](?:\d{4}|\d{2})|29[./-]0?2[./-](?:(?:\d{2}(?:0[48]|[2468][048]|[13579][26])|(?:[02468][048]|[13579][26])00)|\d{2}))\b'
    return re.findall(pattern, text)

# 3. Логи
def parse_log(log_line):
    pattern = r'(\d{4}-\d{2}-\d{2})\s(\d{2}:\d{2}:\d{2})\s\w+\suser=(\w+)\saction=(\w+)\sip=(\d+\.\d+\.\d+\.\d+)'
    match = re.match(pattern, log_line)
    if match:
        return {
            'date': match.group(1),
            'time': match.group(2),
            'user': match.group(3),
            'action': match.group(4),
            'ip': match.group(5)
        }
    return None

# 4. Пароль
def validate_password(password):
    if len(password) < 8:
        return False
    patterns = [r'[A-Z]',r'[a-z]',r'[0-9]',r'[!@#$%^&*]']
    return all(re.search(pattern, password) for pattern in patterns)

# 5. Email
def validate_email_with_domains(email, domains):
    pattern = r'^[a-zA-Z0-9._%+-]+@(' + '|'.join(re.escape(d) for d in domains) + r')$'
    return bool(re.match(pattern, email))

# 6. Телефон
def normalize_phone(phone):
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) == 10:
        return f'+7{digits}'
    elif len(digits) == 11:
        if digits.startswith('7'):
            return f'+{digits}'
        elif digits.startswith('8'):
            return f'+7{digits[1:]}'
    return False

if __name__ == "__main__":
    # 1. Логин
    print(validate_login("user123"))
    print(validate_login("1user"))
    
    # 2. Даты
    text = "Даты: 12.05.2023, 1-1-23, 31/03/2024"
    print(find_dates(text))
    
    # 3. Логи
    log = "2024-02-10 14:23:01 INFO user=ada action=login ip=192.168.1.15"
    print(parse_log(log))
    
    # 4. Пароль
    print(validate_password("Pass123!"))
    print(validate_password("password"))
    
    # 5. Email
    domains = ['gmail.com', 'yandex.ru', 'edu.ru']
    print(validate_email_with_domains("user@gmail.com", domains))
    print(validate_email_with_domains("user@mail.ru", domains))
    
    # 6. Телефон
    print(normalize_phone("8(999)123-45-67"))
    print(normalize_phone("+7 999 123-45-67"))
    print(normalize_phone("+7 999 123-45-67"))
    print(normalize_phone("+7 999 123-45-8"))