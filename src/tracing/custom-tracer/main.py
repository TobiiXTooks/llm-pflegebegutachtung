from tracer import single_turn, Conversation

# Single turn example
response = single_turn(
    prompt_template="Translate the following to French: {{text}}",
    variables={"text": "Hello, how are you?"}
)
print(response)

# Multi turn example
conv = Conversation()

conv.turn(
    prompt_template="You are a helpful assistant. My name is {{name}}.",
    variables={"name": "Alex"}
)

response = conv.turn(
    prompt_template="{{question}}",
    variables={"question": "What is my name?"}
)
print(response)