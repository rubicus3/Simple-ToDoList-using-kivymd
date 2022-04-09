import sqlite3

db = sqlite3.connect("ToDoList.db")


def select_tasks_by_group_id(group_id):
    select = db.execute("SELECT text, task_id, is_checked FROM TASKS WHERE group_id = ?", [group_id])
    tasks = []
    for i in select:
        print(i)
        tasks.append(list(i))
    return tasks


def select_all_groups():
    select = db.execute("SELECT * FROM GROUPS")
    groups = []
    for i in select:
        groups.append(list(i))
    return groups


def create_task(group_id, text):
    db.execute("INSERT into Tasks (text, group_id) VALUES(?, ?)", [text, group_id])
    select = db.execute("SELECT max(task_id) from Tasks as id")
    db.commit()
    for i in select:
        return i[0]


def create_group(name: str):
    db.execute("INSERT into Groups (name) VALUES(?)", [name])
    select = db.execute("SELECT max(group_id) from Groups as id")
    db.commit()
    for i in select:
        return i[0]


def update_task(task_id: int, text: str):
    db.execute("UPDATE Tasks SET text = ? where task_id = ?", [text, task_id])
    db.commit()


def update_group(group_id: int, name: str):
    db.execute("UPDATE Groups SET name = ? where group_id = ?", [name, group_id])
    db.commit()


def delete_task(task_id: int):
    db.execute("DELETE from Tasks where task_id = ?", [task_id])
    db.commit()


def delete_group(group_id: int):
    db.execute("DELETE from Tasks where group_id = ?", [group_id])
    db.execute("DELETE from Groups where group_id = ?", [group_id])
    db.commit()


def task_check(task_id: int, is_checked: bool):
    db.execute("UPDATE Tasks SET is_checked = ? where task_id = ?", [is_checked, task_id])
    db.commit()
