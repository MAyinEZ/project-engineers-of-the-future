import sqlite3

id = [5209227231]#,591742354]
text = "РАБОТАЕМ НАД ПРОЕКТОМ!\n"
workers = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
cursor = workers.cursor()
for i in id:
    cursor.execute("UPDATE tasks SET name_task = ?, task_description = ?, task_time = ?, check_acceptance = ?, degree_of_readiness = ? WHERE user_id = ?", ("делать проект",text,300,1,0,i))
    workers.commit()
    cursor.execute("SELECT task_description FROM tasks WHERE user_id = ?",(i,))
    user_data = cursor.fetchone()
    print(user_data)
workers.close()