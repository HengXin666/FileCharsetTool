"""
/*
 * Copyright Heng_Xin. All rights reserved.
 *
 * @Author: Heng_Xin
 * @Date: 2024-5-26 16:50:58
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *	  https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * */
"""

import os
import chardet
import tkinter as tk
from tkinter import ttk

# 设置读取文件的最大字节数
MAX_LOOK_BYTES = 1024 # 1024 字节

# 支持的编码列表
ENCODINGS = ["utf-8", "gbk", "utf-8-sig", "gb2312", "ascii"]

def convert_encoding():
    # 获取选中的文件列表
    selected_items = tree.selection()
    if not selected_items:
        tk.messagebox.showwarning("Warning", "No files selected.")
        return

    # 获取选中的编码
    selected_encoding = combo_encoding.get()

    for item in selected_items:
        # 获取项目的文本（文件名）
        file_name = tree.item(item, 'text')
        # 获取项目的父节点（文件夹）
        parent_item = tree.parent(item)
        # 初始化文件路径为文件名
        file_path = file_name
        # 逐级向上获取文件路径，直到根目录为止
        while parent_item:
            # 获取父节点的文本（文件夹名）
            parent_name = tree.item(parent_item, 'text')
            # 在父文件夹名和当前文件路径之间添加路径分隔符构建完整路径
            file_path = os.path.join(parent_name, file_path)
            # 获取父节点的父节点
            parent_item = tree.parent(parent_item)
        # 在根目录前添加当前路径以构建完整的文件路径
        file_path = os.path.join(current_path, file_path)

        try:
            detected_encoding = detect_encoding(file_path)

            # 读取文件内容并根据检测到的编码进行解码
            with open(file_path, 'r', encoding=detected_encoding, errors='replace') as f:
                content = f.read()

            # 使用所选的目标编码进行编码并保存文件
            with open(file_path, 'w', encoding=selected_encoding, errors='replace') as f:
                f.write(content)

        except FileNotFoundError:
            error_message = f"Failed to convert {file_path}: File not found."
            print(error_message)  # 打印详细的错误信息到控制台
            tk.messagebox.showerror("Error", error_message)

        except Exception as e:
            error_message = f"Failed to convert {file_path}: {str(e)}"
            print(error_message)  # 打印详细的错误信息到控制台
            tk.messagebox.showerror("Error", error_message)
        # print(f"修改 {file_path} 从 {detected_encoding} 到 {selected_encoding} 成功!")
        
        tree.item(item, values=(f"{detect_encoding(file_path)} ({os.path.getsize(file_path) // 1024} k)",))

def populate_tree(path, parent):
    folders = []
    files = []

    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            folders.append(item)
        else:
            files.append(item)

    for folder in sorted(folders):
        node = tree.insert(parent, 'end', text=folder, open=False, values=('',))
        tree.insert(node, 'end', text='dummy')

    for file in sorted(files):
        file_path = os.path.join(path, file)
        file = os.path.basename(file_path)
        file_encoding = f"{detect_encoding(file_path)} ({os.path.getsize(file_path) // 1024} k)"
        tree.insert(parent, 'end', text=file, values=(file_encoding,))


def detect_encoding(file_path):
    # 使用chardet库检测文件编码
    with open(file_path, 'rb') as f:
        # 读取文件的开头部分内容
        raw_data = f.read(MAX_LOOK_BYTES)
    result = chardet.detect(raw_data)
    return result['encoding']

def on_expand(event):
    # 获取展开的节点ID
    item_id = event.widget.focus()
    # 获取节点的绝对路径
    item_path = tree.item(item_id, 'text')
    parent_path = get_parent_path(item_id)
    full_path = os.path.join(parent_path, item_path)
    # 清除该节点的所有子节点
    tree.delete(*tree.get_children(item_id))
    # 重新加载该节点的内容
    populate_tree(full_path, item_id)

def get_parent_path(item_id):
    # 获取节点的父节点ID
    parent_id = tree.parent(item_id)
    if parent_id:
        # 如果存在父节点，递归获取父节点的路径
        parent_path = get_parent_path(parent_id)
        # 获取父节点的文本内容，即文件夹名
        parent_text = tree.item(parent_id, 'text')
        # 返回拼接后的父路径
        return os.path.join(parent_path, parent_text)
    else:
        # 如果不存在父节点，说明当前节点为根节点，返回当前路径
        return current_path

def go_to_path():
    global current_path
    # 获取路径框中的路径
    path = entry_path.get()
    # 检查路径是否存在
    if os.path.exists(path):
        # 更新当前路径
        current_path = path
        # 清空树形结构
        tree.delete(*tree.get_children())
        # 加载新路径的内容
        populate_tree(path, '')
    else:
        # 如果路径不存在，显示错误信息
        tk.messagebox.showerror("Error", "Path does not exist.")

if __name__ == "__main__":
    # 创建主窗口
    root = tk.Tk()
    root.title("HX File Manager [V 1.0.0]")
    root.geometry("800x600")
    # 设置软件图标
    root.iconbitmap("./icon/app.ico")
    # 获取当前路径
    current_path = os.getcwd()

    # 添加路径框
    frame_path = ttk.Frame(root)
    frame_path.pack(fill="x")

    label_path = ttk.Label(frame_path, text="Path:")
    label_path.pack(side="left")

    entry_path = ttk.Entry(frame_path, width=50)
    entry_path.insert(0, current_path)
    entry_path.pack(side="left", padx=5)

    btn_go_to_path = ttk.Button(frame_path, text="Go", command=go_to_path)
    btn_go_to_path.pack(side="left")

    # 创建一个Treeview控件
    tree = ttk.Treeview(root, columns=('Encoding'))
    tree.heading('#0', text='Name')
    tree.heading('#1', text='Encoding')
    tree.pack(fill="both", expand=True)

    # 加载当前路径的内容
    populate_tree(current_path, '')

    # 绑定事件，展开时动态加载子节点
    tree.bind('<<TreeviewOpen>>', on_expand)

    # 添加编码选择框和按钮
    frame_convert = ttk.Frame(root)
    frame_convert.pack(fill="x")

    label_encoding = ttk.Label(frame_convert, text="Encoding:")
    label_encoding.pack(side="left")

    combo_encoding = ttk.Combobox(frame_convert, values=ENCODINGS, width=10)
    combo_encoding.pack(side="left")

    btn_convert = ttk.Button(frame_convert, text="Convert Encoding", command=convert_encoding)
    btn_convert.pack(side="left")

    # 创建滚动条
    vsb = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
    vsb.pack(side="right", fill="y")
    tree.configure(yscrollcommand=vsb.set)

    root.mainloop()