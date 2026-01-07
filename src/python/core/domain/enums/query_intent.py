from enum import Enum


class QueryIntent(Enum):
    FIND_BEST = "find_best"
    LIST_ALL = "list_all"
    COMPARE = "compare"
    EXPLAIN = "explain"
    GENERAL = "general"
