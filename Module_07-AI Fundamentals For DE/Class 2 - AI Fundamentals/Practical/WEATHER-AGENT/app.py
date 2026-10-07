"""Weather-Based Daily Planning Agent.

This file contains the complete LangGraph application used by LangGraph Studio
and by the local terminal demo.

The important idea in this project is that the agent is not just a single LLM
call. It is a small workflow:

1. Read the user's request.
2. Ask the local Ollama model to extract intent, location, and day.
3. Route either to live weather lookup or to a general response.
4. Fetch weather from Open-Meteo when needed.
5. Classify the weather using deterministic Python rules.
6. Route to the correct planning advice branch.
7. Ask the local Ollama model to generate the final user-facing answer.

LangGraph passes a shared state dictionary from node to node. Each node reads
the fields it needs and returns only the fields it wants to update.
"""
import json
import os
import re
from typing import Literal, Optional, TypedDict

import requests
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph

# Load environment variables from .env.
#
# In this project .env contains:
#
# OLLAMA_MODEL=llama3.2:3b
#
# Keeping the model name in .env makes it easy to switch to another local
# Ollama model without editing code.
load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# ChatOllama talks to the local Ollama server.
#
# This requires:
# 1. Ollama installed.
# 2. The model pulled locally, for example:
#    ollama pull llama3.2:3b
# 3. Ollama running in the background.
#
# temperature=0 makes responses more deterministic, which is useful for demos.
llm = ChatOllama(model=OLLAMA_MODEL, temperature=0)

class WeatherAgentState(TypedDict):
    """Shared state for one LangGraph execution.

    LangGraph state is the "memory" of a single graph run. It is not permanent
    long-term memory and it is not a database. During one run, every node can
    read from this state and return updates to it.

    Example:
        The `extract_intent` node writes `needs_weather`, `location`, and `day`.
        The `fetch_weather` node then reads `location` and `day`, calls the
        weather API, and writes `weather_data`.
    """
    # The original user message typed in the terminal or sent from Studio.
    user_query: str 
    
    # True when the user request requires live weather data.
    needs_weather: bool
    
    # City or place extracted from the query, for example "Mumbai".
    location: Optional[str]
    
    # The day extracted from the query. This demo supports "today" and
    # "tomorrow" because Open-Meteo is queried with a short daily forecast.
    day: Optional[str]
    
    # Weather forecast returned by Open-Meteo, or {"error": "..."} if the API
    # call failed.
    weather_data: Optional[dict]
    
    # Normalized classification derived from weather_data:
    # "rain_expected", "very_hot", "normal_weather", or "unknown".
    weather_condition: Optional[str]
    
    # Route selected after classification:
    # "rain_advice", "hot_advice", or "normal_advice".
    advice_type: Optional[str]
    
    # Final answer generated for the user.
    final_answer: Optional[str]    

def extract_json(text: str) -> dict:
    try:
        return json.load(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.load(match.group())
        raise ValueError(f"Could not parse JSON from LLM response: {text}")
    
def extract_intent_node(state: WeatherAgentState) -> dict:
    user_query = state["user_query"]
    prompt = f"""
        you are an intent extraction assistant
        
        return only valid JSON with these fields:
        {{
            "needs_weather": true or false
            "location": "city name or null"
            "day": "today" or "tomorrow"
        }}
        
        rules:
        - If user asks about umbrella, rain, heat, weather, travel plan, outdoor plan, what to carry, or day planning, needs_weather = true
        - If no city/location is present, location = null
        - If day is not clear, use "today"
        - Do not add explanation
        - Return JSON only
        
        User query:
        {user_query}
    """
    response = llm.invoke(prompt)
    parsed = extract_json(response.conent)
    
    location = parsed.get("location")
    if isinstance(location, str) and location.lower() == "null":
        location = None
        
    day = parsed.get("day") or "today"
    if day not in {"today", "tomorrow"}:
        day = "today"
    
    return {
        "needs_weather": bool(parsed.get("needs_weather", False)),
        "location": location,
        "day": day
    }

def get_coordinates(location: str) -> dict:
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": location,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    if "results" not in data or not data["results"]:
        raise ValueError(f"Could not find coordinates for location: {location}")

    result = data["results"][0]
    return {
        "name": result["name"],
        "country": result.get("country"),
        "latitude": result["latitude"],
        "longitude": result["longitude"]
    }
    
def get_weather_forecast(location:str, day: str) -> dict:
    coordinates = get_coordinates(location)
    url = "https://api.open-meteo.com/v1/forecast"
    
    params = {
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],
        "daily": (
            "weather_code,temperature_2m_max,temperature_2m_min,"
            "precipitation_probability_max"
        ),
        "forcast_days": 3,
        "timezone": "auto"
    }
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    forcast = response.json()
    
    index = 1 if day == "tomorrow" else 0
    daily = forcast["daily"]
    country = coordinates.get("country")
    resolved_location = coordinates["name"]
    if country:
        resolved_location = f"{resolved_location}, {country}"
    
    return {
        "resolved_location": resolved_location,
        "day": day,
        "date": daily["time"][index],
        "weather_code": daily["weather_code"][index],
        "max_temp": daily["temperature_2m_max"][index],
        "min_temp": daily["temperature_2m_min"][index],
        "precipitation_probability": daily["precipitation_probability_max"][index]
    }

def fetch_weather_node(state: WeatherAgentState) -> dict:
    try:
        weather_data = get_weather_forecast(
            location=state["location"] or "",
            day=state["day"] or "today"
        )
        return {"weather_data": weather_data}
    except Exception as exc:
        return {"weather_data": {"error": str(exc)}}

def classify_weather_node(state: WeatherAgentState) -> dict:
    weather_data = state["weather_data"]
    
    if not weather_data or "error" in weather_data:
        return {
            "weather_condition": "unknown",
            "advice_type": "normal_advice"
        }
    
    precipitation = weather_data["precipitation_probability"]
    max_temp = weather_data["max_temp"]
    
    if precipitation >= 50:
        condition = "rain_expected"
        advice_type = "rain_advice"
    elif max_temp >= 35:
        condition = "very_hot"
        advice_type = "hot_advice"
    else:
        condition = "normal_weather"
        advice_type = "normal_advice"
    
    return {
        "weather_condition": condition,
        "advice_type": advice_type
    }

def rain_advice_node(state:WeatherAgentState) -> dict:
    return {"advice_type": "rain_advice"}

def hot_advice_node(state:WeatherAgentState) -> dict:
    return {"advice_type": "hot_advice"}

def normal_advice_node(state:WeatherAgentState) -> dict:
    return {"advice_type": "normal_advice"}

def final_response_node(state:WeatherAgentState) -> dict:
    prompt = f"""
        You are a practical daily planning assistant.
        
        User query:
        {state["user_query"]}
        
        state:
        Location: {state.get("location")}
        Day: {state.get("day")}
        Weather data: {state.get("weather_data")}
        Weather condition: {state.get("weather_condition")}
        Advice route: {state.get("advice_type")}
    
        Generate a concise answer.
        
        Include:
        1. Whether the user should carry an umbrella
        2. Weather summary
        3. Practical planning advice
        4. One short reason behind the recommendation
    """
    
    respose = llm.invoke(prompt)
    return {"final_answer": respose.content}

def general_response_node(state:WeatherAgentState) -> dict:
    prompt = f"""
        The user asked:
        {state['user_query']}
        
        This does not require the live weather data.
        
        Give a helpfull response in 3-5 bullets points
    """
    respose = llm.invoke(prompt)
    return {"final_answer": respose.content}

def route_after_intent(state: WeatherAgentState) -> Literal["fetch_weather", "general_response"]:
    if state["needs_weather"] and state["location"]:
        return "fetch_weather"
    return "general_response"

def route_weather_advice(state:WeatherAgentState) -> Literal["rain_advice", "hot_advice", "normal_advice"]:
    advice_type = state["advice_type"]

    if advice_type == "rain_advice":
        return "rain_advice"
    elif advice_type == "hot_advice":
        return "hot_advice"
    else:
        return "normal_advice"
    
def build_graph():
    """Build and compile the LangGraph workflow.

    The graph is created in three steps:

    1. Register all node functions.
    2. Connect nodes with normal edges and conditional edges.
    3. Compile the graph so it can be invoked locally or loaded by Studio.

    Returns:
        A compiled LangGraph graph object.
    """
    builder = StateGraph(WeatherAgentState)
    
    builder.add_node("extract_intent", extract_intent_node) # this will update the state
    builder.add_node("fetch_weather", fetch_weather_node)
    builder.add_node("classify_weather", classify_weather_node)
    builder.add_node("rain_advice", rain_advice_node)
    builder.add_node("hot_advice", hot_advice_node)
    builder.add_node("normal_advice", normal_advice_node)
    builder.add_node("final_response", final_response_node)
    builder.add_node("general_response", general_response_node)
    
    
    builder.add_edge(START, "extract_intent")
    builder.add_conditional_edges(
        "extract_intent",
        route_after_intent,
        {
            "fetch_weather": "fetch_weather",
            "general_response": "general_response"
        }
    )
    builder.add_edge("fetch_weather", "classify_weather")
    builder.add_conditional_edges(
        "classify_weather",
        route_weather_advice,
        {
            "rain_advice": "rain_advice",
            "hot_advice": "hot_advice",
            "normal_advice": "normal_advice"
        }
    )
    builder.add_edge("rain_advice", "final_response")
    builder.add_edge("hot_advice", "final_response")
    builder.add_edge("normal_advice", "final_response")
    builder.add_edge("final_response", END)
    builder.add_edge("general_response", END)
    
    return builder.compile()
# LangGraph Studio needs a module-level graph object.
#
# langgraph.json points to this object:
#
# {
#   "graphs": {
#     "weather_agent": "./app.py:graph"
#   }
# }
graph = build_graph()

def make_inital_state(user_query: str) -> WeatherAgentState:
    return {
        "user_query": user_query,
        "needs_weather": False,
        "location": None,
        "day": None,
        "weather_data": None,
        "weather_condition": None,
        "advice_type": None,
        "final_answer": None
    }
if __name__ == "__main__":
    # This block runs only when executing:
    #
    # python app.py
    #
    # LangGraph Studio imports `graph` from this file and does not use this
    # terminal loop.
    print("\nWeather Planning Agent is ready.")
    print(f"Using Ollama model: {OLLAMA_MODEL}")
    print("Type 'exit' to stop.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
        except EOFError:
            # This makes the script exit cleanly in non-interactive terminals
            # or automated checks where stdin is closed.
            print("Goodbye!")
            break
    
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not user_input:
            continue
        
        # Run one full graph execution. The result is the final state after all
        # selected nodes have completed.
        result = graph.invoke(make_inital_state(user_input))
        
        print("\nAgent: ")
        print(result["final_answer"])
        
        print("\n--- Debug State ---")
        print(
            {
                "needs_weather": result["needs_weather"],
                "location": result["location"],
                "day": result["day"],
                "weather_condition": result["weather_condition"],
                "advice_type": result["advice_type"],
                "weather_data": result["weather_data"],
            }
        )
        print("---------------------------\n")