"""Browser controller for Chrome with Selenium."""

import logging
import time
from typing import Optional, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class BrowserController:
    """Manages Chrome browser session with Selenium."""

    def __init__(self, window_width: int = 1920, window_height: int = 1080) -> None:
        """Initialize browser controller.
        
        Args:
            window_width: Browser window width
            window_height: Browser window height
        """
        self.driver: Optional[webdriver.Chrome] = None
        self.window_width = window_width
        self.window_height = window_height
        self._setup_browser()

    def _setup_browser(self) -> None:
        """Setup Chrome browser with appropriate options."""
        chrome_options = Options()
        
        # Window size and display settings
        chrome_options.add_argument(f"--window-size={self.window_width},{self.window_height}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        
        # Keep browser open if process crashes for debugging
        chrome_options.add_experimental_option("detach", True)
        
        # Reduce automation detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # Realistic user agent
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )

        try:
            # Try to use system Chrome first
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception:
            # Fallback to webdriver-manager
            logger.info("Using webdriver-manager to install ChromeDriver")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

        if self.driver:
            # Further reduce automation detection
            try:
                self.driver.execute_cdp_cmd(
                    "Page.addScriptToEvaluateOnNewDocument",
                    {
                        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                    },
                )
            except Exception as e:
                logger.debug(f"Could not patch webdriver detection: {e}")

            # Set window size explicitly
            self.driver.set_window_size(self.window_width, self.window_height)
            logger.info(f"Browser initialized with size {self.window_width}x{self.window_height}")

    def navigate(self, url: str) -> bool:
        """Navigate to a URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            True if navigation successful, False otherwise
        """
        if not self.driver:
            logger.error("Browser not initialized")
            return False
            
        try:
            # Add protocol if missing
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
                
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            time.sleep(2)  # Wait for page load
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False

    def take_screenshot(self) -> Optional[bytes]:
        """Take a screenshot of the current viewport.
        
        Returns:
            Screenshot as bytes, or None if failed
        """
        if not self.driver:
            logger.error("Browser not initialized")
            return None
            
        try:
            screenshot_bytes = self.driver.get_screenshot_as_png()
            logger.info("Screenshot captured successfully")
            return screenshot_bytes
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None

    def click_at(self, x: int, y: int) -> bool:
        """Click at specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if click successful, False otherwise
        """
        if not self.driver:
            logger.error("Browser not initialized")
            return False
            
        try:
            # Create action chain for precise clicking
            actions = ActionChains(self.driver)
            actions.move_by_offset(x, y).click().perform()
            
            # Reset action chain
            actions.reset_actions()
            
            logger.info(f"Clicked at coordinates ({x}, {y})")
            time.sleep(1)  # Brief pause after click
            return True
        except Exception as e:
            logger.error(f"Click failed at ({x}, {y}): {e}")
            return False

    def show_point(self, x: int, y: int) -> bool:
        """Display a neon pink dot at the specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if dot displayed successfully, False otherwise
        """
        if not self.driver:
            logger.error("Browser not initialized")
            return False
            
        try:
            # JavaScript to create and display a neon pink dot
            js_code = f"""
            // Remove any existing dots
            const existingDots = document.querySelectorAll('.aspect-click-dot');
            existingDots.forEach(dot => dot.remove());
            
            // Create new dot
            const dot = document.createElement('div');
            dot.className = 'aspect-click-dot';
            dot.style.position = 'fixed';
            dot.style.left = '{x - 10}px';  // Center the 20px dot
            dot.style.top = '{y - 10}px';
            dot.style.width = '20px';
            dot.style.height = '20px';
            dot.style.backgroundColor = '#ff00ff';  // Neon pink
            dot.style.borderRadius = '50%';
            dot.style.zIndex = '9999';
            dot.style.pointerEvents = 'none';
            dot.style.boxShadow = '0 0 10px #ff00ff, 0 0 20px #ff00ff';
            dot.style.border = '2px solid #ffffff';
            
            // Add pulsing animation
            dot.style.animation = 'pulse 1s infinite';
            
            // Add CSS animation if not already present
            if (!document.querySelector('#aspect-dot-styles')) {{
                const style = document.createElement('style');
                style.id = 'aspect-dot-styles';
                style.textContent = `
                    @keyframes pulse {{
                        0% {{ transform: scale(1); opacity: 1; }}
                        50% {{ transform: scale(1.2); opacity: 0.8; }}
                        100% {{ transform: scale(1); opacity: 1; }}
                    }}
                `;
                document.head.appendChild(style);
            }}
            
            document.body.appendChild(dot);
            """
            
            self.driver.execute_script(js_code)
            logger.info(f"Displayed neon pink dot at ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Failed to show point at ({x}, {y}): {e}")
            return False

    def hide_points(self) -> bool:
        """Hide all displayed points.
        
        Returns:
            True if points hidden successfully, False otherwise
        """
        if not self.driver:
            logger.error("Browser not initialized")
            return False
            
        try:
            js_code = """
            const dots = document.querySelectorAll('.aspect-click-dot');
            dots.forEach(dot => dot.remove());
            """
            self.driver.execute_script(js_code)
            logger.info("Hidden all click points")
            return True
        except Exception as e:
            logger.error(f"Failed to hide points: {e}")
            return False

    def resize_window(self, width: int, height: int) -> bool:
        """Resize the browser window.
        
        Args:
            width: New window width
            height: New window height
            
        Returns:
            True if resize successful, False otherwise
        """
        if not self.driver:
            logger.error("Browser not initialized")
            return False
            
        try:
            self.driver.set_window_size(width, height)
            self.window_width = width
            self.window_height = height
            logger.info(f"Resized window to {width}x{height}")
            time.sleep(1)  # Brief pause after resize
            return True
        except Exception as e:
            logger.error(f"Resize failed: {e}")
            return False

    def get_current_url(self) -> Optional[str]:
        """Get the current URL.
        
        Returns:
            Current URL or None if failed
        """
        if not self.driver:
            return None
        try:
            return self.driver.current_url
        except Exception as e:
            logger.error(f"Failed to get current URL: {e}")
            return None

    def close(self) -> None:
        """Close the browser."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
            finally:
                self.driver = None
