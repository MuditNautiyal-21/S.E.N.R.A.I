"""
Version information for SUDNAXI Trading Platform
"""

__version__ = "1.0.0"
__author__ = "Trading Systems Developer"
__description__ = "Advanced Stock Trading Intelligence Platform"
__license__ = "MIT"

# Version history
VERSION_HISTORY = {
    "1.0.0": {
        "date": "2024-12-15",
        "changes": [
            "Initial release with core trading features",
            "Real-time market data integration",
            "Advanced technical analysis tools",
            "Machine learning backtesting engine",
            "News sentiment analysis",
            "Portfolio simulation capabilities"
        ]
    }
}

def get_version_info():
    """Get formatted version information"""
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "license": __license__
    }