# Guided Energy case study

## Description
The goal of the case study is to build an interface where users can ask weather-related questions.

The difficulty is that there are endless questions that could be asked.
Thankfully, we can use modern AI techniques to delegate question answering to an LLM.

The LLM can have a conversation with our users, and it can also call «tools» to get the data it needs to formulate an answer.

## Result
I chose to build a CLI tool because I estimated the web interface would be a distraction from the core of the problem here, and it would be simpler to have a single language and deployment to run for the case study.
It still requires to properly handle asynchronous operations, which (I think) is the main challenge of the user interface here.

## Setup Instructions

### Prerequisites
You'll need API keys for both Anthropic and OpenWeatherMap inside a `.env` file you would create.
I will send you my keys, along with the case study, please don't abuse them :)

You can check-out the repository:
```shell
git clone git@github.com:ValentinMouret/guided-energy
cd guided-energy
```

Then, here are several ways you can get the project running:

### Option 1: Using Nix Flakes

If you have Nix with flakes enabled:

```bash
# Enter the development shell (this will install Python 3.13, uv, and ruff)
nix develop

# Run the weather assistant
uv run python -m back.workflow
```

### Option 2: Using Vanilla Python

Requirements: Python 3.13+ and pip

```bash
pip install uv

uv sync

source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run the weather assistant
uv run python -m back.workflow
```

### Option 3: Using Docker
```bash
# Build the Docker image
docker build -t weather-assistant .

./run-docker.sh
```

## Usage

Once set up, you can interact with the weather assistant:

```bash
# Basic usage
uv run python -m back.workflow

# With debug mode to see tool calls
uv run python -m back.workflow --debug

# Override API keys via command line
uv run python -m back.workflow --api-key "your-key" --weather-api-key "your-weather-key"
```

## Technical decisions
- I chose to keep a simple design with a single prompt. As long as it works, this option should be preferred to building complex agentic workflows.
- I left out a bunch of technical nice-to-have features that would have to make it to a production application, but that were not directly related to the problem at hand. Like data persistence, caching, observability...

## Challenges
- **AI workflow**: one of the challenges of this case study is to design the right-sized AI workflow.
We delegate a part of our user experience to an LLM that can, for example, indirectly make calls to third-party systems.
This brings its own set of concerns (latency, error handling, user notifications, ...) for both user experience and software architecture.
- **Core data structures**: good programs are built around good data structures. Here, I keep the state as the sequence of messages I send to the LLM, and it is going to use it as its context.
- **Quality assurance**: with a non-deterministic component at the core of our system, the right measures need to be in place to maintain the quality of the service. For that, I created scripts to manually test some scenarios.

## Design
We don't know in advance what the users are going to ask. For example, all of these could be valid:
- What's the weather like?
- What's the weather like in Paris?
- What's the weather like in Paris tomorrow?
- What's the weather tomorrow?
- Will it rain in the coming week?
- What will be the temperature next Tuesday?
- What's the daily temperature over the next 7 days?

At our disposal, we have an API that can fetch a 16-day weather forecast for a given location.

The first task of our agent is to figure out the *location* we want the weather for.
From there, we can fetch the 16-day forecast, pipe it to the LLM, and have it answer the user question.

I use [OpenWeatherMap](https://openweathermap.org/api/one-call-3#current) for the API as weather.com is not free.

## Software architecture
- I split the code in vertical slices, with one file containing the domain and implementation. This felt simpler than DDD or similar architectures.
- I extensively validate the shape of the data using `pydantic`.

## Stack
- Python 3.13
- uv (package manager)
- Anthropic: LLM provider
- click: CLI tool

[Reference](https://guided-energy.notion.site/Guided-Energy-Product-Engineer-take-home-test-200a0bac953a80a8bb94f183231c6a0b?source=copy_link)
