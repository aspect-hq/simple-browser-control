"""Aspect SDK client wrapper with mock mode support."""

import io
import logging
import os
import time
from typing import List, Optional

logger = logging.getLogger(__name__)


class AspectPoint:
    """Represents a point returned by Aspect SDK."""
    
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
    
    def __repr__(self) -> str:
        return f"AspectPoint(x={self.x}, y={self.y})"


class AspectAnalyzeResult:
    """Result from Aspect analyze operation."""
    
    def __init__(self, points: List[AspectPoint]) -> None:
        self.points = points
    
    def __repr__(self) -> str:
        return f"AspectAnalyzeResult(points={self.points})"


class AspectClient:
    """Wrapper for Aspect SDK with mock mode support."""
    
    def __init__(self, api_key: Optional[str] = None, mock_mode: bool = False) -> None:
        """Initialize Aspect client.
        
        Args:
            api_key: Aspect API key
            mock_mode: If True, use mock mode instead of real API
        """
        self.api_key = api_key
        self.mock_mode = mock_mode
        self._client = None
        self._index_id = None
        
        if not mock_mode:
            self._initialize_real_client()
    
    def _initialize_real_client(self) -> None:
        """Initialize the real Aspect SDK client."""
        try:
            from aspect_sdk import Aspect, AspectConfig, IndexCreateRequest
            
            if not self.api_key:
                raise ValueError("API key required for non-mock mode")
            
            config = AspectConfig(api_key=self.api_key)
            self._client = Aspect(config)
            
            # Create or get an index for screenshots
            self._setup_index()
            
            logger.info("Aspect SDK client initialized successfully")
            
        except ImportError:
            logger.error(
                "aspect-sdk not installed. Install with: pip install aspect-sdk"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Aspect client: {e}")
            raise
    
    def _setup_index(self) -> None:
        """Setup or find an index for screenshot analysis."""
        try:
            from aspect_sdk import IndexCreateRequest
            
            # Try to create an index for browser screenshots
            index_request = IndexCreateRequest(
                name='Browser Screenshots',
                description='Screenshots for browser automation analysis',
                features=['embedding']  # Enable embedding for analysis
            )
            
            index_response = self._client.indexes.create(index_request)
            self._index_id = index_response.id
            logger.info(f"Created/using index: {self._index_id}")
            
        except Exception as e:
            # If index creation fails (maybe it already exists), try to list and find it
            logger.warning(f"Index creation failed, trying to find existing: {e}")
            try:
                # For now, we'll try to create a new one with a timestamp
                import time
                timestamp = int(time.time())
                index_request = IndexCreateRequest(
                    name=f'Browser Screenshots {timestamp}',
                    description='Screenshots for browser automation analysis',
                    features=['embedding']
                )
                index_response = self._client.indexes.create(index_request)
                self._index_id = index_response.id
                logger.info(f"Created timestamped index: {self._index_id}")
            except Exception as e2:
                logger.error(f"Failed to setup index: {e2}")
                raise
    
    def analyze_screenshot(self, screenshot_bytes: bytes, query: str) -> AspectAnalyzeResult:
        """Analyze screenshot to find click points.
        
        Args:
            screenshot_bytes: Screenshot image data
            query: Text query describing what to find
            
        Returns:
            AspectAnalyzeResult with found points
        """
        if self.mock_mode:
            return self._mock_analyze(query)
        else:
            return self._real_analyze(screenshot_bytes, query)
    
    def _mock_analyze(self, query: str) -> AspectAnalyzeResult:
        """Mock version that asks user for coordinates.
        
        Args:
            query: Text query (displayed to user for context)
            
        Returns:
            AspectAnalyzeResult with user-provided coordinates
        """
        logger.info("Mock mode: requesting coordinates from user")
        
        print(f"\n[MOCK MODE] Query: '{query}'")
        print("Please provide X and Y coordinates where you want to click:")
        
        try:
            x_input = input("X coordinate: ").strip()
            y_input = input("Y coordinate: ").strip()
            
            x = int(x_input)
            y = int(y_input)
            
            if x < 0 or y < 0:
                raise ValueError("Coordinates must be non-negative")
            
            point = AspectPoint(x, y)
            result = AspectAnalyzeResult([point])
            
            logger.info(f"Mock mode: user provided coordinates ({x}, {y})")
            return result
            
        except (ValueError, EOFError) as e:
            logger.error(f"Invalid coordinates provided: {e}")
            # Return empty result for invalid input
            return AspectAnalyzeResult([])
    
    def _real_analyze(self, screenshot_bytes: bytes, query: str) -> AspectAnalyzeResult:
        """Real Aspect SDK analysis using the proper workflow.
        
        Args:
            screenshot_bytes: Screenshot image data
            query: Text query describing what to find
            
        Returns:
            AspectAnalyzeResult with API-provided points
        """
        if not self._client or not self._index_id:
            raise RuntimeError("Aspect client not initialized")
        
        try:
            from aspect_sdk import AssetCreateRequest, AnalyzePointRequest, WaitForDoneOptions
            
            logger.info(f"Analyzing screenshot with query: '{query}'")
            
            # Step 1: Upload screenshot as an asset
            timestamp = int(time.time())
            asset_name = f"screenshot_{timestamp}.png"
            
            # Create asset request with screenshot bytes
            asset_request = AssetCreateRequest(
                index_id=self._index_id,
                name=asset_name,
                asset_file=io.BytesIO(screenshot_bytes),
                save_original=True,
                features=['embedding']  # Enable features needed for analysis
            )
            
            logger.info("Uploading screenshot as asset...")
            asset_response = self._client.assets.create(asset_request)
            asset_id = asset_response.asset_id
            task_id = asset_response.task_id
            
            logger.info(f"Asset created: {asset_id}, task: {task_id}")
            
            # Step 2: Wait for asset processing to complete
            logger.info("Waiting for asset processing...")
            task = self._client.tasks.wait_for_done(task_id, WaitForDoneOptions(
                interval=2000,  # Check every 2 seconds
                timeout=30000   # 30 second timeout
            ))
            
            if hasattr(task, 'features') and hasattr(task.features, 'embedding'):
                if task.features.embedding.state == "failed":
                    logger.error("Asset processing failed")
                    return AspectAnalyzeResult([])
            
            # Step 3: Analyze the asset with the query
            analyze_request = AnalyzePointRequest(
                asset_id=asset_id,
                query=query
            )
            
            logger.info("Running point analysis...")
            result = self._client.analyze.point(analyze_request)
            
            # Step 4: Parse the response
            points = []
            if hasattr(result, 'points') and result.points:
                for point_coord in result.points:
                    # point_coord should be AnalyzePointCoordinate
                    if hasattr(point_coord, 'x') and hasattr(point_coord, 'y'):
                        points.append(AspectPoint(int(point_coord.x), int(point_coord.y)))
            
            logger.info(f"Aspect API returned {len(points)} points")
            return AspectAnalyzeResult(points)
            
        except Exception as e:
            logger.error(f"Aspect API analysis failed: {e}")
            # Return empty result on failure
            return AspectAnalyzeResult([])


def create_aspect_client() -> AspectClient:
    """Create and configure Aspect client from environment variables.
    
    Returns:
        Configured AspectClient instance
    """
    api_key = os.getenv("ASPECT_API_KEY")
    mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
    
    if mock_mode:
        logger.info("Using mock mode for Aspect SDK")
        return AspectClient(mock_mode=True)
    else:
        if not api_key:
            logger.warning("ASPECT_API_KEY not found, falling back to mock mode")
            return AspectClient(mock_mode=True)
        
        logger.info("Using real Aspect SDK")
        return AspectClient(api_key=api_key, mock_mode=False)