"""
Вспомогательные функции
"""

from typing import Iterable, Iterator, Any
from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category
from bookkeeper.models.budget import Budget


def _get_indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _lines_with_indent(lines: Iterable[str]) -> Iterator[tuple[int, str]]:
    for line in lines:
        if not line or line.isspace():
            continue
        yield _get_indent(line), line.strip()


def read_tree(lines: Iterable[str]) -> list[tuple[str, str | None]]:
    """
    Прочитать структуру дерева из текста на основе отступов. Вернуть список
    пар "потомок-родитель" в порядке топологической сортировки. Родитель
    элемента верхнего уровня - None.
    Пример. Следующий текст:
    parent
        child1
            child2
        child3
    даст такое дерево:
    [('parent', None), ('child1', 'parent'),
     ('child2', 'child1'), ('child3', 'parent')]
    Пустые строки игнорируются.
    Parameters
    ----------
    lines - Итерируемый объект, содержащий строки текста (файл или список строк)
    Returns
    -------
    Список пар "потомок-родитель"
    """
    parents: list[tuple[str | None, int]] = []
    last_indent = -1
    last_name = None
    result: list[tuple[str, str | None]] = []
    for i, (indent, name) in enumerate(_lines_with_indent(lines)):
        if indent > last_indent:
            parents.append((last_name, last_indent))
        elif indent < last_indent:
            while indent < last_indent:
                _, last_indent = parents.pop()
            if indent != last_indent:
                raise IndentationError(
                    f'unindent does not match any outer indentation '
                    f'level in line {i}:\n'
                )
        result.append((name, parents[-1][0]))
        last_name = name
        last_indent = indent
    return result


def expense_adapter(exp_row: dict[str, Any]) -> Expense:
    """
    Адаптер для базы с тратами
    Parameters
    ----------
    exp_row - строка в базе с тратами в виде словаря
    Returns
    -------
    Expense объект с данными из базы
    """
    return Expense(pk=int(exp_row['pk']), amount=int(exp_row['amount']),
                   expense_date=exp_row['expense_date'],
                   added_date=exp_row['added_date'],
                   comment=exp_row['comment'], category=int(exp_row['category']))


def category_adapter(cat_row: dict[str, Any]) -> Category:
    """
    Адаптер для базы с категориями
    Parameters
    ----------
    cat_row - строка в базе с категориями в виде словаря
    Returns
    -------
    Category объект с данными из базы
    """
    return Category(pk=cat_row['pk'], name=cat_row['name'],
                    parent=cat_row['parent'])


def budget_adapter(budget_row: dict[str, Any]) -> Budget:
    """
    Адаптер для базы с бюджетом
    Parameters
    ----------
    budget_row - строка в базе с бюджетом в виде словаря
    Returns
    -------
    Budget объект с данными из базы
    """
    return Budget(pk=int(budget_row['pk']),
                  budget=int(budget_row['budget']),
                  cur_sum=int(budget_row['cur_sum'])
                  )


adapters = {
    'budget': budget_adapter,
    'expense': expense_adapter,
    'category': category_adapter
}