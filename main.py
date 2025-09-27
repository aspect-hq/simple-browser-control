#!/usr/bin/env python3
"""Simple Browser Control - Main application entry point."""

import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import logging
from typing import Optional

from dotenv import load_dotenv
from colorama import Fore, Style, init

from aspect_sdk import Aspect, AspectConfig
from browser import BrowserController
from logger import setup_logging


# Initialize colorama for cross-platform colored output
init(autoreset=True)

logger = logging.getLogger(__name__)


class BrowserControlApp:
    """Main application class for browser control."""
    
    def __init__(self) -> None:
        """Initialize the application."""
        self.browser: Optional[BrowserController] = None
        self.aspect_client: Optional[Aspect] = None
        self.running = True
    
    def print_banner(self) -> None:
        """Print the application banner."""
        banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                    SIMPLE BROWSER CONTROL                   ║
║                     Powered by Aspect SDK                   ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.YELLOW}This is a testing environment for browser use. You are acting as the
autonomous agent and your available function calls are:{Style.RESET_ALL}

{Fore.GREEN}  navigate <url>  {Style.RESET_ALL}- Navigate to a webpage
{Fore.GREEN}  locate <query>  {Style.RESET_ALL}- Find and mark elements on the page
{Fore.GREEN}  resize <w> <h>  {Style.RESET_ALL}- Resize browser window
{Fore.GREEN}  exit            {Style.RESET_ALL}- Close browser and quit

{Fore.CYAN}═══════════════════════════════════════════════════════════════{Style.RESET_ALL}
"""
        print(banner)
    
    def print_prompt(self) -> None:
        """Print the command prompt."""
        print(f"\n{Fore.MAGENTA}What would you like to get started with?{Style.RESET_ALL}")
        print(f"{Fore.BLUE}> {Style.RESET_ALL}", end="")
    
    def setup(self) -> bool:
        """Setup the application components.
        
        Returns:
            True if setup successful, False otherwise
        """
        try:
            # Check for .env file first
            if not self._check_env_file():
                return False
            
            # Load environment variables
            load_dotenv()
            
            # Setup logging
            setup_logging()
            logger.info("Starting Simple Browser Control application")
            
            # Show environment status
            self._show_env_status()
            
            # Get window size from user
            window_size = self._get_window_size()
            
            # Initialize browser
            logger.info("Initializing browser...")
            self.browser = BrowserController(
                window_width=window_size[0],
                window_height=window_size[1]
            )
            
            # Initialize Aspect client
            logger.info("Initializing Aspect client...")
            self.aspect_client = self._create_aspect_client()
            
            logger.info("Application setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            print(f"{Fore.RED}Error: Failed to initialize application: {e}{Style.RESET_ALL}")
            return False
    
    def _check_env_file(self) -> bool:
        """Check if .env file exists.
        
        Returns:
            True if .env exists, False otherwise
        """
        env_path = Path(".env")
        if not env_path.exists():
            print(f"{Fore.RED}Error: .env file not found{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please create a .env file from env.example:{Style.RESET_ALL}")
            print(f"  {Fore.CYAN}cp env.example .env{Style.RESET_ALL}")
            print(f"  {Fore.CYAN}# Then edit .env with your ASPECT_API_KEY{Style.RESET_ALL}")
            return False
        return True
    
    def _show_env_status(self) -> None:
        """Show environment configuration status."""
        mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
        api_key = os.getenv("ASPECT_API_KEY")
        
        print(f"\n{Fore.CYAN}Environment Configuration:{Style.RESET_ALL}")
        
        if mock_mode:
            print(f"  {Fore.YELLOW}Mode: MOCK MODE (no API calls){Style.RESET_ALL}")
            print(f"  {Fore.YELLOW}You will be prompted for X,Y coordinates{Style.RESET_ALL}")
        else:
            if api_key:
                # Show only first/last few chars of API key for security
                masked_key = f"{api_key[:7]}...{api_key[-4:]}" if len(api_key) > 11 else "***"
                print(f"  {Fore.GREEN}Mode: REAL API MODE{Style.RESET_ALL}")
                print(f"  {Fore.GREEN}API Key: {masked_key}{Style.RESET_ALL}")
            else:
                print(f"  {Fore.YELLOW}Mode: MOCK MODE (no API key found){Style.RESET_ALL}")
                print(f"  {Fore.YELLOW}Falling back to manual coordinate input{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}═══════════════════════════════════════════════════════════════{Style.RESET_ALL}")

    def _create_aspect_client(self) -> Optional[Aspect]:
        """Create Aspect SDK client or return None for mock mode."""
        mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
        api_key = os.getenv("ASPECT_API_KEY")
        
        if mock_mode:
            logger.info("Mock mode enabled - no Aspect client created")
            return None
        
        if not api_key:
            logger.warning("No API key found - falling back to mock mode")
            return None
        
        try:
            config = AspectConfig(api_key=api_key)
            client = Aspect(config)
            logger.info("Aspect SDK client created successfully")
            return client
        except Exception as e:
            logger.error(f"Failed to create Aspect client: {e}")
            return None

    def _get_window_size(self) -> tuple[int, int]:
        """Get browser window size from user.
        
        Returns:
            Tuple of (width, height)
        """
        print(f"\n{Fore.CYAN}Browser Window Configuration{Style.RESET_ALL}")
        print("Enter browser window size (default: 1920x1080)")
        
        try:
            width_input = input(f"{Fore.BLUE}Width (default 1920): {Style.RESET_ALL}").strip()
            width = int(width_input) if width_input else 1920
            
            height_input = input(f"{Fore.BLUE}Height (default 1080): {Style.RESET_ALL}").strip()
            height = int(height_input) if height_input else 1080
            
            if width < 400 or height < 300:
                print(f"{Fore.YELLOW}Warning: Small window size may affect functionality{Style.RESET_ALL}")
            
            return width, height
            
        except ValueError:
            print(f"{Fore.YELLOW}Invalid input, using default size 1920x1080{Style.RESET_ALL}")
            return 1920, 1080
    
    def run(self) -> None:
        """Run the main application loop."""
        if not self.setup():
            return
        
        self.print_banner()
        
        try:
            while self.running:
                self.print_prompt()
                
                try:
                    command = input().strip()
                    if not command:
                        continue
                    
                    self.handle_command(command)
                    
                except (EOFError, KeyboardInterrupt):
                    print(f"\n{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
                    break
                    
        except Exception as e:
            logger.error(f"Application error: {e}")
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        finally:
            self.cleanup()
    
    def handle_command(self, command: str) -> None:
        """Handle user commands.
        
        Args:
            command: User input command
        """
        parts = command.split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd == "navigate":
            self.handle_navigate(args)
        elif cmd == "locate":
            self.handle_locate(args)
        elif cmd == "resize":
            self.handle_resize(args)
        elif cmd == "exit":
            self.handle_exit()
        else:
            print(f"{Fore.RED}Unknown command: {cmd}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Available commands: navigate, locate, resize, exit{Style.RESET_ALL}")
    
    def handle_navigate(self, args: list[str]) -> None:
        """Handle navigate command.
        
        Args:
            args: Command arguments
        """
        if not args:
            print(f"{Fore.RED}Error: Please provide a URL{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Usage: navigate <url>{Style.RESET_ALL}")
            return
        
        url = " ".join(args)
        
        if not self.browser:
            print(f"{Fore.RED}Error: Browser not initialized{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}Navigating to: {url}{Style.RESET_ALL}")
        
        if self.browser.navigate(url):
            current_url = self.browser.get_current_url()
            print(f"{Fore.GREEN}Successfully navigated to: {current_url}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Failed to navigate to: {url}{Style.RESET_ALL}")
    
    def handle_locate(self, args: list[str]) -> None:
        """Handle locate command.
        
        Args:
            args: Command arguments
        """
        if not args:
            print(f"{Fore.RED}Error: Please provide a search query{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Usage: locate <query>{Style.RESET_ALL}")
            return
        
        query = " ".join(args)
        
        if not self.browser:
            print(f"{Fore.RED}Error: Browser not initialized{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}Locating: {query}{Style.RESET_ALL}")
        
        # Take screenshot
        screenshot = self.browser.take_screenshot()
        if not screenshot:
            print(f"{Fore.RED}Failed to capture screenshot{Style.RESET_ALL}")
            return
        
        # Check if we're in mock mode
        mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
        
        if mock_mode or not self.aspect_client:
            # Mock mode - ask user for coordinates
            points = self._mock_analyze(query)
        else:
            # Real API mode
            points = self._real_analyze(screenshot, query)
        
        if not points:
            print(f"{Fore.YELLOW}No points found for query: {query}{Style.RESET_ALL}")
            return
        
        if len(points) == 1:
            # Single point - show and offer to click
            point = points[0]
            print(f"{Fore.GREEN}Found target at ({point['x']}, {point['y']}){Style.RESET_ALL}")
            
            # Show the point on screen
            if self.browser.show_point(point['x'], point['y']):
                self._handle_click_confirmation(point['x'], point['y'])
            else:
                print(f"{Fore.RED}Failed to display point on screen{Style.RESET_ALL}")
        else:
            # Multiple points - show all but don't allow clicking
            print(f"{Fore.YELLOW}Found {len(points)} points (multiple targets detected):{Style.RESET_ALL}")
            for i, point in enumerate(points, 1):
                print(f"  {i}. ({point['x']}, {point['y']})")
                self.browser.show_point(point['x'], point['y'])
            
            print(f"{Fore.YELLOW}Multiple points found - please try a more specific query{Style.RESET_ALL}")
    
    def _mock_analyze(self, query: str) -> list[dict]:
        """Mock analysis - ask user for coordinates."""
        print(f"\n[MOCK MODE] Query: '{query}'")
        print("Please provide X and Y coordinates where you want to click:")
        
        try:
            x_input = input("X coordinate: ").strip()
            y_input = input("Y coordinate: ").strip()
            
            x = int(x_input)
            y = int(y_input)
            
            if x < 0 or y < 0:
                raise ValueError("Coordinates must be non-negative")
            
            return [{"x": x, "y": y}]
            
        except (ValueError, EOFError) as e:
            logger.error(f"Invalid coordinates provided: {e}")
            return []
    
    def _real_analyze(self, screenshot_bytes: bytes, query: str) -> list[dict]:
        """Real Aspect SDK analysis."""
        try:
            from aspect_sdk import IndexCreateRequest, AssetCreateRequest, AnalyzePointRequest, WaitForDoneOptions
            import io
            import time
            
            # Create index if needed
            index_id = self._ensure_index()
            if not index_id:
                logger.error("Failed to create/get index")
                return []
            
            # Upload screenshot as asset
            timestamp = int(time.time())
            asset_name = f"screenshot_{timestamp}.png"
            
            asset_request = AssetCreateRequest(
                index_id=index_id,
                name=asset_name,
                asset_file=io.BytesIO(screenshot_bytes),
                save_original=True,
                features=['embedding']
            )
            
            logger.info("Uploading screenshot...")
            asset_response = self.aspect_client.assets.create(asset_request)
            asset_id = asset_response.asset_id
            task_id = asset_response.task_id
            
            # Wait for processing
            logger.info("Waiting for processing...")
            self.aspect_client.tasks.wait_for_done(task_id, WaitForDoneOptions(
                interval=2000,
                timeout=30000
            ))
            
            # Analyze
            analyze_request = AnalyzePointRequest(
                asset_id=asset_id,
                query=query
            )
            
            result = self.aspect_client.analyze.point(analyze_request)
            
            # Parse points
            points = []
            if hasattr(result, 'points') and result.points:
                for point_coord in result.points:
                    if hasattr(point_coord, 'x') and hasattr(point_coord, 'y'):
                        points.append({"x": int(point_coord.x), "y": int(point_coord.y)})
            
            return points
            
        except Exception as e:
            logger.error(f"Aspect analysis failed: {e}")
            return []
    
    def _ensure_index(self) -> Optional[str]:
        """Ensure we have an index for screenshots."""
        try:
            from aspect_sdk import IndexCreateRequest
            import time
            
            timestamp = int(time.time())
            index_request = IndexCreateRequest(
                name=f'Browser Screenshots {timestamp}',
                description='Screenshots for browser automation',
                features=['embedding']
            )
            
            index_response = self.aspect_client.indexes.create(index_request)
            return index_response.id
            
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            return None

    def _handle_click_confirmation(self, x: int, y: int) -> None:
        """Handle click confirmation dialog.
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        print(f"\n{Fore.MAGENTA}Point marked at ({x}, {y}){Style.RESET_ALL}")
        
        while True:
            response = input(f"{Fore.BLUE}Confirm click? (yes/no): {Style.RESET_ALL}").strip().lower()
            
            if response in ("yes", "y"):
                # Hide the point first
                self.browser.hide_points()
                
                # Perform the click
                if self.browser.click_at(x, y):
                    print(f"{Fore.GREEN}Clicked at ({x}, {y}){Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Failed to click at ({x}, {y}){Style.RESET_ALL}")
                break
                
            elif response in ("no", "n", "ignore"):
                # Hide the point and return to main prompt
                self.browser.hide_points()
                print(f"{Fore.YELLOW}Click cancelled{Style.RESET_ALL}")
                break
                
            else:
                print(f"{Fore.YELLOW}Please enter 'yes' or 'no'{Style.RESET_ALL}")
    
    def handle_resize(self, args: list[str]) -> None:
        """Handle resize command.
        
        Args:
            args: Command arguments
        """
        if len(args) != 2:
            print(f"{Fore.RED}Error: Please provide width and height{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Usage: resize <width> <height>{Style.RESET_ALL}")
            return
        
        try:
            width = int(args[0])
            height = int(args[1])
            
            if width < 400 or height < 300:
                print(f"{Fore.YELLOW}Warning: Very small window size may affect functionality{Style.RESET_ALL}")
            
            if not self.browser:
                print(f"{Fore.RED}Error: Browser not initialized{Style.RESET_ALL}")
                return
            
            print(f"{Fore.CYAN}Resizing window to {width}x{height}{Style.RESET_ALL}")
            
            if self.browser.resize_window(width, height):
                print(f"{Fore.GREEN}Window resized successfully{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Failed to resize window{Style.RESET_ALL}")
                
        except ValueError:
            print(f"{Fore.RED}Error: Width and height must be numbers{Style.RESET_ALL}")
    
    def handle_exit(self) -> None:
        """Handle exit command."""
        print(f"{Fore.CYAN}Shutting down...{Style.RESET_ALL}")
        self.running = False
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.browser:
            self.browser.close()
        logger.info("Application shutdown completed")


def main() -> None:
    """Main entry point."""
    app = BrowserControlApp()
    app.run()


if __name__ == "__main__":
    main()
