import pygame

# Define which towers can auto-collect which resources
AUTO_COLLECT_RELATIONSHIPS = {
    'RiftiaTubeWorm': 'sulfides',     # Hydrothermal
    'Rockfish': 'methane',            # Coldseep
    'Hagfish': 'salt',                # Brine Pool
    'Muusoctopus': 'lipids',          # Whalefall
    'Nautilus': 'all'                 # Special case - can collect any resource
}

def check_auto_collect(orb, tower):
    """
    Check if a resource orb should be auto-collected by a tower
    Returns True if the orb should be collected, False otherwise
    """
    if not tower.name in AUTO_COLLECT_RELATIONSHIPS:
        return False
        
    collect_type = AUTO_COLLECT_RELATIONSHIPS[tower.name]
    if collect_type == 'all' or collect_type == orb.resource_type:
        # Calculate tower bounds
        tower_rect = pygame.Rect(
            tower.x * tower.CELL_WIDTH + tower.SIDEBAR_WIDTH,
            tower.y * tower.CELL_HEIGHT,
            tower.CELL_WIDTH,
            tower.CELL_HEIGHT
        )
        
        # Check if orb is within the tower's bounds
        orb_pos = pygame.Vector2(orb.x, orb.y)
        return tower_rect.collidepoint(orb_pos)