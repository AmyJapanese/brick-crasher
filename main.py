import pygame
import sys
import random

# 初期設定
pygame.init()
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Breaker")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# 色の定義
WHITE   = (255, 255, 255)
BLACK   = (0, 0, 0)
GRAY    = (200, 200, 200)
GREEN   = (0, 255, 0)
RED     = (255, 0, 0)
BLUE    = (0, 0, 255)
YELLOW  = (255, 255, 0)

# --- クラス定義 ---

class Paddle:
    def __init__(self, x, y, width, height, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed

    def move(self, direction):
        self.rect.x += direction * self.speed
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.move(-1)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.move(1)

    def draw(self, surface):
        pygame.draw.rect(surface, GREEN, self.rect)

class Ball:
    def __init__(self, x, y, radius, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.dx = 0
        self.dy = 0
        self.started = False

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.started = False

    def start(self):
        # 斜め45°、左右の方向はランダムに
        direction = random.choice([-1, 1])
        self.dx = self.speed * direction
        self.dy = -self.speed
        self.started = True

    def update(self):
        self.x += self.dx
        self.y += self.dy
        # 左右の壁で反転
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.dx = -self.dx
        if self.x + self.radius >= WIDTH:
            self.x = WIDTH - self.radius
            self.dx = -self.dx
        # 上側の壁で反転
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.dy = -self.dy

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)

class Block:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)  # 枠線

class Button:
    def __init__(self, rect, text, font, bg_color, text_color):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        surface.blit(self.text_surface, self.text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# --- メイン関数 ---
def main():
    state = "DIFFICULTY"  # 初期状態は難易度選択
    difficulty = 1  # 仮の初期値

    # 変数（ゲームオブジェクト）は後で DIFFICULTY 選択後に初期化するのでここでは宣言だけ
    paddle = None
    ball = None
    blocks = []
    score = 0
    lives = 3
    combo = 0  # コンボカウントの初期化

    # ボタン（ポーズ・ゲームオーバー用）の変数
    pause_continue = None
    pause_exit = None
    gameover_restart = None
    gameover_quit = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if state == "DIFFICULTY":
                # 難易度選択画面：キー "1", "2", "3" で選択
                if event.type == pygame.KEYDOWN:
                    if event.unicode in ['1', '2', '3']:
                        difficulty = int(event.unicode)
                        # 難易度に応じた速度設定
                        if difficulty == 1:
                            paddle_speed = 7
                            ball_speed = 5
                        elif difficulty == 2:
                            paddle_speed = 10
                            ball_speed = 7
                        elif difficulty == 3:
                            paddle_speed = 13
                            ball_speed = 9

                        # パドルの初期化（横100×縦20、下部中央に配置）
                        paddle = Paddle(WIDTH // 2 - 50, HEIGHT - 40, 100, 20, paddle_speed)
                        # ボールはパドル上に配置（半径 10）
                        ball = Ball(paddle.rect.centerx, paddle.rect.top - 10, 10, ball_speed)

                        # ブロック配置（縦3×横5）
                        blocks.clear()
                        margin_left = 50
                        margin_top = 50
                        gap = 5
                        block_rows = 3
                        block_cols = 5
                        block_width = (WIDTH - 2 * margin_left - (block_cols - 1) * gap) // block_cols
                        block_height = 30
                        colors = [BLUE, GREEN, YELLOW]
                        for row in range(block_rows):
                            for col in range(block_cols):
                                x = margin_left + col * (block_width + gap)
                                y = margin_top + row * (block_height + gap)
                                block = Block(x, y, block_width, block_height, colors[row % len(colors)])
                                blocks.append(block)

                        score = 0
                        lives = 3
                        # 次は「待機状態」（ボール発進前）
                        state = "WAITING"

            elif state == "WAITING":
                # 発進待ち状態：Wキーまたは上矢印キーでスタート
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        ball.start()
                        state = "PLAYING"

            elif state == "PLAYING":
                # ESC キーで一時停止
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = "PAUSED"
                        pause_continue = Button((WIDTH // 2 - 75, HEIGHT // 2 - 30, 150, 50),
                                                  "Continue", font, GRAY, BLACK)
                        pause_exit = Button((WIDTH // 2 - 75, HEIGHT // 2 + 40, 150, 50),
                                              "Exit", font, GRAY, BLACK)

            elif state == "PAUSED":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if pause_continue.is_clicked(pos):
                        state = "PLAYING"
                    elif pause_exit.is_clicked(pos):
                        pygame.quit()
                        sys.exit()

            elif state == "GAME_OVER":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if gameover_restart.is_clicked(pos):
                        state = "DIFFICULTY"  # 難易度選択から再スタート
                    elif gameover_quit.is_clicked(pos):
                        pygame.quit()
                        sys.exit()

        # ゲーム更新（PLAYING 状態のみ）
        if state == "PLAYING":
            keys = pygame.key.get_pressed()
            paddle.update(keys)

            if ball.started:
                ball.update()

            # パドルとの衝突判定（ボールが下向きの場合のみ処理）
            if ball.get_rect().colliderect(paddle.rect) and ball.dy > 0:
                ball.y = paddle.rect.top - ball.radius
                ball.dy = -ball.dy
                combo = 0  # パドルに当たったらコンボリセット

            # ブロックとの衝突判定（同一フレームに複数衝突すればコンボ加算）
            ball_rect = ball.get_rect()
            hit_blocks = [block for block in blocks if ball_rect.colliderect(block.rect)]
            if hit_blocks:
                for block in hit_blocks:
                    blocks.remove(block)
                combo += len(hit_blocks)  # コンボ数を増加
                for i in range(len(hit_blocks)):
                    score += 100 + (combo - 1) * 50  # コンボに応じた得点計算
                ball.dy = -ball.dy  # 反転
            else:
                combo = 0  # ヒットしなかった場合コンボリセット

            # 下端（画面外）に到達したとき：残基減少
            if ball.y - ball.radius > HEIGHT:
                lives -= 1
                combo = 0  # コンボリセット
                if lives > 0:
                    # パドル上にボールを再配置（発進待ち状態に戻す）
                    ball.reset(paddle.rect.centerx, paddle.rect.top - ball.radius)
                    state = "WAITING"  # 発進待ち状態に戻す
                else:
                    state = "GAME_OVER"
                    gameover_restart = Button((WIDTH // 2 - 75, HEIGHT // 2 + 20, 150, 50),
                                              "Restart", font, GRAY, BLACK)
                    gameover_quit = Button((WIDTH // 2 - 75, HEIGHT // 2 + 90, 150, 50),
                                           "Quit", font, GRAY, BLACK)

            # すべてのブロックを消したらゲームクリアで終了
            if not blocks:
                state = "GAME_OVER"
                gameover_restart = Button((WIDTH // 2 - 75, HEIGHT // 2 + 20, 150, 50),
                                          "Restart", font, GRAY, BLACK)
                gameover_quit = Button((WIDTH // 2 - 75, HEIGHT // 2 + 90, 150, 50),
                                       "Quit", font, GRAY, BLACK)

        # 描画処理
        screen.fill(BLACK)

        if state in ["WAITING", "PLAYING"]:
            # ブロック描画
            for block in blocks:
                block.draw(screen)
            # パドル・ボール描画
            paddle.draw(screen)
            ball.draw(screen)
            # スコアボード（上中央）
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, 20)))
            # 残基表示（右上に白丸で描画）
            for i in range(lives):
                pygame.draw.circle(screen, WHITE, (WIDTH - 20 - i * 30, 30), 10)
            # 発進待ち時は開始メッセージ表示
            if state == "WAITING":
                start_text = font.render("Press W or Up arrow to start", True, WHITE)
                screen.blit(start_text, start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        elif state == "DIFFICULTY":
            diff_text = font.render("Select Difficulty: 1: Easy, 2: Medium, 3: Hard", True, WHITE)
            screen.blit(diff_text, diff_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        elif state == "PAUSED":
            paused_text = font.render("Game Paused", True, WHITE)
            screen.blit(paused_text, paused_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))
            pause_continue.draw(screen)
            pause_exit.draw(screen)
        elif state == "GAME_OVER":
            over_text = font.render(f"Game Over! Score: {score}", True, WHITE)
            screen.blit(over_text, over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))
            gameover_restart.draw(screen)
            gameover_quit.draw(screen)

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
    pygame.quit()
    sys.exit()