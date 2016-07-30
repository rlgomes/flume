"""
elastic query module

 - handles the conversion of a filter to the ES query DSL
"""
import ast

from flume.exceptions import FlumineException


def to_es_query(node):
    """
    convert AST tree into an ES query
    """

    if isinstance(node, ast.Module):
        return {
            'filter': to_es_query(node.body[0])
        }

    if isinstance(node, list):
        # XXX: handle other elements of the list
        result = []
        nodes = node

        for node in nodes:
            result.append(to_es_query(node))

        return result

    if isinstance(node, ast.Expr):
        return to_es_query(node.value)

    if isinstance(node, ast.Num):
        return node.n

    if isinstance(node, ast.Str):
        return node.s

    if isinstance(node, ast.Compare):
        value = to_es_query(node.comparators[0])

        if isinstance(node.ops[0], ast.Eq):
            return {'term': {node.left.id: value}}

        if isinstance(node.ops[0], ast.NotEq):
            return {'not': {'term': {node.left.id: value}}}

        if isinstance(node.ops[0], ast.Lt):
            return {'range': {node.left.id: {'lt': value}}}

        if isinstance(node.ops[0], ast.Gt):
            return {'range': {node.left.id: {'gt': value}}}

        if isinstance(node.ops[0], ast.LtE):
            return {'range': {node.left.id: {'lte': value}}}

        if isinstance(node.ops[0], ast.GtE):
            return {'range': {node.left.id: {'gte': value}}}

    if isinstance(node, ast.BoolOp):
        if isinstance(node.op, ast.And):
            return {
                'bool': {
                    'must': to_es_query(node.values)
                }
            }

        elif isinstance(node.op, ast.Or):
            return {
                'bool': {
                    'should': to_es_query(node.values),
                    'minimum_should_match': 1
                }
            }

    if isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.Not):
            return {
                'bool': {
                    'must_not': to_es_query(node.operand),
                }
            }

    raise Exception('unhandled %s' % node)

def filter_to_es_query(filter_expr):
    """
    take a filter expression such as `foo=="bar"` and convert it into
    the corresponding ES query
    """
    if filter_expr is None:
        return {'match_all': {}}
    else:
        try:
            tree = ast.parse(filter_expr)
            return {'constant_score': to_es_query(tree)}
        except Exception as exception:
            raise FlumineException('invalid filter expression: %s - %s' %
                                   (filter_expr, exception))
