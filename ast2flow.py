import os
import re

node_dict = {}
line_dict = {}
flow_node_dict = {}
flow_line_list = []
node_queue = []
new_node_dict = {}
new_line_list = []
high_light = []
function_names = []
pre_valid_node = None
count = 1
if_count = 1
while_count = 1
switch_count = 1
do_while_count = 1
for_count = 1
else_count = 1
tag = None
pattern_node = r"^\s*\"(?P<id>\d+)\"\s*\[label = <\((?P<type>.*?),(?P<content>.*)\)>\s*]"
pattern_node_sub = r"^\s*\"(?P<id>\d+)\"\s*\[label = <\((?P<type>.*?),(?P<content>.*)\)<SUB>(?P<line>\d+)</SUB>>\s*]"
pattern_line = r"^\s*\"(?P<parent>\d+)\" -> \"(?P<child>\d+)\""
pattern_if = r"if.*?\(.*\),if.*?\(.*\)"
pattern_while = r"while.*?\(.*\),while.*?\(.*\)"
pattern_switch = r"switch.*?\(.*\),switch.*?\(.*\)"
pattern_do_while = r"do.*?\{.*\}.*?while.*?\(.*\);,do.*?\{.*\}.*?while.*?\(.*\);"
pattern_for = r"for.*?\(.*\),for.*?\(.*\)"
pattern_else = r"else,else"
pattern_break = r"break;,break;"
pattern_continue = r"continue;,continue;"


def read_ast(path):
    with open(path, "r") as f:
        dot = f.read()
    dot_list = dot.split("\n")
    for item in dot_list:
        node = re.match(pattern_node_sub, item)
        node_s = re.match(pattern_node, item)
        line = re.match(pattern_line, item)
        if node is not None:
            node_id = node.group("id")
            node_type = node.group("type")
            content = node.group("content")
            line = node.group("line")
            temp_dict = {
                "type": node_type,
                "content": content,
                "line": line
            }
            node_dict[node_id] = temp_dict
        elif node_s is not None:
            node_id = node_s.group("id")
            node_type = node_s.group("type")
            content = node_s.group("content")
            temp_dict = {
                "type": node_type,
                "content": content,
                "line": None
            }
            node_dict[node_id] = temp_dict
        elif line is not None:
            parent = line.group("parent")
            child = line.group("child")
            if parent not in line_dict.keys():
                temp_list = [child, ]
                line_dict[parent] = temp_list
            else:
                line_dict[parent].append(child)


def dfs(key, func, flag, j_flag):
    global count, if_count, while_count, switch_count, do_while_count, for_count, else_count
    children = line_dict[key]
    for child in children:
        node = node_dict[child]
        if node["type"] == "BLOCK":
            dfs(child, func, 0, j_flag)
            if flag < 0:
                node_queue.append({"id": str(-flag),
                                   "type": "CONDITION",
                                   "content": None,
                                   "line": None})
                flag = -flag
        elif node["type"] == "CONTROL_STRUCTURE":
            if_match = re.match(pattern_if, node["content"])
            while_match = re.match(pattern_while, node["content"])
            switch_match = re.match(pattern_switch, node["content"])
            do_while_match = re.match(pattern_do_while, node["content"])
            else_match = re.match(pattern_else, node["content"])
            for_match = re.match(pattern_for, node["content"])
            break_match = re.match(pattern_break, node["content"])
            continue_match = re.match(pattern_continue, node["content"])
            if if_match is not None:
                temp_if_count = if_count
                if_count = if_count + 1
                node_queue.append({"id": str(temp_if_count),
                                   "type": "if_begin",
                                   "content": None,
                                   "line": None})
                dfs(child, func, temp_if_count, 0)
                node_queue.append({"id": str(temp_if_count),
                                   "type": "if_end",
                                   "content": None,
                                   "line": None})
            elif else_match is not None:
                node_queue.append({"id": str(flag),
                                   "type": "else",
                                   "content": str(else_count),
                                   "line": None})
                else_count = else_count + 1
                dfs(child, func, flag, 0)
            elif while_match is not None:
                temp_while_count = while_count
                while_count = while_count + 1
                node_queue.append({"id": str(temp_while_count),
                                   "type": "while_begin",
                                   "content": None,
                                   "line": None})
                dfs(child, func, temp_while_count, 0)
                node_queue.append({"id": str(temp_while_count),
                                   "type": "while_end",
                                   "content": None,
                                   "line": None})
            elif switch_match is not None:
                temp_switch_count = switch_count
                switch_count = switch_count + 1
                node_queue.append({"id": str(temp_switch_count),
                                   "type": "switch_begin",
                                   "content": None,
                                   "line": None})
                dfs(child, func, 0, temp_switch_count)
                node_queue.append({"id": str(temp_switch_count),
                                   "type": "switch_end",
                                   "content": None,
                                   "line": None})
            elif do_while_match is not None:
                temp_do_while_count = do_while_count
                do_while_count = do_while_count + 1
                node_queue.append({"id": str(temp_do_while_count),
                                   "type": "do_while_begin",
                                   "content": None,
                                   "line": None})
                dfs(child, func, temp_do_while_count, 0)
                node_queue.append({"id": str(temp_do_while_count),
                                   "type": "do_while_end",
                                   "content": None,
                                   "line": None})
            elif for_match is not None:
                temp_for_count = for_count
                for_count = for_count + 1
                node_queue.append({"id": str(temp_for_count),
                                   "type": "for_begin",
                                   "content": None,
                                   "line": None})
                dfs(child, func, -temp_for_count, 0)
                node_queue.append({"id": str(temp_for_count),
                                   "type": "for_end",
                                   "content": None,
                                   "line": None})
            elif break_match is not None:
                node_queue.append({"id": func + str(count),
                                   "type": "break",
                                   "content": "break",
                                   "line": node["line"]})
                count = count + 1
            elif continue_match is not None:
                node_queue.append({"id": func + str(count),
                                   "type": "continue",
                                   "content": "continue",
                                   "line": node["line"]})
                count = count + 1
        elif node["type"] == "JUMP_TARGET":
            node_queue.append({"id": str(j_flag),
                               "type": node["content"],
                               "content": None,
                               "line": None})
        elif node["type"] == "RETURN":
            node_queue.append({"id": func + str(count),
                               "type": "return",
                               "content": node["content"],
                               "line": node["line"]})
            count = count + 1
        elif node["type"] == "PARAM":
            node_queue.append({"id": func + str(count),
                               "type": "PARAM",
                               "content": node["content"],
                               "line": node["line"]})
            count = count + 1
        elif node["type"] == "METHOD":
            new_func = node["content"]
            function_names.append(new_func)
            node_queue.append({"id": new_func + str(count),
                               "type": "start",
                               "content": new_func,
                               "line": None})
            count = count + 1
            dfs(child, new_func, 0, 0)
        elif node["type"] == "METHOD_RETURN" and func != "global":
            node_queue.append({"id": func + "0",
                               "type": "end",
                               "content": func + "_end",
                               "line": None})
            count = 1
        elif node["type"] == "LOCAL" and func != "global":
            node_queue.append({"id": func + str(count),
                               "type": "LOCAL",
                               "content": node["content"],
                               "line": node["line"]})
            count = count + 1
        elif func != "global":
            if flag == 0:
                node_queue.append({"id": func + str(count),
                                   "type": "operation",
                                   "content": node["content"],
                                   "line": node["line"]})
            else:
                node_queue.append({"id": func + str(count),
                                   "type": "CONDITION",
                                   "content": node["content"],
                                   "line": node["line"]})
            count = count + 1


def array_node(func):
    keys = line_dict.keys()
    head = list(keys)[0]
    global count
    dfs(head, func, 0, 0)


def break_handle(index, n):
    global tag, pre_valid_node
    i = 0
    circle_stake = []
    while i < index:
        node = node_queue[i]
        id = node["id"]
        type = node["type"]
        if type == "while_begin" or type == "do_while_begin" or type == "for_begin" or type == "switch_begin":
            circle_stake.append(i)
        elif type == "while_end" or type == "do_while_end" or type == "for_end" or type == "switch_end":
            circle_stake.pop()
        i = i + 1
    record = len(circle_stake)
    i = index + 1
    while i < n:
        node = node_queue[i]
        id = node["id"]
        type = node["type"]
        if type == "while_begin" or type == "do_while_begin" or type == "for_begin" or type == "switch_begin":
            circle_stake.append(i)
        elif type == "while_end" or type == "do_while_end" or type == "for_end" or type == "switch_end":
            circle_stake.pop()
            if len(circle_stake) < record:
                new_line_list.append({"parent": pre_valid_node,
                                      "child": type + id,
                                      "label": tag,
                                      "style": None})
                pre_valid_node = None
                tag = None
                break
        i = i + 1


def continue_handle(index, n):
    global tag, pre_valid_node
    i = 0
    circle_stake = []
    while i < index:
        node = node_queue[i]
        id = node["id"]
        type = node["type"]
        if type == "while_begin" or type == "do_while_begin" or type == "for_begin":
            circle_stake.append(i)
        elif type == "while_end" or type == "do_while_end" or type == "for_end":
            circle_stake.pop()
        i = i + 1
    i = circle_stake[len(circle_stake) - 1]
    node = node_queue[i]
    circle_id = node["id"]
    type = node["type"]
    if type == "while_begin":
        node = node_queue[i + 1]
        id = node["id"]
        new_line_list.append({"parent": pre_valid_node,
                              "child": id,
                              "label": tag,
                              "style": None})
        pre_valid_node = None
        tag = None
    elif type == "for_begin":
        i = i + 1
        while i < n:
            node = node_queue[i]
            id = node["id"]
            type = node["type"]
            if type == "CONDITION":
                new_line_list.append({"parent": pre_valid_node,
                                      "child": id,
                                      "label": tag,
                                      "style": None})
                pre_valid_node = None
                tag = None
                break
            i = i + 1
    else:
        i = i + 1
        while i < n:
            node = node_queue[i]
            id = node["id"]
            type = node["type"]
            if type == "do_while_end" and circle_id == id:
                node = node_queue[i - 1]
                id = node["id"]
                new_line_list.append({"parent": pre_valid_node,
                                      "child": id,
                                      "label": tag,
                                      "style": None})
                pre_valid_node = None
                tag = None
                break
            i = i + 1


def if_handle(index, n, flag):
    global tag, pre_valid_node
    i = index - 1
    while i >= 0:
        node = node_queue[i]
        id = node["id"]
        type = node["type"]
        if type == "if_begin" and id == flag:
            node = node_queue[i + 1]
            id = node["id"]
            pre_valid_node = id
            tag = "N"
            break
        elif type == "else" and id == flag:
            pre_valid_node = None
            tag = None
            break
        i = i - 1


def else_handle(index, n, flag):
    global tag, pre_valid_node
    i = index + 1
    while i < n:
        node = node_queue[i]
        id = node["id"]
        type = node["type"]
        if id == flag and type == "if_end":
            new_line_list.append({"parent": pre_valid_node,
                                  "child": type + id,
                                  "label": tag,
                                  "style": None})
            tag = None
            break
        i = i + 1
    i = index - 1
    while i >= 0:
        node = node_queue[i]
        id = node["id"]
        type = node["type"]
        if type == "if_begin" and id == flag:
            node = node_queue[i + 1]
            id = node["id"]
            pre_valid_node = id
            tag = "N"
            break
        i = i - 1


def while_handle(index, n, flag):
    global tag, pre_valid_node
    i = index - 1
    while i >= 0:
        node = node_queue[i]
        id = node["id"]
        type = node["type"]
        if type == "while_begin" and id == flag:
            node = node_queue[i + 1]
            id = node["id"]
            new_line_list.append({"parent": pre_valid_node,
                                  "child": id,
                                  "label": tag,
                                  "style": None})
            pre_valid_node = id
            tag = "N"
            break
        i = i - 1


def for_handle(index, n, flag):
    global tag, pre_valid_node
    i = index - 1
    while i >= 0:
        node = node_queue[i]
        id = node["id"]
        type = node["type"]
        if type == "for_begin" and id == flag:
            i = i + 1
            while i < n:
                node = node_queue[i]
                id = node["id"]
                type = node["type"]
                if type == "CONDITION":
                    new_line_list.append({"parent": pre_valid_node,
                                          "child": id,
                                          "label": tag,
                                          "style": None})
                    pre_valid_node = id
                    tag = "N"
                    break
                i = i + 1
            break
        i = i - 1


def do_while_handle(index, n, flag):
    global tag, pre_valid_node
    i = index - 1
    while i >= 0:
        node = node_queue[i]
        id = node["id"]
        type = node["type"]
        if type == "do_while_begin" and id == flag:
            node = node_queue[i + 1]
            id = node["id"]
            new_line_list.append({"parent": pre_valid_node,
                                  "child": id,
                                  "label": tag,
                                  "style": None})
            tag = "N"
            break
        i = i - 1


def switch_handle(index, n, flag):
    global tag, pre_valid_node
    i = index - 1
    while i >= 0:
        node = node_queue[i]
        id = node["id"]
        type = node["type"]
        if type == "case" and id == flag:
            i = i + 1
            node = node_queue[i]
            id = node["id"]
            pre_valid_node = id
            tag = "N"
            break
        elif type == "default" and id == flag:
            pre_valid_node = None
            tag = None
            break
        i = i - 1


def case_handle(index, n, flag, case_node):
    global tag, pre_valid_node
    i = index - 1
    while i >= 0:
        node = node_queue[i]
        id = node["id"]
        type = node["type"]
        if type == "switch_begin" and id == flag:
            new_line_list.append({"parent": pre_valid_node,
                                  "child": case_node,
                                  "label": tag,
                                  "style": None})
            tag = None
            break
        elif type == "case" and id == flag:
            i = i + 1
            node = node_queue[i]
            id = node["id"]
            new_line_list.append({"parent": id,
                                  "child": case_node,
                                  "label": "N",
                                  "style": None})
            i = index + 2
            while i < n:
                node = node_queue[i]
                id = node["id"]
                type = node["type"]
                if type == "case":
                    i = i + 1
                elif type == "operation" or type == "break":
                    new_line_list.append({"parent": pre_valid_node,
                                          "child": id,
                                          "label": tag,
                                          "style": None})
                    tag = None
                    break
                elif type == "if_begin" or type == "while_begin" or type == "do_while_begin" \
                    or type == "for_begin" or type == "switch_begin":
                    new_line_list.append({"parent": pre_valid_node,
                                          "child": type + id,
                                          "label": tag,
                                          "style": None})
                    tag = None
                    break
                elif type == "switch_end" and id == flag:
                    new_line_list.append({"parent": pre_valid_node,
                                          "child": type + id,
                                          "label": tag,
                                          "style": None})
                    tag = None
                    break
                i = i + 1
            break
        i = i - 1


def default_handle(index, n, flag):
    global tag, pre_valid_node
    i = index - 1
    temp_parent = None
    while i >= 0:
        node = node_queue[i]
        id = node["id"]
        type = node["type"]
        if type == "switch_begin" and id == flag:
            break
        elif type == "case" and id == flag:
            i = i + 1
            node = node_queue[i]
            id = node["id"]
            temp_parent = id
            break
        i = i - 1
    i = index + 1
    node = node_queue[i]
    id = node["id"]
    type = node["type"]
    if type == "operation" or type == "break":
        new_line_list.append({"parent": pre_valid_node,
                              "child": id,
                              "label": tag,
                              "style": None})
        if temp_parent is not None:
            new_line_list.append({"parent": temp_parent,
                                  "child": id,
                                  "label": "N",
                                  "style": None})
        tag = None
    elif type == "if_begin" or type == "while_begin" or type == "do_while_begin" \
            or type == "for_begin" or type == "switch_begin":
        new_line_list.append({"parent": pre_valid_node,
                              "child": type + id,
                              "label": tag,
                              "style": None})
        if temp_parent is not None:
            new_line_list.append({"parent": temp_parent,
                                  "child": type + id,
                                  "label": "N",
                                  "style": None})
        tag = None


def generate_flow():
    n = len(node_queue)
    i = 0
    global pre_valid_node, tag
    for_cond = False
    temp_cond = {"id": "",
                 "content": ""}
    func = None
    while i < n:
        node = node_queue[i]
        id = node["id"]
        type = node["type"]
        content = node["content"]
        line = node["line"]
        if type == "start":
            pre_valid_node = id
            new_node_dict[id] = {"label": content,
                                 "type": type,
                                 "style": "shape = circle, style = bold, color = green,"}
            func = content
            tag = None
        elif type == "PARAM":
            temp_label = "{" + "param: " + content
            temp_style = "shape = record,"
            marked = False
            if line in high_light:
                temp_style = temp_style + "style = filled, fillcolor = yellow,"
                marked = True
            j = i + 1
            while j < n:
                new_node = node_queue[j]
                j_type = new_node["type"]
                j_content = new_node["content"]
                j_line = new_node["line"]
                if j_type != "PARAM":
                    break
                else:
                    temp_label = temp_label + "|" + "param: " + j_content
                    if j_line in high_light and not marked:
                        temp_style = temp_style + "style = filled, fillcolor = yellow,"
                        marked = True
                j = j + 1
            i = j - 1
            new_node_dict[id] = {"label": temp_label + "}",
                                 "type": type,
                                 "style": temp_style}
            new_line_list.append({"parent": pre_valid_node,
                                  "child": id,
                                  "label": tag,
                                  "style": None})
            pre_valid_node = id
            tag = None
        elif type == "LOCAL":
            temp_label = "{" + content
            temp_style = "shape = record,"
            marked = False
            if line in high_light:
                temp_style = temp_style + "style = filled, fillcolor = yellow,"
                marked = True
            j = i + 1
            while j < n:
                new_node = node_queue[j]
                j_type = new_node["type"]
                j_content = new_node["content"]
                j_line = new_node["line"]
                if j_type != "LOCAL":
                    break
                else:
                    temp_label = temp_label + "|" + j_content
                    if j_line in high_light and not marked:
                        temp_style = temp_style + "style = filled, fillcolor = yellow,"
                        marked = True
                j = j + 1
            i = j - 1
            new_node_dict[id] = {"label": temp_label + "}",
                                 "type": type,
                                 "style": temp_style}
            new_line_list.append({"parent": pre_valid_node,
                                  "child": id,
                                  "label": tag,
                                  "style": None})
            pre_valid_node = id
            tag = None
        elif type == "operation":
            node_style = None
            if line in high_light:
                node_style = ""
                node_style = node_style + "style = filled, fillcolor = yellow,"
            new_node_dict[id] = {"label": content,
                                 "type": type,
                                 "style": node_style}
            new_line_list.append({"parent": pre_valid_node,
                                  "child": id,
                                  "label": tag,
                                  "style": None})
            pre_valid_node = id
            tag = None
        elif type == "if_begin" or type == "while_begin" or type == "do_while_begin" \
                or type == "for_begin" or type == "switch_begin":
            new_node_dict[type + id] = {"label": type + ": " + id,
                                        "type": type,
                                        "style": "shape = box, style = dashed, color = blue"}
            new_line_list.append({"parent": pre_valid_node,
                                  "child": type + id,
                                  "label": tag,
                                  "style": None})
            pre_valid_node = type + id
            tag = None
        elif type == "CONDITION":
            if content is None:
                for_cond = True
                temp_cond["id"] = id
                temp_cond["content"] = ""
            if not for_cond:
                node_style = "shape = diamond,"
                if line in high_light:
                    node_style = node_style + "style = filled, fillcolor = yellow,"
                new_node_dict[id] = {"label": content,
                                     "type": type,
                                     "style": node_style}
                new_line_list.append({"parent": pre_valid_node,
                                      "child": id,
                                      "label": tag,
                                      "style": None})
                pre_valid_node = id
                tag = "Y"
            else:
                if content is not None:
                    temp_cond["content"] = temp_cond["content"] + content + ";"
                if node_queue[i + 1]["type"] != "CONDITION":
                    node_style = "shape = diamond,"
                    if line in high_light:
                        node_style = node_style + "style = filled, fillcolor = yellow,"
                    for_cond = False
                    new_node_dict[temp_cond["id"]] = {"label": temp_cond["content"],
                                                      "type": "CONDITION",
                                                      "style": node_style}
                    new_line_list.append({"parent": pre_valid_node,
                                          "child": temp_cond["id"],
                                          "label": tag,
                                          "style": None})
                    pre_valid_node = temp_cond["id"]
                    tag = "Y"
        elif type == "else":
            new_node_dict[id + type + content] = {"label": type + ": " + id,
                                                  "type": type,
                                                  "style": "shape = box, style = dashed, color = blue"}
            else_handle(i, n, id)
            new_line_list.append({"parent": pre_valid_node,
                                  "child": id + type + content,
                                  "label": tag,
                                  "style": None})
            pre_valid_node = id + type + content
            tag = None
        elif type == "if_end":
            new_node_dict[type + id] = {"label": type + ": " + id,
                                        "type": type,
                                        "style": "shape = box, style = dashed, color = blue"}
            new_line_list.append({"parent": pre_valid_node,
                                  "child": type + id,
                                  "label": tag,
                                  "style": None})
            if_handle(i, n, id)
            if pre_valid_node is not None:
                new_line_list.append({"parent": pre_valid_node,
                                      "child": type + id,
                                      "label": tag,
                                      "style": None})
            pre_valid_node = type + id
            tag = None
        elif type == "while_end":
            new_node_dict[type + id] = {"label": type + ": " + id,
                                        "type": type,
                                        "style": "shape = box, style = dashed, color = blue"}
            while_handle(i, n, id)
            new_line_list.append({"parent": pre_valid_node,
                                  "child": type + id,
                                  "label": tag,
                                  "style": None})
            pre_valid_node = type + id
            tag = None
        elif type == "do_while_end":
            new_node_dict[type + id] = {"label": type + ": " + id,
                                        "type": type,
                                        "style": "shape = box, style = dashed, color = blue"}
            do_while_handle(i, n, id)
            new_line_list.append({"parent": pre_valid_node,
                                  "child": type + id,
                                  "label": tag,
                                  "style": None})
            pre_valid_node = type + id
            tag = None
        elif type == "for_end":
            new_node_dict[type + id] = {"label": type + ": " + id,
                                        "type": type,
                                        "style": "shape = box, style = dashed, color = blue"}
            for_handle(i, n, id)
            new_line_list.append({"parent": pre_valid_node,
                                  "child": type + id,
                                  "label": tag,
                                  "style": None})
            pre_valid_node = type + id
            tag = None
        elif type == "case":
            i = i + 1
            case_cond = node_queue[i]
            new_id = case_cond["id"]
            new_content = case_cond["content"]
            new_line = case_cond["line"]
            node_style = "shape = diamond,"
            if new_line in high_light:
                node_style = node_style + "style = filled, fillcolor = yellow,"
            new_node_dict[new_id] = {"label": "case: " + new_content,
                                 "type": "CONDITION",
                                 "style": node_style}
            case_handle(i - 1, n, id, new_id)
            pre_valid_node = new_id
            tag = "Y"
        elif type == "default":
            i = i + 1
            case_cond = node_queue[i]
            new_type = case_cond["type"]
            if new_type == "switch_end":
                i = i - 1
            else:
                default_handle(i - 1, n, id)
                i = i - 1
                pre_valid_node = None
        elif type == "switch_end":
            new_node_dict[type + id] = {"label": type + ": " + id,
                                        "type": type,
                                        "style": "shape = box, style = dashed, color = blue"}
            new_line_list.append({"parent": pre_valid_node,
                                  "child": type + id,
                                  "label": tag,
                                  "style": None})
            switch_handle(i, n, id)
            if pre_valid_node is not None:
                new_line_list.append({"parent": pre_valid_node,
                                      "child": type + id,
                                      "label": tag,
                                      "style": None})
            pre_valid_node = type + id
            tag = None
        elif type == "break":
            node_style = None
            if line in high_light:
                node_style = ""
                node_style = node_style + "style = filled, fillcolor = yellow,"
            new_node_dict[id] = {"label": content,
                                 "type": type,
                                 "style": node_style}
            new_line_list.append({"parent": pre_valid_node,
                                  "child": id,
                                  "label": tag,
                                  "style": None})
            pre_valid_node = id
            tag = None
            break_handle(i, n)
        elif type == "continue":
            node_style = None
            if line in high_light:
                node_style = ""
                node_style = node_style + "style = filled, fillcolor = yellow,"
            new_node_dict[id] = {"label": content,
                                 "type": type,
                                 "style": node_style}
            new_line_list.append({"parent": pre_valid_node,
                                  "child": id,
                                  "label": tag,
                                  "style": None})
            pre_valid_node = id
            tag = None
            continue_handle(i, n)
        elif type == "return":
            new_node_dict[id] = {"label": content,
                                 "type": type,
                                 "style": None}
            new_line_list.append({"parent": pre_valid_node,
                                  "child": id,
                                  "label": tag,
                                  "style": None})
            new_line_list.append({"parent": id,
                                  "child": func + "0",
                                  "label": tag,
                                  "style": None})
            pre_valid_node = None
            tag = None
        elif type == "end":
            new_node_dict[id] = {"label": content,
                                 "type": type,
                                 "style": "shape = circle, style = bold, color = red,"}
            new_line_list.append({"parent": pre_valid_node,
                                  "child": id,
                                  "label": tag,
                                  "style": None})
            pre_valid_node = None
            tag = None
            clear()
            # hide_struct()
            generate_dot(func)
        i = i + 1


def clear():
    copy_line = new_line_list
    for item in copy_line:
        if item["parent"] is None:
            new_line_list.remove(item)
    total_list = []
    for key in new_node_dict.keys():
        total_list.append(key)
    record = -1
    n = len(total_list)
    while n != record:
        record = n
        copy_line = new_line_list
        copy_total = total_list
        reserve_list = [total_list[0], ]
        delete_list = []
        for item in copy_line:
            if item["child"] not in reserve_list:
                reserve_list.append(item["child"])
        for item in copy_total:
            if item not in reserve_list:
                total_list.remove(item)
                new_node_dict.pop(item)
                delete_list.append(item)
        n = len(total_list)
        for item in copy_line:
            if item["parent"] in delete_list:
                new_line_list.remove(item)


def hide_struct():
    global new_node_dict, new_line_list
    delete_node_list = []
    for key, value in new_node_dict.items():
        type = value["type"]
        if type == "if_begin" or type == "if_end" or type == "for_begin" \
            or type == "for_end" or type == "while_begin" or type == "while_end" \
            or type == "do_while_begin" or type == "do_while_end" \
            or type == "switch_begin" or type == "switch_end" or type == "else":
            print(key)
            print(type)
            delete_node_list.append(key)
            parent = []
            child = []
            delete_line_list = []
            copy_line_list = new_line_list
            for item in copy_line_list:
                if item["parent"] == key:
                    print("1")
                    print(item)
                    delete_line_list.append(item)
                    child.append(item["child"])
                elif item["child"] == key:
                    print(item)
                    delete_line_list.append(item)
                    parent.append({"id": item["parent"],
                                   "label": item["label"]})
            for line in delete_line_list:
                new_line_list.remove(line)
            for p in parent:
                for c in child:
                    new_line_list.append({"parent": p["id"],
                                          "child": c,
                                          "label": p["label"],
                                          "style": None})
    for id in delete_node_list:
        new_node_dict.pop(id)


def generate_dot(func):
    path = "./flow_" + func + ".dot"
    global new_node_dict, new_line_list
    with open(path, "w") as f:
        f.write("digraph {\n")
        for key, value in new_node_dict.items():
            code = "\"" + key + "\" ["
            if value["style"] is not None:
                code = code + value["style"]
            code = code + " label = <" + value["label"] + ">]\n"
            f.write(code)
        for item in new_line_list:
            code = "\"" + item["parent"] + "\"" + " -> " + "\"" + item["child"] + "\""
            if item["style"] is not None or item["label"] is not None:
                code = code + " ["
                if item["style"] is not None:
                    code = code + item["style"]
                if item["label"] is not None:
                    code = code + " label = <" + item["label"] + ">]"
            code = code + "\n"
            f.write(code)
        f.write("}\n")
    f.close()
    flow_node_dict[func] = new_node_dict
    flow_line_list.extend(new_line_list)
    new_node_dict = {}
    new_line_list = []


def mark_line():
    with open("./error_line.txt", "r") as f:
        error_lines = f.readlines()
        for row in error_lines:
            row = row.strip()
            high_light.append(row)
    f.close()


# def initiate():
#     global node_dict, line_dict, node_queue, new_node_dict, new_line_list, \
#         pre_valid_node, count, if_count, while_count, switch_count, do_while_count, \
#         for_count, else_count, tag
#     node_dict = {}
#     line_dict = {}
#     node_queue = []
#     new_node_dict = {}
#     new_line_list = []
#     pre_valid_node = None
#     count = 1
#     if_count = 1
#     while_count = 1
#     switch_count = 1
#     do_while_count = 1
#     for_count = 1
#     else_count = 1
#     tag = None


def call_analysis():
    for fun, dic in flow_node_dict.items():
        for key, value in dic.items():
            label = value["label"]
            for c_func in function_names:
                pattern_call = r"(?:.*\W|\s*)" + c_func + r"\(.*?\)"
                call = re.match(pattern_call, label)
                if call is not None:
                    flow_line_list.append({"parent": key,
                                           "child": c_func + "1",
                                           "label": "call",
                                           "style": "color = red"})
                    flow_line_list.append({"parent": c_func + "0",
                                           "child": key,
                                           "label": "return",
                                           "style": "color = blue"})


def assemble_flow():
    with open("./output.dot", "w") as f:
        f.write("digraph {\n")
        for fun, dic in flow_node_dict.items():
            f.write("subgraph cluster_" + fun + " {\n")
            for key, value in dic.items():
                code = "\"" + key + "\" ["
                if value["style"] is not None:
                    code = code + value["style"]
                code = code + " label = <" + value["label"] + ">]\n"
                f.write(code)
            f.write("}\n")
        for item in flow_line_list:
            code = "\"" + item["parent"] + "\"" + " -> " + "\"" + item["child"] + "\""
            if item["style"] is not None or item["label"] is not None:
                code = code + " ["
                if item["style"] is not None:
                    code = code + item["style"]
                if item["label"] is not None:
                    code = code + " label = <" + item["label"] + ">]"
            code = code + "\n"
            f.write(code)
        f.write("}\n")
    f.close()


def get_ast():
    cpg_name = input()
    source_code = input()
    path = input()
    os.system("cd ~/bin/joern/joern-cli/")
    os.system("./joern-parse -o " + cpg_name + " " + source_code)
    os.system("./joern-export -o " + path + " --repr=ast --format=dot " + cpg_name)


if __name__ == '__main__':
    mark_line()
    read_ast("./temp/0-ast.dot")
    array_node("global")
    generate_flow()
    call_analysis()
    assemble_flow()







