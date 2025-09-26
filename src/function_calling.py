import json
from typing import Callable
from openai import OpenAI

from weather import get_current_weather, get_sun_times, get_weather_forecast


############## RUN USING #########################
# uv run --env-file=.env src/function_calling.py
##################################################

def main() -> None:
    client = OpenAI()

    # User input
    messages = [
        {
            "role": "developer",
            "content": "You are a helpful assistant that can get weather information.",
        },
        {
            "role": "user", 
            "content": "At what time is the sunset in Milan, Italy?"
        },
    ]

    print("🌤️  Weather Function Calling Example")
    print("=" * 40)
    print(f"User: {messages[1]['content']}")

    # Define tools using the tools format for Response API
    weather_tools = [
        {
            "type": "function",
            "name": "get_current_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            }
        },
        {
            "type": "function",
            "name": "get_weather_forecast",
            "description": "Get daily weather forecast for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "days": {"type": "integer", "description": "Number of days to forecast (max 10)", "maximum": 10}
                },
                "required": ["location", "days"]
            }
        },
        {
            "type": "function",
            "name": "get_sun_times",
            "description": "Get sunrise and sunset times for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }
    ]

    # Use the Response API instead of chat completions
    response = client.responses.create(
        model="gpt-4o",
        input=messages,
        tools=weather_tools,
        tool_choice="auto",
    )

    # Get the tool call from the openAI response
    tool_call = response.output[0]
    function_name = tool_call.name
    function_args = json.loads(tool_call.arguments)

    tool: Callable = {
        "get_current_weather": get_current_weather,
        "get_weather_forecast": get_weather_forecast,
        "get_sun_times": get_sun_times
    }[function_name]
    
    # Call the tool
    result = tool(**function_args)

    # Print the tool call and the result
    print(f"\nAssistant is calling: {function_name}({function_args})")
    print(f"\nFunction call retuned: {result}")

    # Add the tool call and the result to the messages
    messages = messages + [
        tool_call,
        {
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": json.dumps(result),
        },
    ]

    # Call the final response
    final_response = client.responses.create(
        model="gpt-4o",
        input=messages,
    )

    print(f"\nAssistant: {final_response.output_text}")


if __name__ == "__main__":
    main()
