import dataclasses
import textwrap



def _test(gemtext: str):
    return list(parse(gemtext.lstrip()))


def parse(gemtext: str):
    """
    >>> _test('''
    ... This is a test.
    ... ''')
    [TextLine(text='This is a test.')]
    """

    for line in gemtext.splitlines():
        yield TextLine(line)


@dataclasses.dataclass
class TextLine:
    text: str
