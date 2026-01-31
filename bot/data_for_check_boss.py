import sqlite3

text = "2234"
workers = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
cursor = workers.cursor()
cursor.execute("INSERT INTO bosses (code, username, surname, patronymic) VALUES (?,?,?,?)",(text,"Иван", "Иванов", "Иванович"))
workers.commit()
cursor.execute("SELECT code FROM bosses WHERE code = ?",(text,))
user_data = cursor.fetchone()
print(user_data)