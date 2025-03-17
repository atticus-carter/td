import random
from enemy import Enemy
from config import *
from ui import WaveInfoDisplay

class WaveDefinition:
    def __init__(self, wave_num, duration=30, buildup_time=10):
        self.wave_num = wave_num
        self.duration = duration
        self.buildup_time = buildup_time
        self.enemy_groups = []
        self.pattern_type = None
        
    def add_enemy_group(self, enemy_type, count, delay_between=1.0, start_delay=0):
        """Add a group of enemies to spawn in this wave"""
        self.enemy_groups.append({
            'enemy_type': enemy_type,
            'count': count,
            'delay': delay_between,
            'start_delay': start_delay,
            'spawned': 0,
            'timer': start_delay
        })
        return self

class WaveManager:
    def __init__(self, level_number):
        self.level_number = level_number
        self.current_wave = 0
        self.wave_timer = 0
        self.build_phase = True
        self.waves = []
        self.setup_waves()
        
        # Initialize WaveInfoDisplay component
        self.wave_info_display = WaveInfoDisplay(SIDEBAR_WIDTH + 10, 10)
        
    def setup_waves(self):
        """Set up wave definitions based on level number"""
        # Early game (levels 1-5)
        if self.level_number <= 5:
            self._setup_early_game_waves()
        # Mid game (levels 6-10)
        elif self.level_number <= 10:
            self._setup_mid_game_waves()
        # Late game (levels 11+)
        else:
            self._setup_late_game_waves()
            
    def _setup_early_game_waves(self):
        """Set up early game waves focusing on basic enemies and simple patterns"""
        num_waves = 5
        patterns = WAVE_PATTERNS['early_game']
        
        for wave in range(num_waves):
            wave_num = wave + 1
            duration = 35 + wave * 5
            buildup = max(12, 15 - wave)
            
            wave_def = WaveDefinition(wave_num, duration, buildup)
            
            # Mix of basic patterns
            if wave == 0:
                # Tutorial wave - simple scouts
                wave_def.add_enemy_group('ScoutDrone', 3, 2.0, 3)
            elif wave == 1:
                # Resource raid pattern
                self._add_pattern(wave_def, patterns['resource_raid'], delay=1.5)
            elif wave == 2:
                # Mixed wave with scouts and exosuits
                wave_def.add_enemy_group('ScoutDrone', 4, 1.5, 2)
                wave_def.add_enemy_group('ExosuitDiver', 2, 3.0, 8)
            elif wave == 3:
                # Drilling team pattern
                self._add_pattern(wave_def, patterns['drilling_team'], delay=2.0)
            elif wave == 4:
                # Final early game wave - all basic types
                self._add_pattern(wave_def, patterns['basic_rush'], delay=1.2)
                wave_def.add_enemy_group('DrillingMech', 1, 1.0, 15)
            
            self.waves.append(wave_def)
            
    def _setup_mid_game_waves(self):
        """Set up mid-game waves with advanced enemies and coordinated attacks"""
        num_waves = 5
        patterns = WAVE_PATTERNS['mid_game']
        
        for wave in range(num_waves):
            wave_num = wave + 1
            duration = 40 + wave * 5
            buildup = max(10, 12 - wave)
            
            wave_def = WaveDefinition(wave_num, duration, buildup)
            
            # More complex pattern combinations
            if wave == 0:
                # Tech squad intro
                self._add_pattern(wave_def, patterns['tech_squad'], delay=2.0)
            elif wave == 1:
                # Collection team with support
                self._add_pattern(wave_def, patterns['collection_team'], delay=1.8)
                wave_def.add_enemy_group('ROV', 2, 2.5, 12)
            elif wave == 2:
                # Heavy assault wave
                self._add_pattern(wave_def, patterns['heavy_assault'], delay=2.5)
            elif wave == 3:
                # Mixed tech and collection
                wave_def.add_enemy_group('MiningLaser', 2, 2.0, 2)
                wave_def.add_enemy_group('CollectorCrab', 2, 2.0, 8)
                wave_def.add_enemy_group('SonicDisruptor', 1, 1.0, 15)
            elif wave == 4:
                # All mid-game types finale
                wave_def.add_enemy_group('SeabedCrawler', 1, 1.0, 2)
                wave_def.add_enemy_group('PressureCrusher', 2, 3.0, 8)
                wave_def.add_enemy_group('VortexGenerator', 2, 2.0, 15)
                wave_def.add_enemy_group('MiningLaser', 2, 1.5, 20)
            
            self.waves.append(wave_def)
            
    def _setup_late_game_waves(self):
        """Set up late-game waves with elite enemies and boss encounters"""
        num_waves = 5
        patterns = WAVE_PATTERNS['late_game']
        
        for wave in range(num_waves):
            wave_num = wave + 1
            duration = 45 + wave * 5
            buildup = max(8, 10 - wave)
            
            wave_def = WaveDefinition(wave_num, duration, buildup)
            
            # Complex patterns with elite units
            if wave == 0:
                # Elite force intro
                self._add_pattern(wave_def, patterns['elite_force'], delay=2.5)
            elif wave == 1:
                # Swarm attack with support
                self._add_pattern(wave_def, patterns['swarm_attack'], delay=1.5)
                wave_def.add_enemy_group('VortexGenerator', 2, 3.0, 15)
            elif wave == 2:
                # Mixed elite wave
                wave_def.add_enemy_group('BionicSquid', 2, 3.0, 2)
                wave_def.add_enemy_group('PressureCrusher', 2, 2.5, 10)
                wave_def.add_enemy_group('NaniteSwarm', 3, 1.5, 18)
            elif wave == 3:
                # Heavy elite assault
                wave_def.add_enemy_group('SeabedCrawler', 2, 3.0, 2)
                wave_def.add_enemy_group('BionicSquid', 2, 2.5, 12)
                wave_def.add_enemy_group('SonicDisruptor', 3, 1.5, 20)
            elif wave == 4:
                # Final boss wave
                self._add_pattern(wave_def, patterns['boss_raid'], delay=3.0)
                wave_def.add_enemy_group('NaniteSwarm', 4, 1.0, 25)
            
            self.waves.append(wave_def)
            
    def _add_pattern(self, wave_def, enemy_types, delay=2.0):
        """Add a predefined pattern of enemies to a wave"""
        start_delay = 2.0
        for enemy_type in enemy_types:
            wave_def.add_enemy_group(enemy_type, 1, delay, start_delay)
            start_delay += delay
    
    def update(self, dt, enemies):
        """Update wave state and spawn enemies"""
        if self.current_wave >= len(self.waves):
            return False  # No more waves
            
        current_wave_def = self.waves[self.current_wave]
        
        if self.build_phase:
            self.wave_timer += dt
            if self.wave_timer >= current_wave_def.buildup_time:
                self.build_phase = False
                self.wave_timer = 0
            return True
            
        # Wave phase
        self.wave_timer += dt
        spawned_enemy = False
        
        # Update enemy groups
        for group in current_wave_def.enemy_groups:
            if group['spawned'] < group['count']:
                group['timer'] -= dt
                if group['timer'] <= 0:
                    # Spawn enemy with random vertical position
                    y = random.randint(0, GRID_ROWS - 1)
                    enemies.append(Enemy(y, group['enemy_type']))
                    group['spawned'] += 1
                    group['timer'] = group['delay']
                    spawned_enemy = True
        
        # Check if wave is complete
        if self.wave_timer >= current_wave_def.duration:
            all_spawned = True
            for group in current_wave_def.enemy_groups:
                if group['spawned'] < group['count']:
                    all_spawned = False
                    break
            
            if all_spawned:
                self.current_wave += 1
                self.build_phase = True
                self.wave_timer = 0
                
        return True
    
    def get_wave_status(self):
        """Get current wave status information"""
        if self.current_wave >= len(self.waves):
            return "All waves complete!"
            
        current_wave_def = self.waves[self.current_wave]
        if self.build_phase:
            time_left = current_wave_def.buildup_time - self.wave_timer
            return f"Wave {self.current_wave + 1} - Build Phase ({int(time_left)}s)"
        else:
            time_left = current_wave_def.duration - self.wave_timer
            return f"Wave {self.current_wave + 1} - Combat Phase ({int(time_left)}s)"
    
    def is_final_wave(self):
        """Check if current wave is the final wave"""
        return self.current_wave == len(self.waves) - 1
        
    def draw_wave_info(self, surface):
        """Draw wave information using the shared WaveInfoDisplay component"""
        wave_status = self.get_wave_status()
        self.wave_info_display.draw(surface, wave_status)