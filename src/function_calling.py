import json
import random

from openai import OpenAI


def get_current_weather(location: str, unit: str = "celsius") -> str:
    weather_data = {
        "location": location,
        "temperature": random.randint(15, 30)
        if unit == "celsius"
        else random.randint(60, 85),
        "unit": unit,
        "forecast": random.choice(["sunny", "cloudy", "rainy", "snowy"]),
    }
    return json.dumps(weather_data)


def main() -> None:
    client = OpenAI()

    # User input
    messages = [
        {
            "role": "developer",
            "content": "You are a helpful assistant that can get weather information.",
        },
        {"role": "user", "content": "What's the weather like in San Francisco, CA?"},
    ]

    print("🌤️  Weather Function Calling Example")
    print("=" * 40)
    print(f"User: {messages[1]['content']}")

    # Define tool using the tools format for Response API
    weather_tool = {
        "type": "function",
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The temperature unit to use",
                },
            },
            "required": ["location"],
        },
    }

    # Use the Response API instead of chat completions
    response = client.responses.create(
        model="gpt-4o",
        input=messages,
        tools=[weather_tool],
        tool_choice="auto",
    )

    tool_call = response.output[0]
    function_name = tool_call.name
    function_args = json.loads(tool_call.arguments)

    print(f"\nAssistant is calling: {function_name}({function_args})")
    weather_result = get_current_weather(**function_args)
    print(f"\nFunction call retuned: {weather_result}")

    messages = messages + [
        tool_call,
        {
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": weather_result,
        },
    ]
    final_response = client.responses.create(
        model="gpt-4o",
        input=messages,
    )

    print(f"\nAssistant: {final_response.output_text}")


if __name__ == "__main__":
    main()
