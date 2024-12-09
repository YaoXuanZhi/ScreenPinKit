# coding:utf-8
"""
模糊匹配库，用来辅助插件市场的快捷搜索
"""

from PyQt5.QtCore import *

from fuzzywuzzy import process
from .trie import Trie

class FuzzyMatch(QObject):
    searchedSignal = pyqtSignal(list)
    def __init__(self, parent = None):
        super().__init__(parent)
        self.choices = []
        self.map = {}
        self.trie = Trie()

    def insertItem(self, item0:str):
        item = item0.lower()
        index = len(self.choices)
        if item in self.map:
            return
        self.map[item] = index
        self.choices.append(item)
        self.trie.insert(item, index)

    def clear(self):
        self.map.clear()
        self.choices.clear()
        self.trie = Trie()

    def bestMatch2(self, keyWord0:str):
        keyWord = keyWord0.lower()
        items = self.trie.items(keyWord.lower())
        indexes = {i[1] for i in items}
        return indexes

    def bestMatch(self, keyWord0:str):
        indexes = []
        keyWord = keyWord0.lower()
        for val in process.extract(keyWord, self.choices):
            item, score = val
            # 过滤掉评分太低的结果
            if score < 60:
                continue
            indexes.append(self.map[item])

        result = {i for i in indexes}
        return result