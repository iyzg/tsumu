# contributing to tsumu

thanks for your interest in contributing!

## quick start

```bash
# clone and install
git clone https://github.com/iyzg/tsumu
cd tsumu
make install

# run tests
make test
```

## adding a new generator

1. **create your generator script** in `scripts/`
```python
from anki_utils import (
    InputHandler, OutputHandler, ArgumentParser,
    check_input_not_empty
)

def generate_cards(text, args):
    """Your card generation logic here."""
    cards = []
    # ... your logic ...
    return cards

def main():
    parser = ArgumentParser.create_basic_parser("your generator description")
    # add custom arguments
    parser.add_argument('--custom', help='custom option')
    args = parser.parse_args()

    text = InputHandler.get_input(args.input)
    check_input_not_empty(text)

    cards = generate_cards(text, args)
    OutputHandler.write_cards(cards, args.output, verbose=args.verbose)

if __name__ == '__main__':
    main()
```

2. **add tests** in `scripts/test_your_generator.py`

3. **register in CLI** - add to `scripts/anki.py`:
```python
COMMANDS = {
    'yourgen': {
        'script': 'your_generator.py',
        'help': 'brief description'
    },
    # ...
}
```

4. **update documentation** - add example to README.md

## code style

- use standard python conventions
- keep functions focused and simple
- add type hints where helpful
- write clear docstrings

## testing

```bash
make test       # all tests
make test-fast  # core tests only
```

## design principles

1. **simplicity** - prefer clear over clever
2. **no dependencies** - use only python standard library
3. **composability** - tools should work together
4. **consistency** - follow existing patterns

## questions?

open an issue or discussion on github!
