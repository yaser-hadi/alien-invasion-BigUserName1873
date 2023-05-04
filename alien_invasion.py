import sys
import pygame
import random
from time import sleep
from setting import Settings
from ship import Ship
from bullet import Bullet, Alien_Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard



class AlienInvasion:
    

    def __init__(self):

        pygame.init()
        pygame.mixer.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.shoot_sfx = pygame.mixer.Sound('shot.mp3')
        self.scream_sfx = pygame.mixer.Sound('scream.mp3')
        self._create_fleet()
        self.stats = GameStats(self)
        self.play_button = Button(self, "Play")
        self.sb = Scoreboard(self)
        
        pygame.display.set_caption('Alien Invasion')




  
    def run_game(self):
        self._update_screen()

        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._update_screen()
                '''r = random.randint(0,100)
                if r == 0 :
                    self._fire_bullet()'''


    def _update_screen(self):
            self.screen.fill(self.settings.bg_color)
            self.ship.blitme()
            for bullet in self.bullets.sprites():
                bullet.draw_bullet()
            self.aliens.draw(self.screen)

            if not self.stats.game_active:
                self.play_button.draw_button()

            self.sb.show_score()

            pygame.display.flip()


    def _check_events(self):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    self._check_keydown_events(event)

                        
                elif event.type == pygame.KEYUP:
                    self._check_keyup_events(event)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self._check_play_button(mouse_pos)


    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        if event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        if event.key == pygame.K_q:
            sys.exit()
        if event.key == pygame.K_SPACE:
            self._fire_bullet()
    
    
    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        if event.key == pygame.K_LEFT:
            self.ship.moving_left = False




    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:

            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            self.shoot_sfx.play()


    def _update_bullets(self):
            self.bullets.update()
            for bullet in self.bullets.copy():
                if bullet.rect.bottom <= 0:
                    self.bullets.remove(bullet)
            
            self._check_bullets_alien_collision()


    def _ship_hit(self):
        if self.stats.ships_left > 0:

            self.stats.ships_left -= 1
            self.sb.prep_ships()
                
            self.aliens.empty()
            self.bullets.empty()
            
            self._create_fleet()
            self.ship.center_ship()
            
            sleep(0.5)

        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)




    def _check_bullets_alien_collision(self):
        collisions1 = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        collisions2 = pygame.sprite.groupcollide(self.aliens, self.bullets, True, True)

        if collisions1:
            self.stats.score += self.settings.alien_points
            self.sb.prep_score()
            self.scream_sfx.play()
            self.sb.check_high_score()

        if collisions2:
            self._ship_hit()

        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()




    def _create_alien(self, alien_number, row_number, can_shoot = False):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien_height + 2 * alien.rect.height * row_number
        alien.can_shoot = can_shoot
        self.aliens.add(alien)


    def _create_fleet(self):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        can_shoot = False
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3* alien_height) - ship_height)

        number_rows = available_space_y // (2 * alien_height)

        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                if row_number == number_rows -1:
                    can_shoot = True
                self._create_alien(alien_number, row_number, can_shoot)


    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break


    def _check_aliens_bottom(self):
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break


    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1


    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()

        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        self._check_aliens_bottom()


    def _alien_shoot(self):
            new_bullet = Alien_Bullet(self)
            self.alien_bullets.add(new_bullet)


    def _alien_update_bullets(self):
            self.alien_bullets.update()
            for bullet in self.bullets.copy():
                if bullet.rect.bottom <= 0:
                    self.bullets.remove(bullet)




    def _check_play_button(self, mouse_pos):
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self.stats.reset_stats()
            self.settings.initialize_dynamic_settings()
            self.sb.prep_level()
            self.sb.prep_score()
            self.sb.prep_ships()
            self.stats.game_active = True

            self.aliens.empty()
            self.bullets.empty()

            self._create_fleet()
            self.ship.center_ship()
            pygame.mouse.set_visible(False)





if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()