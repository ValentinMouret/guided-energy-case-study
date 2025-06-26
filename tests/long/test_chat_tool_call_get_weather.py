"""
In this test case, the user did not provide any context initially,
but we asked them and they provided a location.

The next step is to get the coordinates for this location using a
tool call.
"""

import asyncio
from datetime import date

from back.prompts import SYSTEM_PROMPT
from back.workflow import Context, assistant_message, main_loop, user_message

context = Context(
    system_prompt=SYSTEM_PROMPT.format({"date": str(date.today())}),
    messages=[
        user_message("Hey! I was wondering, do you think it will rain tomorrow?"),
        assistant_message(
            "I'd be happy to help you check if it will rain tomorrow! However, I need to know your location to get the weather forecast. Could you tell me what city or area you're in?"
        ),
        user_message(
            "Oops! You are right. I am based in Paris, but I want the weather for Berlin."
        ),
    ],
)
response = asyncio.run(
    main_loop(
        context=context,
        debug=True,
    )
)
print(response)
