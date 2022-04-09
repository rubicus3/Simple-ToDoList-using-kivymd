import api

from kivy import Config
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SwapTransition
from kivymd.app import MDApp
from kivymd.uix.behaviors import TouchBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem, CheckboxLeftWidget, OneLineAvatarIconListItem
from kivymd.uix.screen import MDScreen

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Window.size = (480, 720)
Window.minimum_width = 480
Window.minimum_height = 720


# ------------------------------------------------------------------------------------------------------------------- #


class Dialog(MDBoxLayout):
    def __init__(self, text: str, **kwargs):
        super().__init__(**kwargs)
        self.ids["TextField"].text = text
        self.ids["TextField"].multiline = False


# ------------------------------------------------------------------------------------------------------------------- #


class LeftCheckbox(CheckboxLeftWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(active=self.callback)

    def callback(self, instance, value):
        if value:
            self.parent.parent.markup = True
            self.parent.parent.text = f"[color=#999999][s]{self.parent.parent.real_text}[/s][/color]"
            self.parent.parent.is_checked = True
        else:
            self.parent.parent.markup = False
            self.parent.parent.text = self.parent.parent.real_text
            self.parent.parent.is_checked = False
        api.task_check(self.parent.parent.task_id, self.parent.parent.is_checked)


# ------------------------------------------------------------------------------------------------------------------- #


class TaskItem(OneLineAvatarIconListItem, TouchBehavior):
    def __init__(self, text: str, task_id: int, is_checked=False):
        super().__init__()
        self.task_id = task_id
        self.real_text = text
        self.text = self.real_text
        self.is_checked = is_checked
        self.ids["TaskCheckBox"].active = is_checked

        self.dialog = None
        self.markup = False

    def on_release(self):
        self.dialog = MDDialog(
            title=f"Edit Task",
            type="custom",
            content_cls=Dialog(text=self.real_text),
            buttons=[
                MDFlatButton(text="CANCEL", on_press=self.dialog_cancel),
                MDFlatButton(text="DELETE", on_press=self.dialog_delete_task),
                MDFlatButton(text="SAVE", on_press=self.dialog_update_task)
            ],
        )
        self.dialog.open()

    def dialog_update_task(self, obj):
        self.real_text = self.dialog.content_cls.ids["TextField"].text
        if self.real_text == "":
            self.real_text = "NoName"
        if self.markup:
            self.text = f"[s]{self.real_text}[/s]"
        else:
            self.text = self.real_text

        api.update_task(self.task_id, self.real_text)

        self.dialog.dismiss()

    def dialog_delete_task(self, obj):
        api.delete_task(self.task_id)
        self.parent.remove_widget(self)
        self.dialog.dismiss()

    def dialog_cancel(self, obj):
        self.dialog.dismiss()


# ------------------------------------------------------------------------------------------------------------------- #


class GroupItem(OneLineListItem, TouchBehavior):
    def __init__(self, group_name: str, group_id: int):
        super().__init__()
        self.group_id = group_id
        self.text = group_name
        self.dialog = None

    def on_long_touch(self, touch, *args):
        self.dialog = MDDialog(
            title="Edit Group",
            type="custom",
            content_cls=Dialog(text=self.text),
            buttons=[
                MDFlatButton(text="CANCEL", on_press=self.dialog_cancel),
                MDFlatButton(text="DELETE", on_press=self.dialog_delete_group),
                MDFlatButton(text="SAVE", on_press=self.dialog_update_group)
            ],
        )
        self.dialog.open()

    def dialog_update_group(self, obj):
        name = self.dialog.content_cls.ids["TextField"].text
        if name == "":
            name = "NoName"

        api.update_group(self.group_id, name)

        self.text = name

        self.parent.parent.parent.parent.parent.parent.toolbar_update()
        self.dialog.dismiss()

    def dialog_delete_group(self, obj):
        if len(self.parent.children) == 1:
            print("Can't delete single one group")
        else:
            if self.group_id == self.parent.parent.parent.parent.parent.parent.current_group_id:
                self.parent.parent.parent.parent.parent.parent.fill_tasks(self.parent.children[-1].group_id)

            api.delete_group(self.group_id)

            self.parent.remove_widget(self)
            self.dialog.dismiss()

    def dialog_cancel(self, obj):
        self.dialog.dismiss()


# ------------------------------------------------------------------------------------------------------------------- #


class ToDoList(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.dialog = None
        self.fill_groups()

        self.current_group_id = self.ids["GroupList"].children[-1].group_id
        self.fill_tasks(self.current_group_id)

    def fill_groups(self):
        groups = api.get_all_groups()
        if len(groups) == 0:
            group_id = api.create_group("NoName")
            self.ids["GroupList"].add_widget(GroupItem("NoName", group_id))
        else:
            for group in groups:
                self.ids["GroupList"].add_widget(GroupItem(group[1], group[0]))

    def fill_tasks(self, group_id: int):
        tasks = api.get_all_tasks_by_group_id(group_id)

        self.ids["TaskList"].clear_widgets()
        self.current_group_id = group_id
        if len(tasks) > 0:
            for task in tasks:
                self.ids["TaskList"].add_widget(TaskItem(task[0], task[1], bool(task[2])))

        self.ids["nav_drawer"].set_state("close")
        self.toolbar_update()

    def add_group(self):
        self.dialog = MDDialog(
            title="Create Group",
            type="custom",
            content_cls=Dialog(text=""),
            buttons=[
                MDFlatButton(text="CANCEL", on_press=self.dialog_cancel),
                MDFlatButton(text="CREATE", on_press=self.dialog_create_group)
            ],
        )
        self.dialog.open()

    def add_task(self):
        self.dialog = MDDialog(
            title="Tasks Creation",
            type="custom",
            content_cls=Dialog(text=""),
            buttons=[
                MDFlatButton(text="CREATE", on_press=self.dialog_create_task),
                MDFlatButton(text="EXIT", on_press=self.dialog_cancel)
            ],
        )
        self.dialog.open()

    def dialog_create_task(self, obj):
        name = self.dialog.content_cls.ids["TextField"].text
        if name == "":
            name = "NoName"

        task_id = api.create_task(self.current_group_id, name)

        self.ids["TaskList"].add_widget(TaskItem(name, task_id))
        self.dialog.content_cls.ids["TextField"].text = ""

    def dialog_create_group(self, obj):
        name = self.dialog.content_cls.ids["TextField"].text
        if name == "":
            name = "NoName"

        group_id = api.create_group(name)

        self.ids["GroupList"].add_widget(GroupItem(name, group_id))
        self.dialog.dismiss()

    def dialog_cancel(self, obj):
        self.dialog.dismiss()

    def toolbar_update(self):
        for group in self.ids["GroupList"].children:
            if group.group_id == self.current_group_id:
                self.ids["ToolBar"].title = group.text


# ------------------------------------------------------------------------------------------------------------------- #


class Container(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = SwapTransition()
        self.add_widget(ToDoList(name="ToDoList"))


# ------------------------------------------------------------------------------------------------------------------- #


class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.accent_palette = "BlueGray"
        return Container()


if __name__ == '__main__':
    MainApp().run()
