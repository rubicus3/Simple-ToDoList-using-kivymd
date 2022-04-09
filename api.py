import db


def get_all_tasks_by_group_id(group_id: int) -> list:
    print(f"returning all tasks with group_id = {group_id}")
    tasks = db.select_tasks_by_group_id(group_id)
    return tasks


def get_all_groups() -> list:
    print("returning all groups")
    groups = db.select_all_groups()
    return groups


def update_task(task_id: int, text: str):
    print(f"updating task's name with task_id = {task_id} to name = {text}")
    db.update_task(task_id, text)


def update_group(group_id: int, name: str):
    print(f"updating group's name with group_id = {group_id} to name = {name}")
    db.update_group(group_id, name)


def delete_task(task_id: int):
    print(f"deleting task with task_id = {task_id}")
    db.delete_task(task_id)


def delete_group(group_id: int):
    print(f"deleting group and all tasks with group_id = {group_id}")
    db.delete_group(group_id)


def create_task(group_id: int, text: str) -> int:
    print(f"creating task with group_id = {group_id} and text = {text}")
    task_id = db.create_task(group_id, text)
    print(f"new task's task_id = {task_id}")
    return task_id


def create_group(name: str) -> int:
    print(f"creating group with name = {name}")
    group_id = db.create_group(name)
    print(f"new group's group_id = {group_id}")
    return group_id


def task_check(task_id: int, is_checked: bool):
    db.task_check(task_id, is_checked)
    if is_checked:
        print(f"task with task_id = {task_id} has been checked")
    else:
        print(f"task with task_id = {task_id} has been unchecked")
