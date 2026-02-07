import dataclasses
import typing


def _test(gemtext: str):
    return list(parse(gemtext.lstrip()))


def parse(gemtext: str):
    """
    >>> _test('''
    ... This is a test.
    ... ''')
    [TextLine(text='This is a test.')]

    >>> _test('''
    ... This is a test.
    ...
    ... => https://www.example.com/ Link
    ... ''')
    [TextLine(text='This is a test.'), TextLine(text=''), LinkLine(url='https://www.example.com/', link_name='Link')]
    """

    for line in gemtext.splitlines():
        link_line = LinkLine.parse(line)
        if link_line:
            yield link_line
            continue
        yield TextLine(line)


@dataclasses.dataclass
class TextLine:
    text: str


@dataclasses.dataclass
class LinkLine:
    url: str
    link_name: typing.Optional[str] = None

    @staticmethod
    def parse(line: str):
        """
        >>> LinkLine.parse('Not a link line')

        >>> LinkLine.parse('=>foo')
        LinkLine(url='foo', link_name=None)

        >>> LinkLine.parse('=> foo')
        LinkLine(url='foo', link_name=None)

        >>> LinkLine.parse('=> foo bar')
        LinkLine(url='foo', link_name='bar')
        """
        if not line.startswith('=>'):
            return None
        line = line.removeprefix('=>')
        line = line.lstrip()
        parts = line.split(maxsplit=1)
        assert len(parts) in (1,2)
        if len(parts) == 1:
            return LinkLine(parts[0])
        return LinkLine(parts[0], parts[1])
