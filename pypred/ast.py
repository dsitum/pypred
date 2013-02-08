"""
This module provides the AST nodes that are used to
represent and later, evaluate a predicate.
"""
import re


class Node(object):
    "Root object in the AST tree"
    def __init__(self):
        # Set to true in our _validate method
        self.valid = False

    def validate(self, info=None):
        """
        Performs semantic validation of the Node.
        Attaches information to an info object,
        which is returned
        """
        if info is None:
            info = {}

        # Post order validation
        if hasattr(self, "left"):
            self.left.validate(info)
        if hasattr(self, "right"):
            self.right.validate(info)
        self.valid = self._validate(info)

    def _validate(self, info):
        "Validates the node"
        return True

    def pre(self, func):
        """
        Performs a pre-order traversal of the
        tree, and invokes a callback for each node.
        """
        func(self)
        if hasattr(self, "left"):
            self.left.pre(func)
        if hasattr(self, "right"):
            self.right.pre(func)

    def __repr__(self):
        name = self.__class__.__name__
        r = name
        if hasattr(self, "type"):
            r += " t:" + str(self.type)
        if hasattr(self, "value"):
            r += " v:" + str(self.value)
        if hasattr(self, "left"):
            r += " l:" + self.left.__class__.__name__
        if hasattr(self, "right"):
            r += " r:" + self.right.__class__.__name__
        return r


class LogicalOperator(Node):
    "Used for the logical operators"
    def __init__(self, op, left, right):
        self.type = op
        self.left = left
        self.right = right

    def _validate(self, info):
        "Validates the node"
        if self.type not in ("and", "or"):
            errs = info.setdefault("errors", [])
            errs.append("Unknown logical operator %s" % self.type)
            return False
        return True

class NegateOperator(Node):
    "Used to negate a result"
    def __init__(self, expr):
        self.left = expr

class CompareOperator(Node):
    "Used for all the mathematical comparisons"
    def __init__(self, comparison, left, right):
        self.type = comparison
        self.left = left
        self.right = right

    def _validate(self, info):
        if self.type not in (">=", ">", "<", "<=", "=", "!=", "is"):
            errs = info.setdefault("errors", [])
            errs.append("Unknown compare operator %s" % self.type)
            return False
        return True

class ContainsOperator(Node):
    "Used for the 'contains' operator"
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def _validate(self, info):
        if not isinstance(self.right, (Number, Literal, Constant)):
            errs = info.setdefault("errors", [])
            errs.append("Contains operator must take a literal or constant! Got: %s" % repr(self.right))
            return False
        return True

class MatchOperator(Node):
    "Used for the 'matches' operator"
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def _validate(self, info):
        if not isinstance(self.right, Regex):
            errs = info.setdefault("errors", [])
            errs.append("Match operator must take a regex! Got: " % repr(self.right))
            return False
        return True

class Regex(Node):
    "Regular expression literal"
    def __init__(self, value):
        # Unpack a Node object if we are given one
        if isinstance(value, Node):
            self.value = value.value
        else:
            self.value = value

    def _validate(self, info):
        if not isinstance(self.value, str):
            errs = info.setdefault("errors", [])
            errs.append("Regex must be a string! Got: " % repr(self.value))
            return False

        # Try to compile
        try:
            self.re = re.compile(self.value)
        except Exception, e:
            errs = info.setdefault("errors", [])
            errs.append("Regex compilation failed")
            regexes = info.setdefault("regex", {})
            regexes[self.value] = repr(e)
            return False

        return True

class Literal(Node):
    "String literal"
    def __init__(self, value):
        self.value = value

class Number(Node):
    "Numeric literal"
    def __init__(self, value):
        try:
            self.value = float(value)
        except:
            self.value = value

    def _validate(self, info):
        if not isinstance(self.value, float):
            errs = info.setdefault("errors", [])
            errs.append("Failed to convert number to float! Got: %s" % self.value)
            return False
        return True

class Constant(Node):
    "Used for true, false, null"
    def __init__(self, value):
        self.value = value

    def _validate(self, info):
        if self.value not in (True, False, None):
            errs = info.setdefault("errors", [])
            errs.append("Invalid Constant! Got: %s" % self.value)
            return False
        return True

class Undefined(Node):
    "Represents a non-defined object"
    def __init__(self):
        return

class Empty(Node):
    "Represents the null set"
    def __init__(self):
        return

