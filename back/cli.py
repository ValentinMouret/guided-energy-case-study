import asyncio
import sys
from datetime import date

import click
from anthropic import APIStatusError

from back.config import config
from back.workflow import Context, main_loop
from back.prompts import SYSTEM_PROMPT


def print_welcome():
    click.echo(
        click.style("🌤️  Welcome to your Weather Assistant", fg="bright_cyan", bold=True)
    )
    click.echo(click.style("=" * 50, fg="cyan"))
    click.echo("Ask me anything about weather conditions and forecasts!")
    click.echo("Type 'exit', 'quit', or press Ctrl+C to leave.\n")


def print_thinking():
    click.echo(click.style("🤔 Thinking...", fg="yellow", dim=True), nl=False)


def clear_thinking():
    click.echo("\r" + " " * 20 + "\r", nl=False)


@click.command()
@click.option(
    "--api-key",
    envvar="ANTHROPIC_API_KEY",
    help="Anthropic API key (can also be set via ANTHROPIC_API_KEY env var)",
)
@click.option(
    "--weather-api-key",
    envvar="WEATHER_API_KEY",
    help="Weather API key (can also be set via WEATHER_API_KEY env var)",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode to show tool calls",
)
def chat(
    api_key: str | None,
    weather_api_key: str | None,
    debug: bool,
):
    """Start an interactive chat session with your weather assistant."""

    if api_key:
        config.anthropic_api_key = api_key

    if weather_api_key:
        config.weather_api_key = weather_api_key

    if not config.anthropic_api_key:
        click.echo(click.style("❌ Error: Anthropic API key not found!", fg="red"))
        click.echo(
            "Please set ANTHROPIC_API_KEY environment variable or use --api-key option."
        )
        sys.exit(1)

    if not config.weather_api_key:
        click.echo(click.style("❌ Error: Weather API key not found!", fg="red"))
        click.echo(
            "Please set WEATHER_API_KEY environment variable or use --weather-api-key option."
        )
        sys.exit(1)

    print_welcome()

    context = Context(
        system_prompt=SYSTEM_PROMPT.format(date=str(date.today())),
        messages=[],
    )

    while True:
        try:
            user_input = click.prompt(
                click.style("You", fg="green", bold=True), prompt_suffix=": "
            )

            if user_input.lower() in ["exit", "quit", "bye"]:
                click.echo(
                    click.style("\n👋 Goodbye! Stay weather-aware!", fg="bright_cyan")
                )
                break

            context.messages.append(
                {
                    "role": "user",
                    "content": user_input,
                }
            )

            print_thinking()

            try:
                response = asyncio.run(main_loop(context, debug=debug))
                clear_thinking()

                click.echo(
                    click.style("Weather", fg="bright_blue", bold=True) + ": ", nl=False
                )

                if isinstance(response, str):
                    click.echo(response)
                else:
                    click.echo(
                        response.get("content", "I couldn't generate a response.")
                    )

                context.messages.append(
                    {
                        "role": "assistant",
                        "content": response
                        if isinstance(response, str)
                        else response.get("content", ""),
                    }
                )

                click.echo()

            except APIStatusError as e:
                clear_thinking()
                if e.status_code == 401:
                    click.echo(
                        click.style(
                            "❌ Authentication error: Invalid API key", fg="red"
                        )
                    )
                elif e.status_code == 429:
                    click.echo(
                        click.style(
                            "❌ Rate limit exceeded. Please try again later.", fg="red"
                        )
                    )
                else:
                    click.echo(click.style(f"❌ API error: {e.message}", fg="red"))
            except Exception as e:
                clear_thinking()
                if debug:
                    click.echo(click.style(f"❌ Error: {str(e)}", fg="red"))
                else:
                    click.echo(
                        click.style(
                            "❌ An error occurred. Use --debug for more details.",
                            fg="red",
                        )
                    )

        except KeyboardInterrupt:
            click.echo(
                click.style("\n\n👋 Goodbye! Stay weather-aware!", fg="bright_cyan")
            )
            break
        except EOFError:
            click.echo(
                click.style("\n\n👋 Goodbye! Stay weather-aware!", fg="bright_cyan")
            )
            break


if __name__ == "__main__":
    chat()
