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

    >>> _test('''
    ... This is a test
    ...
    ... ```foo
    ... bar
    ... ```
    ... ''')
    [TextLine(text='This is a test'), TextLine(text=''), PreformattingToggleLine(alt_text='foo'), PreformattedTextLine(text='bar'), PreformattingToggleLine(alt_text=None)]

    >>> _test('''
    ... # Welcome
    ...
    ... Something.
    ... ''')
    [TextLine(text='# Welcome'), TextLine(text=''), TextLine(text='Something.')]

    >>> _test('''
    ... This is a test.
    ...
    ... * Item 1
    ... * Item 2
    ... ''')
    [TextLine(text='This is a test.'), TextLine(text=''), ListItem(text='Item 1'), ListItem(text='Item 2')]

    >>> _test('''
    ... This is a test.
    ...
    ... > Line 1
    ... > Line 2
    ... ''')
    [TextLine(text='This is a test.'), TextLine(text=''), QuoteLine(text='Line 1'), QuoteLine(text='Line 2')]
    """

    current_preformatting_toggle_line = None

    for line in gemtext.splitlines():
        preformatting_toggle_line = PreformattingToggleLine.parse(line)

        if current_preformatting_toggle_line:
            if preformatting_toggle_line:
                assert not preformatting_toggle_line.alt_text, 'closing preformatting toggle line with alt text {preformatting_toggle_line.alt_text}'
                current_preformatting_toggle_line = None
                yield preformatting_toggle_line
                continue
            else:
                yield PreformattedTextLine(line)
                continue

        if preformatting_toggle_line:
            current_preformatting_toggle_line = preformatting_toggle_line
            yield preformatting_toggle_line
            continue
        elif current_preformatting_toggle_line and not preformatting_toggle_line:
            current_preformatting_toggle_line = None

        link_line = LinkLine.parse(line)
        if link_line:
            yield link_line
            continue

        list_item = ListItem.parse(line)
        if list_item:
            yield list_item
            continue

        quote_line = QuoteLine.parse(line)
        if quote_line:
            yield quote_line
            continue

        yield TextLine(line)


@dataclasses.dataclass
class TextLine:
    text: str


@dataclasses.dataclass
class PreformattedTextLine(TextLine):
    pass

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


@dataclasses.dataclass
class PreformattingToggleLine:
    alt_text: typing.Optional[str]

    @staticmethod
    def parse(line: str):
        """
        >>> PreformattingToggleLine.parse('Not a preformatting toggle line')

        >>> PreformattingToggleLine.parse('```')
        PreformattingToggleLine(alt_text=None)

        >>> PreformattingToggleLine.parse('```alt')
        PreformattingToggleLine(alt_text='alt')
        """
        if not line.startswith('```'):
            return None
        line = line.removeprefix('```')
        line: typing.Optional[str] = line if line else None
        return PreformattingToggleLine(line)


@dataclasses.dataclass
class HeadingLine:
    level: int
    heading_text: str

    @staticmethod
    def parse(line: str):
        """
        >>> HeadingLine.parse('Not a heading line')

        >>> HeadingLine.parse('# Foo')
        HeadingLine(level=1, heading_text='Foo')
        """
        parts = line.split(maxsplit=1)
        if len(parts) < 2:
            return None
        if not parts[0] in ('#', '##', '###'):
            return None
        return HeadingLine(len(parts[0]), parts[1])


@dataclasses.dataclass
class ListItem:
    text: str

    @staticmethod
    def parse(line: str):
        """
        >>> ListItem.parse('Not a list item')

        >>> ListItem.parse('* Foo')
        ListItem(text='Foo')
        """
        if not line.startswith("* "):
            return None
        return ListItem(line.removeprefix("* "))


@dataclasses.dataclass
class QuoteLine:
    text: str

    @staticmethod
    def parse(line: str):
        """
        >>> QuoteLine.parse('Not a quote line')

        >>> QuoteLine.parse('> Foo')
        QuoteLine(text='Foo')
        """
        if not line.startswith("> "):
            return None
        return QuoteLine(line.removeprefix("> "))
