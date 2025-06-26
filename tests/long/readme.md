# Long tests
These tests are long or expensive to run, so they are not to be «watched», or even probably run in hooks.

They can be run manually to observe typical scenarios and ensure there is no regression.

To take them further, we could put an agent in the loop whose job it is to ensure there are no regressions.

To run a test:
```
PYTHONPATH=. uv run python tests/long/test_chat_init_missing_context.py
```
