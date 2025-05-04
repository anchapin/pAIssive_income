"""
"""
Event handlers for the pAIssive Income UI.
Event handlers for the pAIssive Income UI.


This module provides event handlers for the UI.
This module provides event handlers for the UI.
"""
"""




import logging
import logging
from typing import Any, Dict
from typing import Any, Dict


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




def handle_niche_selected(ui, event_data: Dict[str, Any]) -> None:
    def handle_niche_selected(ui, event_data: Dict[str, Any]) -> None:
    """
    """
    Handle a niche selection event.
    Handle a niche selection event.


    Args:
    Args:
    ui: UI instance
    ui: UI instance
    event_data: Event data
    event_data: Event data
    """
    """
    logger.info(f"Handling niche selection event: {event_data}")
    logger.info(f"Handling niche selection event: {event_data}")


    # Get the niche ID
    # Get the niche ID
    niche_id = event_data.get("niche_id")
    niche_id = event_data.get("niche_id")


    if niche_id is None:
    if niche_id is None:
    logger.warning("No niche ID in event data")
    logger.warning("No niche ID in event data")
    return # Find the niche
    return # Find the niche
    niche = None
    niche = None
    for n in ui.current_niches:
    for n in ui.current_niches:
    if n.get("id") == niche_id:
    if n.get("id") == niche_id:
    niche = n
    niche = n
    break
    break


    if niche is None:
    if niche is None:
    logger.warning(f"Niche with ID {niche_id} not found")
    logger.warning(f"Niche with ID {niche_id} not found")
    return # Set the selected niche
    return # Set the selected niche
    ui.selected_niche = niche
    ui.selected_niche = niche
    logger.info(f"Selected niche: {niche.get('name')}")
    logger.info(f"Selected niche: {niche.get('name')}")