"""
In this test case, the user did not provide any context and we only
could inject today’s date in the context.
"""

import asyncio
from datetime import date

from back.prompts import SYSTEM_PROMPT
from back.workflow import Context, main_loop, user_message

context = Context(
    system_prompt=SYSTEM_PROMPT.format({"date": str(date.today())}),
    messages=[
        user_message("Hey! I was wondering, do you think it will rain tomorrow?")
    ],
)
response = asyncio.run(
    main_loop(
        context=context,
        debug=True,
    )
)
print(response)
