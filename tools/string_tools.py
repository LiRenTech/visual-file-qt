def get_width_by_file_name(file_name: str) -> int:
    """
    根据文件名获取宽度
    一个英文或者标点数字字符占24像素，一个汉字占48像素
    :param file_name:
    :return:
    """
    res = 0
    for c in file_name:
        if '\u4e00' <= c <= '\u9fff':
            res += 48
        else:
            res += 24
    return res
