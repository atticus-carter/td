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
        # Tutorial level (1)
        if self.level_number == 1:
            self._setup_tutorial_waves()
        # Early levels (2-5)
        elif self.level_number <= 5:
            self._setup_early_game_waves()
        # Mid levels (6-10)
        elif self.level_number <= 10:
            self._setup_mid_game_waves()
        # Late levels (11-15)
        elif self.level_number <= 15:
            self._setup_late_game_waves()
        # End game levels (16-20)
        else:
            self._setup_end_game_waves()
            
    def _setup_tutorial_waves(self):
        """Set up tutorial waves with very gradual difficulty"""
        # Wave 1: Few scattered scouts
        w1 = WaveDefinition(1, duration=40, buildup_time=20)
        w1.add_enemy_group('ScoutDrone', 3, delay_between=3, start_delay=5)
        self.waves.append(w1)
        
        # Wave 2: More scouts, introduced slowly
        w2 = WaveDefinition(2, duration=40, buildup_time=15)
        w2.add_enemy_group('ScoutDrone', 5, delay_between=2, start_delay=3)
        self.waves.append(w2)
        
        # Wave 3: Scouts and first Exosuit
        w3 = WaveDefinition(3, duration=40, buildup_time=15)
        w3.add_enemy_group('ScoutDrone', 4, delay_between=2, start_delay=2)
        w3.add_enemy_group('ExosuitDiver', 1, delay_between=1, start_delay=15)
        self.waves.append(w3)
        
        # Wave 4: Mixed wave
        w4 = WaveDefinition(4, duration=45, buildup_time=15)
        w4.add_enemy_group('ScoutDrone', 6, delay_between=1.5, start_delay=2)
        w4.add_enemy_group('ExosuitDiver', 2, delay_between=8, start_delay=10)
        self.waves.append(w4)
        
        # Wave 5: Final tutorial wave with all basic enemies
        w5 = WaveDefinition(5, duration=50, buildup_time=20)
        w5.add_enemy_group('ScoutDrone', 8, delay_between=1.5, start_delay=2)
        w5.add_enemy_group('ExosuitDiver', 3, delay_between=6, start_delay=8)
        w5.add_enemy_group('DrillingMech', 1, delay_between=1, start_delay=25)
        self.waves.append(w5)
    
    def _setup_early_game_waves(self):
        """Set up waves for early game levels (2-5)"""
        num_waves = 5
        base_buildup = 15  # Base buildup time
        
        for wave in range(num_waves):
            wave_num = wave + 1
            duration = 35 + wave * 5
            buildup = max(10, base_buildup - wave)
            
            wave_def = WaveDefinition(wave_num, duration, buildup)
            
            # Add scout drones
            scout_count = 4 + wave * 2
            wave_def.add_enemy_group('ScoutDrone', scout_count, 
                                   delay_between=1.5 - wave * 0.2,
                                   start_delay=2)
            
            # Add exosuit divers from wave 2
            if wave >= 1:
                exosuit_count = 1 + (wave - 1)
                wave_def.add_enemy_group('ExosuitDiver', exosuit_count,
                                       delay_between=4,
                                       start_delay=10)
            
            # Add drilling mech in final wave
            if wave == num_waves - 1:
                wave_def.add_enemy_group('DrillingMech', 2,
                                       delay_between=8,
                                       start_delay=20)
            
            self.waves.append(wave_def)
    
    def _setup_mid_game_waves(self):
        """Set up waves for mid game levels (6-10)"""
        num_waves = 5
        
        for wave in range(num_waves):
            wave_num = wave + 1
            duration = 40 + wave * 5
            buildup = max(8, 12 - wave)
            
            wave_def = WaveDefinition(wave_num, duration, buildup)
            
            # Multiple enemy groups per wave
            scout_count = 6 + wave * 2
            wave_def.add_enemy_group('ScoutDrone', scout_count,
                                   delay_between=1.2 - wave * 0.1,
                                   start_delay=2)
            
            exosuit_count = 2 + wave
            wave_def.add_enemy_group('ExosuitDiver', exosuit_count,
                                   delay_between=3,
                                   start_delay=8)
            
            drilling_count = 1 + wave // 2
            wave_def.add_enemy_group('DrillingMech', drilling_count,
                                   delay_between=6,
                                   start_delay=15)
            
            # Boss in final wave
            if wave == num_waves - 1:
                wave_def.add_enemy_group('CorporateSubmarine', 1,
                                       delay_between=1,
                                       start_delay=25)
            
            self.waves.append(wave_def)
    
    def _setup_late_game_waves(self):
        """Set up waves for late game levels (11-15)"""
        num_waves = 5
        
        for wave in range(num_waves):
            wave_num = wave + 1
            wave_def = WaveDefinition(wave_num, 45 + wave * 5, max(6, 10 - wave))
            
            # Multiple coordinated attack groups
            # Fast scout group
            wave_def.add_enemy_group('ScoutDrone', 8 + wave * 2,
                                   delay_between=0.8,
                                   start_delay=2)
            
            # Exosuit squad
            wave_def.add_enemy_group('ExosuitDiver', 3 + wave,
                                   delay_between=2,
                                   start_delay=10)
            
            # Heavy assault group
            wave_def.add_enemy_group('DrillingMech', 2 + wave // 2,
                                   delay_between=4,
                                   start_delay=15)
            
            # Mini-boss every other wave
            if wave % 2 == 1:
                wave_def.add_enemy_group('CorporateSubmarine', 1,
                                       start_delay=20)
            
            self.waves.append(wave_def)
    
    def _setup_end_game_waves(self):
        """Set up waves for end game levels (16-20)"""
        num_waves = 5
        
        for wave in range(num_waves):
            wave_num = wave + 1
            wave_def = WaveDefinition(wave_num, 50 + wave * 5, max(5, 8 - wave))
            
            # Continuous scout pressure
            wave_def.add_enemy_group('ScoutDrone', 10 + wave * 3,
                                   delay_between=0.6,
                                   start_delay=2)
            
            # Strong exosuit presence
            wave_def.add_enemy_group('ExosuitDiver', 4 + wave,
                                   delay_between=1.5,
                                   start_delay=8)
            
            # Heavy assault
            wave_def.add_enemy_group('DrillingMech', 2 + wave,
                                   delay_between=3,
                                   start_delay=12)
            
            # Multiple bosses in later waves
            if wave >= 3:
                wave_def.add_enemy_group('CorporateSubmarine',
                                       1 + (wave - 3),
                                       delay_between=15,
                                       start_delay=20)
            
            self.waves.append(wave_def)
    
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
                    # Spawn enemy
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