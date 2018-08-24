# -*- coding: utf-8 -*-

class Common:
    def __init__(self):
        pass

    @staticmethod
    def replace_string(totalstring, replace_pos, substring):
        begin = totalstring[0:replace_pos[0]]
        last = totalstring[replace_pos[1]:]
        return ''.join([begin, substring, last])
