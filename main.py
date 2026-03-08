#!/usr/bin/env python3
"""
Browser-Use Interactive CLI Application
Control browser with natural language commands
"""

import asyncio
import os
import signal
import sys
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fix Windows console encoding for Unicode
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from browser_use import Agent
from browser_use.browser.profile import BrowserProfile
from browser_use.browser.session import BrowserSession
from browser_use.controller import Controller
import logging

# Configure logging with timestamps and file output
import os
from datetime import datetime
os.makedirs("logs", exist_ok=True)
log_filename = datetime.now().strftime("logs/run_%Y%m%d_%H%m%S.log")

log_formatter = logging.Formatter('%(asctime)s - %(levelname)-8s [%(name)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Configure root logger to output DEBUG to file
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_formatter)
root_logger.addHandler(file_handler)

# Disable excessive HTTP request logs in debug output unless it's a warning
logging.getLogger("httpx").setLevel(logging.WARNING)

# Reconfigure browser-use logger
browser_logger = logging.getLogger('browser_use')
browser_logger.propagate = True
browser_logger.setLevel(logging.DEBUG)  # Capture all debug details

# Clear existing handlers from browser_logger to prevent duplicates
if browser_logger.handlers:
    for h in browser_logger.handlers[:]:
        browser_logger.removeHandler(h)

# Add console handler to browser_use (INFO level)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_formatter)
browser_logger.addHandler(console_handler)

# Optionally also capture langchain debug logs in the file
langchain_logger = logging.getLogger('langchain')
langchain_logger.setLevel(logging.DEBUG)
langchain_logger.propagate = True


class BrowserManager:
    """Browser Manager - Handles browser lifecycle"""

    def __init__(self, mode="screen"):
        self.mode = mode
        self.browser_profile: Optional[BrowserProfile] = None
        self.browser_session: Optional[BrowserSession] = None
        self.controller: Optional[Controller] = None
        self.llm_config = None  # List of LLM instances
        self.current_model_index = 0  # Track current model for fallback
        self.agent: Optional[Agent] = None
        self.is_initialized = False

    async def initialize(self):
        """Initialize browser profile and controller"""
        if self.is_initialized:
            return

        # Create browser profile - visible mode with persistent session
        # Use user_data_dir to persist cookies, login states, and browser settings
        user_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_data")

        # Kill any existing browser processes using this data directory to prevent conflicts
        if sys.platform == "win32":
            try:
                # Format path for WQL command line matching
                wql_path = user_data_dir.replace("\\", "\\\\")
                os.system(f'wmic process where "name=\'chrome.exe\' and commandline like \'%%{wql_path}%%\'" call terminate >nul 2>&1')
            except Exception:
                pass
        self.browser_profile = BrowserProfile(
            headless=False,  # Visible mode
            keep_alive=True,  # Keep browser alive after agent runs
            user_data_dir=user_data_dir,  # Persist browser data (cookies, sessions, etc.)
        )

        # Create browser session and start it immediately
        # This opens the browser and keeps it waiting for commands
        self.browser_session = BrowserSession(
            browser_profile=self.browser_profile,
        )
        await self.browser_session.start()
        print("[OK] Browser opened and waiting")

        # Create controller
        self.controller = Controller()
        
        # Add custom action to read local files bypassing browser-use restrictions
        @self.controller.action('Read a local file from the computer. Use this for reading specific files provided by the user using their absolute path. Supports reading only a specific line range.')
        async def read_local_file(file_path: str, start_line: int = 1, end_line: Optional[int] = None):
            import os
            try:
                if not os.path.exists(file_path):
                    return f"Error: File not found at {file_path}"
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                start_idx = max(0, start_line - 1)
                end_idx = end_line if end_line is not None else len(lines)
                content = "".join(lines[start_idx:end_idx])
                return f"Successfully read {file_path} (lines {start_line} to {end_line or len(lines)}):\n\n{content}"
            except Exception as e:
                return f"Error reading file {file_path}: {str(e)}"

        @self.controller.action('Read a local file and directly input/paste its content into the specified element by index. Supports starting from a specific line. Extremely useful for pasting large amounts of text (e.g., novel chapters starting from line 2 to skip titles) into a text box without hallucination or truncation.')
        async def fill_from_file(index: int, file_path: str, browser_session: BrowserSession, start_line: int = 1, end_line: Optional[int] = None):
            import os
            from browser_use.browser.events import TypeTextEvent
            try:
                if not os.path.exists(file_path):
                    return f"Error: File not found at {file_path}"
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                start_idx = max(0, start_line - 1)
                end_idx = end_line if end_line is not None else len(lines)
                content = "".join(lines[start_idx:end_idx])
                
                node = await browser_session.get_element_by_index(index)
                if node is None:
                    return f"Error: Element index {index} not available."
                
                # Get CDP session for this node to execute JS directly
                # This bypasses TypeTextEvent character-by-character typing which causes newline duplication
                cdp_session = await browser_session.cdp_client_for_node(node)
                
                # Resolve node to get objectId
                result = await cdp_session.cdp_client.send.DOM.resolveNode(
                    params={'backendNodeId': node.backend_node_id},
                    session_id=cdp_session.session_id,
                )
                
                if 'object' not in result or 'objectId' not in result['object']:
                    return f"Error: Could not resolve DOM element for index {index}."
                    
                object_id = result['object']['objectId']
                
                # JS to focus, select all, and insert text as a single paste operation
                js_code = """
                function(text) {
                    this.focus();
                    try {
                        // This behaves exactly like pasting from the clipboard
                        document.execCommand('selectAll', false, null);
                        document.execCommand('insertText', false, text);
                    } catch (e) {
                        // Fallback for simple textareas or inputs
                        this.value = text;
                        this.dispatchEvent(new Event('input', { bubbles: true }));
                        this.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
                """
                
                await cdp_session.cdp_client.send.Runtime.callFunctionOn(
                    params={
                        'functionDeclaration': js_code,
                        'objectId': object_id,
                        'arguments': [{'value': content}],
                        'awaitPromise': True,
                    },
                    session_id=cdp_session.session_id,
                )
                
                return f"Successfully read {file_path} and pasted its content into element {index}."
            except Exception as e:
                return f"Error filling file content: {str(e)}"

        # Get and store LLM configuration
        self.llm_config = self._get_llm_config()

        self.is_initialized = True
        print("[OK] Browser initialized")

    def _get_llm_config(self):
        """Get LLM configuration from environment - supports multiple models"""
        from browser_use.llm import ChatOpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        model_names = os.getenv("MODEL_NAME", "gpt-4o")

        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")

        # Support multiple models (comma-separated)
        model_list = [m.strip() for m in model_names.split(",")]

        # Create LLM instances for each model
        llms = []
        for model_name in model_list:
            llm = ChatOpenAI(
                model=model_name,
                api_key=api_key,
                base_url=api_base,
                temperature=0.1,
                frequency_penalty=None, # Fix Gemini error: "Unknown name frequency_penalty"
                timeout=120,
            )
            llms.append(llm)

        print(f"[OK] Loaded {len(llms)} model(s): {model_list}")
        return llms

    async def execute_command(self, command: str) -> str:
        """
        Execute a single command

        Args:
            command: Natural language command, e.g. "open google"

        Returns:
            Execution result description
        """
        if not self.is_initialized:
            await self.initialize()

        if not command.strip():
            return "Command cannot be empty"

        try:
            print(f"Executing: {command}")

            # Get current and next model (for fallback)
            llms = self.llm_config
            current_idx = self.current_model_index
            primary_llm = llms[current_idx]

            # Set fallback to next model in list (cycle through)
            next_idx = (current_idx + 1) % len(llms)
            fallback_llm = llms[next_idx]

            print(f"[INFO] Using model: {primary_llm.model} (fallback: {fallback_llm.model})")
            
            use_vision = self.mode != "dom"
            print(f"[INFO] Using vision: {use_vision}")
            
            # Add instruction for screen mode to encourage scrolling
            system_message = None
            file_instruction = (
                "\n\nCRITICAL INSTRUCTION FOR LOCAL FILES:\n"
                "1. STRICTLY use the `read_local_file` action to read files, OR use `fill_from_file` if you need to directly input the file's content into a text box (like pasting a novel chapter).\n"
                "2. NEVER alter the directory path or folder names provided by the user.\n"
                "3. If the user provides a path with a placeholder like `C:\\Code\\iNovel-v2.3\\data\\chapters\\chapter-[序号].txt`, you MUST KEEP the EXACT directory structure `C:\\Code\\iNovel-v2.3\\data\\chapters\\`.\n"
                "4. Only replace the placeholder `[序号]` with the calculated number (e.g., 131). DO NOT invent or substitute directory names like `fanqie_auto_publlish` or `...`.\n"
                "5. The final file path MUST perfectly match the path prefix given in the instructions."
            )

            if use_vision:
                system_message = (
                    "You are in screen mode and only see the current viewport. "
                    "If you need to extract multiple items (e.g., top 10 news) but only see a few in the current viewport, "
                    "DO NOT hallucinate or guess the remaining items. "
                    "You MUST use the `scroll` action to scroll down, view more of the page, and collect the items across multiple steps. "
                    "Only use the `done` action once you have actually seen and collected all requested information."
                    + file_instruction
                )
            else:
                system_message = file_instruction

            # Recreate agent for each command so they are independent
            self.agent = Agent(
                task=command,
                browser_session=self.browser_session,  # Use existing browser session
                controller=self.controller,
                llm=primary_llm,
                fallback_llm=fallback_llm,
                use_thinking=False,  # Disable thinking for better compatibility
                llm_timeout=120,     # Increase default LLM timeout
                use_vision=use_vision,
                extend_system_message=system_message,
            )

            # Execute with enough steps to allow for scrolling and multiple extractions
            result = await self.agent.run(max_steps=50)

            # Check if execution was successful, if not, try next model
            success, error_msg = self._check_execution_success(result)
            if not success and len(llms) > 1:
                # Try with next model
                print(f"[WARN] Model {primary_llm.model} failed: {error_msg}")
                print(f"[INFO] Trying next model: {fallback_llm.model}...")
                self.current_model_index = next_idx
                # Recreate agent with new model for retry
                self.agent = None
                return await self.execute_command(command)

            # Extract meaningful summary from result
            summary = self._extract_summary(result)
            return summary

        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            print(error_msg)

            # Try next model on error
            llms = self.llm_config
            if len(llms) > 1:
                next_idx = (self.current_model_index + 1) % len(llms)
                print(f"[INFO] Retrying with model: {llms[next_idx].model}")
                self.current_model_index = next_idx
                # Recreate agent with new model for retry
                self.agent = None
                return await self.execute_command(command)

            return error_msg

    def _check_execution_success(self, result):
        """
        Check if the agent execution was successful
        
        Returns:
            tuple: (success: bool, error_message: str)
        """
        try:
            # Check if there are any results
            if hasattr(result, 'all_results') and result.all_results:
                return True, ""

            # Check history for errors
            if hasattr(result, 'history') and result.history:
                for step in result.history:
                    if hasattr(step, 'error') and step.error:
                        return False, str(step.error)
                return True, ""

            # If no clear results, check if it's a "failed" state
            if hasattr(result, 'history') and not result.history:
                return False, "No history results"

            return True, ""  # Assume success if we can't determine
        except Exception as e:
            return False, str(e)

    def _extract_summary(self, result) -> str:
        """Extract a human-readable summary from agent result"""
        try:
            # Check if result has all_results (newer browser-use versions)
            if hasattr(result, 'all_results') and result.all_results:
                last_result = result.all_results[-1]
                if hasattr(last_result, 'extracted_content') and last_result.extracted_content:
                    content = str(last_result.extracted_content)
                    if len(content) > 500:
                        return content[:500] + "..."
                    return content

            # Fallback to history attribute
            if hasattr(result, 'history') and result.history:
                last_result = result.history[-1]
                if hasattr(last_result, 'extracted_content') and last_result.extracted_content:
                    content = str(last_result.extracted_content)
                    if len(content) > 500:
                        return content[:500] + "..."
                    return content

            # Check for errors in the result
            if hasattr(result, 'history') and result.history:
                for step in result.history:
                    if hasattr(step, 'error') and step.error:
                        return f"Error: {step.error}"

            return "Command completed successfully"
        except Exception as e:
            return f"Command completed (result parsing: {str(e)})"

    async def close(self):
        """Close browser"""
        try:
            if getattr(self, "browser_session", None):
                if hasattr(self.browser_session, "stop"):
                    await self.browser_session.stop()
                elif hasattr(self.browser_session, "close"):
                    await self.browser_session.close()
                elif hasattr(self.browser_session, "browser") and hasattr(self.browser_session.browser, "close"):
                    await self.browser_session.browser.close()
                print("[OK] Browser closed")
        except Exception as e:
            print(f"[WARN] Error closing browser: {e}")
        self.agent = None
        self.browser_session = None
        self.is_initialized = False


class CLIInterface:
    """Command Line Interface - Handles user input and output"""

    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager
        self.running = True

    def print_welcome(self):
        """Display welcome message"""
        print("\n" + "=" * 60)
        print("Browser-Use Interactive Console")
        print("=" * 60)
        print("Enter natural language commands to control browser, e.g.:")
        print(" - open google")
        print(" - close cookie popup")
        print(" - search for Python tutorials")
        print(" - click login button")
        print("\nSpecial commands:")
        print(" - help: show this help")
        print(" - status: show browser status")
        print(" - exit/quit: exit program")
        print("=" * 60 + "\n")

    def print_status(self):
        """Display browser status"""
        if self.browser_manager.is_initialized:
            print("[OK] Browser initialized")
        else:
            print("[ERROR] Browser not initialized")

    async def process_command(self, command: str) -> bool:
        """
        Process user command

        Returns:
            True to continue, False to exit
        """
        command = command.strip()

        if not command:
            return True

        # Handle special commands
        if command.lower() in ["exit", "quit"]:
            print("Exiting...")
            return False

        elif command.lower() == "help":
            self.print_welcome()
            return True

        elif command.lower() == "status":
            self.print_status()
            return True

        else:
            # Execute browser command
            result = await self.browser_manager.execute_command(command)
            print(result)
            return True

    async def run(self):
        """Run CLI main loop"""
        self.print_welcome()

        # Initialize browser
        try:
            await self.browser_manager.initialize()
        except Exception as e:
            print(f"[ERROR] Initialization failed: {e}")
            return

        # Main loop
        import concurrent.futures
        import sys
        
        pool = concurrent.futures.ThreadPoolExecutor(1)
        while self.running:
            try:
                # Get user input non-blockingly so we can check browser state
                print("\nCommand > ", end="", flush=True)
                loop = asyncio.get_event_loop()
                input_task = loop.run_in_executor(pool, sys.stdin.readline)
                
                while not input_task.done():
                    await asyncio.sleep(0.5)
                    # Check if browser was manually closed and reconnection failed
                    if hasattr(self.browser_manager, "browser_session") and self.browser_manager.browser_session:
                        bs = self.browser_manager.browser_session
                        if hasattr(bs, "is_cdp_connected") and not bs.is_cdp_connected:
                            # If it's not connected and not reconnecting, it's dead
                            if hasattr(bs, "is_reconnecting") and not bs.is_reconnecting:
                                print("\n\n[ERROR] Browser connection lost or closed. Exiting...")
                                import os
                                os._exit(1)
                
                command = input_task.result()
                if not command:
                    continue
                command = command.strip()

                # Process command
                should_continue = await self.process_command(command)
                if not should_continue:
                    break

            except KeyboardInterrupt:
                print("\n\n[WARN] Interrupted, exiting...")
                break
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"[ERROR] An error occurred: {e}")
                continue


import argparse

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Browser-Use Interactive CLI Application")
    parser.add_argument("-m", "--mode", choices=["dom", "screen"], default="screen",
                        help="Operation mode: 'dom' (text only) or 'screen' (with screenshots/vision)")
    parser.add_argument("-c", "--command", type=str,
                        help="Execute a single command and exit")
    args = parser.parse_args()

    # Create browser manager
    browser_manager = BrowserManager(mode=args.mode)

    # Create CLI interface
    cli = CLIInterface(browser_manager)

    # Set up signal handling
    def signal_handler(sig, frame):
        print("\n\nExiting...")
        cli.running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        if args.command:
            # Execute single command and exit
            await browser_manager.initialize()
            print(f"\nExecuting command: {args.command}")
            result = await browser_manager.execute_command(args.command)
            print(result)
        else:
            # Run CLI
            await cli.run()
    finally:
        # Cleanup resources
        await browser_manager.close()
        if args.command:
            import os
            os._exit(0)


if __name__ == "__main__":
    # Run main program
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated")
    except Exception as e:
        print(f"[ERROR] Program failed: {e}")
        sys.exit(1)
