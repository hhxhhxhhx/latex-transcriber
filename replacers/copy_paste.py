
def replace(lines):
    """
    COPY
    """
    copy_dict = {}
    copy_label = None
    copied_text = []
    index = 0
    while index < len(lines) - 1:
        if lines[index].startswith('..begin copy'):
            if not lines[index][13:].strip():
                print("..begin copy requires 1 argument. Read documentation if necessary")
                exit(1)
            copy_label = lines[index][13:].strip()
            if copy_label in copy_dict:
                print("Warning, copy label \"{0}\" is used multiple times. Unintended behavior may occur. The last \"..begin copy {0}\" will override all previous labels.".format(copy_label))
            lines.pop(index)
            continue
        elif lines[index].startswith('..end copy'):
            copy_dict[copy_label] = copied_text
            copy_label = None
            copied_text = []
            lines.pop(index)
            continue
        elif copy_label:
            copied_text.append(lines[index])
        index += 1

    """
    PASTE
    """
    index = 0
    while index < len(lines) - 1:
        if lines[index].startswith('..paste'):
            if not lines[index][8:].strip():
                print("..paste requires 1 argument. Read documentation if necessary")
                exit(1)
            label = lines[index][8:].strip()
            try:
                lines[index:index + 1] = copy_dict[label]
                index += len(copy_dict[label]) - 1
            except KeyError as ke:
                print("Copy label \"{0}\" not found!".format(label))
                exit(1)
        index += 1

    return lines, copy_dict
