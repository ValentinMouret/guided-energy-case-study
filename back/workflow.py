from __future__ import annotations

import json
import logging
from datetime import date

import anthropic
from anthropic.types import (
    MessageParam,
    TextBlock,
    ToolUseBlock,
)
from pydantic import BaseModel

from .config import config
from .prompts import SYSTEM_PROMPT
from .weather import GetWeatherInputs, get_weather, get_weather_tool

logging.basicConfig(
    level=logging.WARN,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class Context(BaseModel):
    """
    Context for managing conversation state.
    """

    system_prompt: str
    messages: list[MessageParam]

    @staticmethod
    def default() -> Context:
        return Context(
            system_prompt=SYSTEM_PROMPT.format(
                {
                    "today": str(date.today()),
                }
            ),
            messages=[],
        )


client = anthropic.Anthropic(
    api_key=config.anthropic_api_key,
)


async def main_loop(context: Context, debug: bool = False):
    """
    The agent handles the conversation loop.
    """
    if debug:
        logger.info(f"Messages: {context.messages}")

    response = client.messages.create(
        model=config.model,
        max_tokens=1024,
        tools=[
            get_weather_tool,
        ],
        system=context.system_prompt,
        messages=context.messages,
    )
    if debug:
        logger.info(f"Got response: {response}")

    assistant_content = ""
    tool_calls = []

    for content in response.content:
        match content:
            case TextBlock(text=text):
                assistant_content += text

            case ToolUseBlock(id=id, name=name, input=input) as tool_use:
                tool_calls.append(tool_use)
                match name:
                    case "get_weather":
                        inputs = GetWeatherInputs.from_tool_call(input)
                        if debug:
                            logger.info(f"Tool use: get_weather({inputs.location})")

                        result = get_weather(inputs.location)

                        if debug:
                            logger.info(f"Weather result: {result}")

                        context.messages.extend(
                            [
                                {"role": "assistant", "content": [tool_use]},
                                tool_result_message(
                                    tool_use_id=id,
                                    content=json.dumps(result.simplify()),
                                ),
                            ]
                        )

                        return await main_loop(context, debug=debug)

                    case tool:
                        raise ValueError(f"Tool call error: unknown tool {tool}")

            case _ as content:
                logging.warning(f"Got unexpected block: {content}")

    return assistant_content


def user_message(content: str) -> MessageParam:
    return {
        "role": "user",
        "content": content,
    }


def assistant_message(content: str) -> MessageParam:
    return {
        "role": "assistant",
        "content": content,
    }


def tool_use_message(content: ToolUseBlock) -> MessageParam:
    return {"role": "assistant", "content": [content]}


def tool_result_message(tool_use_id: str, content: str) -> MessageParam:
    return {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": content,
                "is_error": False,
            }
        ],
    }


if __name__ == "__main__":
    from back.cli import chat

    context = Context.default()

    chat(context)
