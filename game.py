"""
Jogo Atari 2D — Nave Espacial vs Asteroides
Desenvolvido com Python + Pygame (sem assets externos)

Controles:
  ← →    : Mover nave
  ESPAÇO : Atirar
"""

import pygame
import random
import math
import sys

# ─────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────
SCREEN_W, SCREEN_H = 800, 600
FPS = 60
TITLE = "Atari Space — Asteroid Destroyer"

# Cores
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
YELLOW     = (255, 230,  50)
ORANGE     = (255, 140,  0)
CYAN       = (0,   220, 255)
GRAY_DARK  = (60,  60,  70)
GRAY_MED   = (120, 115, 130)
GRAY_LIGHT = (190, 185, 200)
RED        = (220,  50,  50)
GREEN_NEON = (50,  255, 150)
PURPLE     = (140,  60, 220)

# Nave
SHIP_SPEED     = 8          # px por frame
BULLET_SPEED   = 12         # px por frame
BULLET_COOLDOWN = 300       # ms entre tiros

# Asteroides
ASTEROID_BASE_SPEED  = 2.0  # velocidade inicial
ASTEROID_MAX_SPEED   = 6.5  # velocidade máxima
SPEED_INCREMENT      = 0.0008  # aceleração por frame
SPAWN_INTERVAL_MS    = 1200    # ms entre spawns (inicial)
SPAWN_MIN_MS         = 500     # intervalo mínimo de spawn

# Pontuação
POINTS_PER_HIT = 10

# Estados do jogo
STATE_PLAYING   = "playing"
STATE_GAME_OVER = "gameover"


# ─────────────────────────────────────────────
#  ESTRELAS DE FUNDO
# ─────────────────────────────────────────────
class StarField:
    """Campo de estrelas estáticas para fundo espacial."""

    def __init__(self, num_stars: int = 120):
        self.stars = []
        for _ in range(num_stars):
            x = random.randint(0, SCREEN_W)
            y = random.randint(0, SCREEN_H)
            r = random.choice([1, 1, 1, 2])
            brightness = random.randint(120, 255)
            color = (brightness, brightness, brightness)
            self.stars.append((x, y, r, color))

    def draw(self, surface: pygame.Surface):
        for x, y, r, color in self.stars:
            pygame.draw.circle(surface, color, (x, y), r)


# ─────────────────────────────────────────────
#  NAVE DO JOGADOR
# ─────────────────────────────────────────────
class Nave(pygame.sprite.Sprite):
    """Nave controlada pelo jogador via setas ← →."""

    WIDTH  = 44
    HEIGHT = 48

    def __init__(self):
        super().__init__()
        self.image = self._build_surface()
        self.rect  = self.image.get_rect()
        self.rect.centerx = SCREEN_W // 2
        self.rect.bottom   = SCREEN_H - 20
        self.mask = pygame.mask.from_surface(self.image)

    # ------------------------------------------------------------------
    def _build_surface(self) -> pygame.Surface:
        """Desenha a nave como polígono + detalhes em superfície transparente."""
        surf = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        cx = self.WIDTH // 2

        # Corpo principal — triângulo
        body = [(cx, 2), (self.WIDTH - 4, self.HEIGHT - 10), (4, self.HEIGHT - 10)]
        pygame.draw.polygon(surf, CYAN, body)
        pygame.draw.polygon(surf, WHITE, body, 2)

        # Base da nave
        base = [(6, self.HEIGHT - 10), (self.WIDTH - 6, self.HEIGHT - 10),
                (self.WIDTH - 4, self.HEIGHT - 2), (4, self.HEIGHT - 2)]
        pygame.draw.polygon(surf, PURPLE, base)
        pygame.draw.polygon(surf, WHITE, base, 1)

        # Cockpit (detalhe central)
        pygame.draw.ellipse(surf, WHITE, (cx - 5, 14, 10, 12))
        pygame.draw.ellipse(surf, CYAN,  (cx - 3, 16,  6,  8))

        # Canhão central
        pygame.draw.rect(surf, YELLOW, (cx - 2, 0, 4, 10), border_radius=2)

        return surf

    # ------------------------------------------------------------------
    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= SHIP_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += SHIP_SPEED

        # Limitar às bordas
        self.rect.left  = max(0, self.rect.left)
        self.rect.right = min(SCREEN_W, self.rect.right)

    # ------------------------------------------------------------------
    def get_gun_pos(self):
        """Posição do canhão para spawnar o projétil."""
        return self.rect.centerx, self.rect.top


# ─────────────────────────────────────────────
#  PROJÉTIL
# ─────────────────────────────────────────────
class Projetil(pygame.sprite.Sprite):
    """Projétil disparado pela nave."""

    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pygame.Surface((4, 14), pygame.SRCALPHA)
        # Gradiente manual (amarelo → laranja)
        for row in range(14):
            t = row / 13
            r = int(255)
            g = int(230 - t * 100)
            b = int(50  - t * 50)
            pygame.draw.line(self.image, (r, g, max(b, 0)), (0, row), (3, row))
        self.rect = self.image.get_rect(centerx=x, bottom=y)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.y -= BULLET_SPEED
        if self.rect.bottom < 0:
            self.kill()


# ─────────────────────────────────────────────
#  ASTEROIDE
# ─────────────────────────────────────────────
class Asteroide(pygame.sprite.Sprite):
    """Asteroide que desce da parte superior da tela."""

    # Tamanhos possíveis (raio)
    SIZES = [18, 26, 36]
    COLORS = [
        [(80, 75, 90),  (110, 100, 120), (140, 130, 150)],   # cinza arroxeado
        [(90, 70, 55),  (120, 95,  70),  (150, 120,  90)],   # marrom
        [(60, 60, 75),  (90,  85, 100),  (115, 110, 130)],   # cinza azulado
    ]

    def __init__(self, speed: float):
        super().__init__()
        self.radius   = random.choice(self.SIZES)
        self.speed    = speed
        size          = self.radius * 2 + 4

        palette_idx   = random.randint(0, len(self.COLORS) - 1)
        self.palette  = self.COLORS[palette_idx]

        self.image    = self._build_surface(size)
        self.rect     = self.image.get_rect()
        self.rect.x   = random.randint(self.radius, SCREEN_W - self.radius)
        self.rect.y   = -size
        self.mask     = pygame.mask.from_surface(self.image)

        # Rotação
        self._angle   = 0
        self._rot_speed = random.uniform(-1.5, 1.5)
        self._base_img  = self.image.copy()

    # ------------------------------------------------------------------
    def _build_surface(self, size: int) -> pygame.Surface:
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx = cy = size // 2
        r  = self.radius

        # Gerar pontos irregulares do polígono
        num_pts = random.randint(8, 12)
        points  = []
        for i in range(num_pts):
            angle  = (2 * math.pi / num_pts) * i
            jitter = random.uniform(0.65, 1.0)
            px = cx + int(r * jitter * math.cos(angle))
            py = cy + int(r * jitter * math.sin(angle))
            points.append((px, py))

        # Preenchimento
        pygame.draw.polygon(surf, self.palette[0], points)
        # Borda
        pygame.draw.polygon(surf, self.palette[2], points, 2)
        # Crateras (círculos menores aleatórios)
        for _ in range(random.randint(1, 3)):
            cx2 = random.randint(cx - r // 2, cx + r // 2)
            cy2 = random.randint(cy - r // 2, cy + r // 2)
            cr  = random.randint(3, max(4, r // 4))
            pygame.draw.circle(surf, self.palette[1], (cx2, cy2), cr)
            pygame.draw.circle(surf, self.palette[0], (cx2, cy2), max(1, cr - 2))

        return surf

    # ------------------------------------------------------------------
    def update(self):
        self.rect.y += self.speed
        # Rotação suave
        self._angle = (self._angle + self._rot_speed) % 360
        rotated     = pygame.transform.rotate(self._base_img, self._angle)
        old_center  = self.rect.center
        self.image  = rotated
        self.rect   = self.image.get_rect(center=old_center)
        self.mask   = pygame.mask.from_surface(self.image)

    # ------------------------------------------------------------------
    def saiu_da_tela(self) -> bool:
        return self.rect.top > SCREEN_H


# ─────────────────────────────────────────────
#  EFEITO DE EXPLOSÃO (partículas simples)
# ─────────────────────────────────────────────
class Particula:
    """Partícula de explosão."""

    def __init__(self, x: int, y: int, color):
        self.x    = float(x)
        self.y    = float(y)
        angle     = random.uniform(0, 2 * math.pi)
        speed     = random.uniform(1.5, 5.0)
        self.vx   = math.cos(angle) * speed
        self.vy   = math.sin(angle) * speed
        self.life = random.randint(20, 45)
        self.max_life = self.life
        self.color    = color
        self.radius   = random.randint(2, 5)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.12   # gravidade leve
        self.life -= 1

    def draw(self, surface: pygame.Surface):
        alpha  = int(255 * (self.life / self.max_life))
        r, g, b = self.color
        color  = (min(r, 255), min(g, 255), min(b, 255))
        radius = max(1, int(self.radius * (self.life / self.max_life)))
        # Desenhar com transparência via Surface
        s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, alpha), (radius, radius), radius)
        surface.blit(s, (int(self.x) - radius, int(self.y) - radius))

    @property
    def vivo(self):
        return self.life > 0


# ─────────────────────────────────────────────
#  BOTÃO
# ─────────────────────────────────────────────
class Botao:
    """Botão clicável simples."""

    def __init__(self, texto: str, cx: int, cy: int, w: int = 240, h: int = 54):
        self.texto = texto
        self.rect  = pygame.Rect(0, 0, w, h)
        self.rect.center = (cx, cy)
        self.hovered = False
        self._font   = pygame.font.SysFont("Arial", 26, bold=True)

    def handle_event(self, event) -> bool:
        """Retorna True se o botão foi clicado."""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface: pygame.Surface):
        color_bg     = (50, 220, 130) if self.hovered else (30, 170, 100)
        color_border = (200, 255, 220)
        color_text   = BLACK if self.hovered else WHITE

        pygame.draw.rect(surface, color_bg,     self.rect, border_radius=12)
        pygame.draw.rect(surface, color_border, self.rect, 2, border_radius=12)

        label = self._font.render(self.texto, True, color_text)
        lrect = label.get_rect(center=self.rect.center)
        surface.blit(label, lrect)


# ─────────────────────────────────────────────
#  CLASSE PRINCIPAL DO JOGO
# ─────────────────────────────────────────────
class Game:
    """Gerencia o loop principal, estados e renderização."""

    def __init__(self):
        pygame.init()
        self.screen  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(TITLE)
        self.clock   = pygame.time.Clock()
        self.stars   = StarField()

        # Fontes
        self.font_score    = pygame.font.SysFont("Consolas", 24, bold=True)
        self.font_big      = pygame.font.SysFont("Arial",    56, bold=True)
        self.font_medium   = pygame.font.SysFont("Arial",    30)
        self.font_sub      = pygame.font.SysFont("Consolas", 20)

        self._reset()

    # ------------------------------------------------------------------
    def _reset(self):
        """Reinicia todas as variáveis para uma nova partida."""
        self.state  = STATE_PLAYING
        self.score  = 0
        self.frame  = 0
        self.asteroid_speed = ASTEROID_BASE_SPEED

        # Grupos de sprites
        self.all_sprites  = pygame.sprite.Group()
        self.bullets      = pygame.sprite.Group()
        self.asteroids    = pygame.sprite.Group()

        self.nave = Nave()
        self.all_sprites.add(self.nave)

        # Timers
        self.last_shot_time  = 0
        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_interval  = SPAWN_INTERVAL_MS

        # Partículas
        self.particulas: list[Particula] = []

        # Botão Game Over
        self.btn_restart = Botao("▶  JOGAR NOVAMENTE", SCREEN_W // 2, SCREEN_H // 2 + 90)

    # ------------------------------------------------------------------
    def _spawn_asteroid(self):
        speed  = min(self.asteroid_speed, ASTEROID_MAX_SPEED)
        ast    = Asteroide(speed)
        self.asteroids.add(ast)
        self.all_sprites.add(ast)

    # ------------------------------------------------------------------
    def _shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= BULLET_COOLDOWN:
            gx, gy = self.nave.get_gun_pos()
            bullet  = Projetil(gx, gy)
            self.bullets.add(bullet)
            self.all_sprites.add(bullet)
            self.last_shot_time = now

    # ------------------------------------------------------------------
    def _explode(self, x: int, y: int, colors: list, count: int = 25):
        for color in [colors] if not isinstance(colors, list) else colors:
            for _ in range(count // len(colors) if isinstance(colors, list) else count):
                self.particulas.append(Particula(x, y, color))

    # ------------------------------------------------------------------
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self._shoot()

            elif self.state == STATE_GAME_OVER:
                if self.btn_restart.handle_event(event):
                    self._reset()

    # ------------------------------------------------------------------
    def _update_playing(self, keys):
        self.frame += 1

        # Aumentar dificuldade gradualmente
        self.asteroid_speed = min(
            ASTEROID_BASE_SPEED + self.frame * SPEED_INCREMENT,
            ASTEROID_MAX_SPEED
        )
        # Reduzir intervalo de spawn com o tempo (mínimo SPAWN_MIN_MS)
        self.spawn_interval = max(
            SPAWN_MIN_MS,
            SPAWN_INTERVAL_MS - self.score * 2
        )

        # Spawn de asteroides
        now = pygame.time.get_ticks()
        if now - self.last_spawn_time >= self.spawn_interval:
            self._spawn_asteroid()
            self.last_spawn_time = now

        # Atualizar nave
        self.nave.update(keys)

        # Atualizar projéteis e asteroides
        self.bullets.update()
        self.asteroids.update()

        # Atualizar partículas
        for p in self.particulas:
            p.update()
        self.particulas = [p for p in self.particulas if p.vivo]

        # ── Colisão: projétil × asteroide ──────────────────────────────
        hits = pygame.sprite.groupcollide(
            self.bullets, self.asteroids, True, True,
            pygame.sprite.collide_mask
        )
        for bullet, asts in hits.items():
            for ast in asts:
                cx, cy = ast.rect.center
                self._explode(cx, cy, [ORANGE, YELLOW, (200, 200, 200)], 30)
                self.score += POINTS_PER_HIT

        # ── Asteroide saiu da tela ──────────────────────────────────────
        for ast in list(self.asteroids):
            if ast.saiu_da_tela():
                self.state = STATE_GAME_OVER
                return

        # ── Colisão: nave × asteroide ───────────────────────────────────
        collididos = pygame.sprite.spritecollide(
            self.nave, self.asteroids, False,
            pygame.sprite.collide_mask
        )
        if collididos:
            cx, cy = self.nave.rect.center
            self._explode(cx, cy, [CYAN, WHITE, PURPLE, ORANGE], 50)
            self.state = STATE_GAME_OVER

    # ------------------------------------------------------------------
    def _draw_hud(self):
        # Fundo semi-transparente para o HUD
        hud_surf = pygame.Surface((180, 36), pygame.SRCALPHA)
        hud_surf.fill((0, 0, 0, 130))
        self.screen.blit(hud_surf, (8, 8))

        score_txt = self.font_score.render(f"  SCORE: {self.score:05d}", True, GREEN_NEON)
        self.screen.blit(score_txt, (12, 12))

    # ------------------------------------------------------------------
    def _draw_game_over(self):
        # Overlay escuro
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        self.screen.blit(overlay, (0, 0))

        # Título "GAME OVER"
        go_text = self.font_big.render("GAME OVER", True, RED)
        go_rect = go_text.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 100))
        # Sombra
        shadow  = self.font_big.render("GAME OVER", True, (80, 0, 0))
        self.screen.blit(shadow, (go_rect.x + 3, go_rect.y + 3))
        self.screen.blit(go_text, go_rect)

        # Pontuação final
        sc_text = self.font_medium.render(f"Pontuação Final:  {self.score:05d}", True, WHITE)
        sc_rect = sc_text.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 20))
        self.screen.blit(sc_text, sc_rect)

        # Dica de controle
        hint = self.font_sub.render("← → para mover  |  ESPAÇO para atirar", True, GRAY_LIGHT)
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 145)))

        # Botão
        self.btn_restart.draw(self.screen)

    # ------------------------------------------------------------------
    def _draw(self):
        # Fundo
        self.screen.fill(BLACK)
        self.stars.draw(self.screen)

        # Sprites
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, sprite.rect)

        # Partículas
        for p in self.particulas:
            p.draw(self.screen)

        if self.state == STATE_PLAYING:
            self._draw_hud()
        elif self.state == STATE_GAME_OVER:
            self._draw_hud()
            self._draw_game_over()

        pygame.display.flip()

    # ------------------------------------------------------------------
    def run(self):
        """Loop principal do jogo."""
        while True:
            self._handle_events()

            if self.state == STATE_PLAYING:
                keys = pygame.key.get_pressed()
                self._update_playing(keys)

                # Permitir atirar pressionando espaço continuamente
                if keys[pygame.K_SPACE]:
                    self._shoot()

            elif self.state == STATE_GAME_OVER:
                # Atualizar partículas mesmo na tela de Game Over
                for p in self.particulas:
                    p.update()
                self.particulas = [p for p in self.particulas if p.vivo]

            self._draw()
            self.clock.tick(FPS)


# ─────────────────────────────────────────────
#  PONTO DE ENTRADA
# ─────────────────────────────────────────────
if __name__ == "__main__":
    Game().run()
