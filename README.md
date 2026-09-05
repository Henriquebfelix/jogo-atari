# Jogo Atari 2D — Asteroid Destroyer 🚀

Jogo 2D no estilo Atari clássico desenvolvido em **Python + Pygame**.

## 🎮 Como Jogar

| Tecla | Ação |
|---|---|
| `←` / `A` | Mover nave para a esquerda |
| `→` / `D` | Mover nave para a direita |
| `ESPAÇO` | Atirar projétil |

- **Destrua** os asteroides antes que eles cheguem ao fundo da tela.
- Se um asteroide **colidir com a nave** ou **passar pela tela**, é **Game Over**.
- Cada asteroide destruído vale **+10 pontos**.
- A dificuldade aumenta progressivamente com a pontuação.

## ▶️ Como Executar

```bash
# Instalar dependência
pip install pygame

# Rodar o jogo
python3 game.py
```

## 🛠️ Tecnologias

- Python 3
- Pygame 2.x
- Sem assets externos — tudo desenhado via primitivas gráficas

## 📁 Estrutura

```
jogo-atari/
├── game.py          # Código principal do jogo Atari 2D (Pygame)
├── requirements.txt # Dependências do jogo
└── portfolio/       # Portfólio Pessoal responsivo (HTML5, CSS3, JS Vanilla, Bootstrap 5)
    ├── index.html
    ├── style.css
    └── app.js
```

