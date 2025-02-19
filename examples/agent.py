from enum import Enum
from typing import Callable, Optional, Union

from examples.lm_studio import *


# Message and Role definitions remain the same
class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    role: Role
    content: str
    name: Optional[str] = None


class AgentConfig(BaseModel):
    model: str = "qwen2.5-coder-1.5b-instruct"
    temperature: float = 0.7
    max_tokens: int = -1
    stream: bool = False
    system_prompt: str = "You are a helpful AI assistant."
    exit_commands: list = ["exit", "quit", "bye", "goodbye"]


class Agent:
    def __init__(
        self,
        config: AgentConfig,
        client: Union['LmStudio', 'AsyncLmStudio'],
        message_processor: Optional[Callable[[str], str]] = None
    ):
        self.config = config
        self.client = client
        self.message_processor = message_processor or (lambda x: x)
        self.conversation_history: List[Message] = []
        self._initialize_conversation()

    def _initialize_conversation(self):
        """Initialize the conversation with the system prompt"""
        self.conversation_history = []  # Clear existing history
        self.conversation_history.append(
            Message(role=Role.SYSTEM, content=self.config.system_prompt)
        )

    def _prepare_messages(self) -> dict:
        """Prepare messages in the format expected by the API"""
        return {
            "model": self.config.model,
            "messages": [msg.model_dump(exclude_none=True) for msg in self.conversation_history],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": self.config.stream
        }

    def add_message(self, content: str, role: Role = Role.USER):
        """Add a message to the conversation history"""
        self.conversation_history.append(Message(role=role, content=content))

    def get_conversation_history(self) -> List[Message]:
        """Get the current conversation history"""
        return self.conversation_history

    def clear_history(self):
        """Clear the conversation history and reinitialize with system prompt"""
        self._initialize_conversation()

    def print_conversation(self, last_n: Optional[int] = None):
        """Print the conversation history, optionally limiting to last n messages"""
        history = self.conversation_history
        if last_n is not None:
            history = history[-last_n:]

        for msg in history:
            if msg.role != Role.SYSTEM:  # Skip system message in display
                prefix = "User: " if msg.role == Role.USER else "Assistant: "
                print(f"\n{prefix}{msg.content}")

    def is_exit_command(self, user_input: str) -> bool:
        """Check if the user input is an exit command"""
        return user_input.lower().strip() in self.config.exit_commands

    async def async_generate_response(self) -> str:
        """Generate a response using the async client"""
        if not isinstance(self.client, AsyncLmStudio):
            raise ValueError("Async generation requires an AsyncLmStudio client")

        messages = self._prepare_messages()
        response = await self.client.chat_completions(BodyMap(messages))

        if response.choices:
            content = response.choices[0].get('message', {}).get('content', '')
            processed_content = self.message_processor(content)
            self.add_message(processed_content, Role.ASSISTANT)
            return processed_content
        return ""

    def generate_response(self) -> str:
        """Generate a response using the sync client"""
        if not isinstance(self.client, LmStudio):
            raise ValueError("Sync generation requires a LmStudio client")

        messages = self._prepare_messages()
        response = self.client.chat_completions(BodyMap(messages))

        if response.choices:
            content = response.choices[0].get('message', {}).get('content', '')
            processed_content = self.message_processor(content)
            self.add_message(processed_content, Role.ASSISTANT)
            return processed_content
        return ""

    def start_conversation(self):
        """Start an interactive conversation loop"""
        print("\nStarting conversation. Type 'exit', 'quit', 'bye', or 'goodbye' to end the chat.")
        print("Special commands:")
        print("  !clear - Clear conversation history")
        print("  !history - Show conversation history")
        print("-" * 50)

        while True:
            try:
                user_input = input("\nYou: ").strip()

                # Handle special commands
                if user_input.lower() == "!clear":
                    self.clear_history()
                    print("Conversation history cleared.")
                    continue
                elif user_input.lower() == "!history":
                    self.print_conversation()
                    continue
                elif self.is_exit_command(user_input):
                    print("\nGoodbye! Thanks for chatting.")
                    break
                elif not user_input:
                    print("Please enter a message.")
                    continue

                # Add user message and generate response
                self.add_message(user_input)
                response = self.generate_response()
                print(response)

            except KeyboardInterrupt:
                print("\nConversation interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\nAn error occurred: {str(e)}")
                print("Please try again.")


# Usage example
if __name__ == "__main__":
    # Initialize configuration
    config = AgentConfig(
        model="qwen2.5-coder-14b-instruct",
        system_prompt="""your system prompt"""
    )

    # Initialize sync client
    sync_client = LmStudio(
        base_url="http://localhost:1234",
        default_headers={
            "Content-Type": "application/json",
            "Authorization": get_dynamic_lm_studio_token
        },
        timeout=None
    )

    # Create and start conversation with sync agent
    sync_agent = Agent(config=config, client=sync_client)
    sync_agent.start_conversation()
