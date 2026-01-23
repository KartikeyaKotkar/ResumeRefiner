from google.genai import types
import inspect

try:
    sig = inspect.signature(types.GenerateContentConfig)
    print("GenerateContentConfig parameters:", sig.parameters.keys())
except Exception as e:
    print(f"Error inspecting signature: {e}")

# Also check if we can instantiate it with system_instruction
try:
    config = types.GenerateContentConfig(system_instruction="You are a helper.")
    print("Successfully created GenerateContentConfig with system_instruction")
except TypeError as e:
    print(f"Failed to create GenerateContentConfig: {e}")
