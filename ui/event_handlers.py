"""
Event handlers for the pAIssive Income UI.

This module provides event handlers for the UI.
"""

import logging
from typing import Any, Dict

# Set up logging
logger = logging.getLogger(__name__)

def handle_niche_selected(ui, event_data: Dict[str, Any]) -> None:
    """
    Handle a niche selection event.
    
    Args:
        ui: UI instance
        event_data: Event data
    """
    logger.info(f"Handling niche selection event: {event_data}")
    
    # Get the niche ID
    niche_id = event_data.get('niche_id')
    
    if niche_id is None:
        logger.warning("No niche ID in event data")
        return
    
    # Find the niche
    niche = None
    for n in ui.current_niches:
        if n.get('id') == niche_id:
            niche = n
            break
    
    if niche is None:
        logger.warning(f"Niche with ID {niche_id} not found")
        return
    
    # Set the selected niche
    ui.selected_niche = niche
    logger.info(f"Selected niche: {niche.get('name')}")
